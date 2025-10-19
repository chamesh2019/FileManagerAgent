from time import sleep
from httpx import get
from langchain_chroma import Chroma
from dotenv import load_dotenv
from glob import glob
import os
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector_store = Chroma(collection_name="file_index",embedding_function=embeddings, persist_directory="db")

def index(documents):
    """Index the given documents into the vector store."""
    vector_store.add_documents(documents, ids=[doc.metadata["folder_path"] for doc in documents])

def search(query, k=5):
    """Search the vector store for the given query."""
    return vector_store.similarity_search(query, k=k)

def get_indexed_folders():
    """Get all indexed folder paths in the vector store."""
    data = vector_store.get(limit=None, include=["metadatas"])
    return [data["metadatas"][i]["folder_path"] for i in range(len(data["metadatas"]))]

def get_files_in_folder(folder_path):
    """Get all files directly in a folder (not including subfolders) using multi-threading."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return []
    
    try:
        # Get all items in the folder
        items = list(folder.iterdir())
        
        # Use thread pool to check files concurrently
        files = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit file checking tasks
            future_to_item = {
                executor.submit(lambda item: str(item) if item.is_file() else None, item): item 
                for item in items
            }
            
            # Collect results
            for future in as_completed(future_to_item):
                result = future.result()
                if result:  # Only add actual files
                    files.append(result)
        
        return files
    except (PermissionError, OSError) as e:
        print(f"⚠️ Permission denied or error accessing {folder_path}: {e}")
        return []

def get_all_folders(root_path, ignore_folders=None):
    """Get all folders recursively from root path using multi-threading, with optional ignore patterns."""
    if ignore_folders is None:
        ignore_folders = ("System Volume Information", "node_modules", ".git", ".venv", 
                         "RECYCLE.BIN", "dev")
    
    root = Path(root_path)
    folders = []
    folders_lock = threading.Lock()
    
    def process_directory(directory):
        """Process a single directory and return its subdirectories."""
        local_folders = []
        try:
            if not directory.exists() or not directory.is_dir():
                return local_folders
            
            folder_str = str(directory.resolve())
            # Check if current folder should be ignored
            if any(ignored.lower() in folder_str.lower() for ignored in ignore_folders):
                return local_folders
            
            # Add current folder
            local_folders.append(folder_str)
            
            # Get subdirectories
            for item in directory.iterdir():
                if item.is_dir():
                    item_str = str(item.resolve())
                    # Check if subdirectory should be ignored
                    if not any(ignored.lower() in item_str.lower() for ignored in ignore_folders):
                        local_folders.extend(process_directory(item))
                        
        except (PermissionError, OSError) as e:
            print(f"⚠️ Permission denied or error accessing {directory}: {e}")
        
        return local_folders
    
    def collect_folders_worker(dir_queue):
        """Worker function to process directories from queue."""
        while True:
            try:
                directory = dir_queue.get_nowait()
                local_folders = process_directory(directory)
                
                with folders_lock:
                    folders.extend(local_folders)
                    
            except:
                break
    
    # Start with root directory
    print(f"🔍 Scanning folders in {root_path} using multi-threading...")
    
    # For very large directory trees, use threading
    try:
        # Use a simpler approach - just use the recursive function directly
        # as the threading overhead might not be worth it for directory traversal
        root_folders = process_directory(root)
        folders.extend(root_folders)
        
    except Exception as e:
        print(f"❌ Error during folder scanning: {e}")
        # Fallback to simple approach
        for item in root.rglob("*"):
            if item.is_dir():
                folder_str = str(item.resolve())
                if not any(ignored.lower() in folder_str.lower() for ignored in ignore_folders):
                    folders.append(folder_str)
    
    print(f"📁 Total folders found under {root_path}: {len(folders)}")
    return folders

def folder_to_document(folder_path):
    """Convert a single folder to a document with its direct files only."""
    files = get_files_in_folder(folder_path)
    
    if not files:  # Skip empty folders
        print(f"⚠️ Skipping empty folder: {folder_path}")
        return None
    
    folder_name = os.path.basename(folder_path)
    filenames = [os.path.basename(f) for f in files]
    combined_content = f"{folder_name} {' '.join(filenames)}"
    
    print(f"📝 Creating document for: {folder_path} ({len(files)} files)")
    document = Document(
        page_content=combined_content,
        metadata={
            "folder_path": folder_path,
            "file_count": len(files),
            "files": "|".join(files)  # Convert list to pipe-separated string
        }
    )
    return document

def build_index(root_path, max_folders=None):
    """Build the file index for all folders under root_path.
    
    Args:
        root_path: Root directory to index
        max_folders: Optional limit on number of folders to index (for testing)
    """
    print(f"Building index for: {root_path}")
    
    # Get all folders (with ignoring logic built-in)
    all_folders = get_all_folders(root_path)
    
    # Get already indexed folders and normalize them
    indexed_folders = get_indexed_folder_paths()
    indexed_folders_normalized = {str(Path(f).resolve()) for f in indexed_folders}
    
    # Filter out already indexed folders using normalized paths
    new_folders = [f for f in all_folders if f not in indexed_folders_normalized]

    print(f"Found {len(all_folders)} folders to process.")
    # Remove indexed folders that no longer exist
    all_folders_set = set(all_folders)
    for folder_path in indexed_folders:
        normalized_path = str(Path(folder_path).resolve())
        if normalized_path not in all_folders_set:
            try:
                vector_store.delete(where={"folder_path": folder_path})
                print(f"Removed deleted folder from index: {folder_path}")
            except Exception as e:
                print(f"Error removing folder {folder_path}: {e}")
    
    print(f"# of new folders to index: {len(new_folders)}")
    
    if max_folders:
        new_folders = new_folders[:max_folders]
        print(f"Limited to {max_folders} folders for testing")
    
    # Convert folders to documents using multi-threading
    print(f"🧵 Creating documents using multi-threading...")
    documents = []
    indexed_count = 0
    skipped_count = 0
    
    def process_folder_batch(folder_batch):
        """Process a batch of folders and return documents."""
        batch_docs = []
        batch_skipped = 0
        
        for folder_path in folder_batch:
            doc = folder_to_document(folder_path)
            if doc:
                batch_docs.append(doc)
            else:
                batch_skipped += 1
        
        return batch_docs, batch_skipped
    
    # Process folders in batches using thread pool
    batch_size = 10
    folder_batches = [new_folders[i:i + batch_size] for i in range(0, len(new_folders), batch_size)]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_batch = {
            executor.submit(process_folder_batch, batch): i 
            for i, batch in enumerate(folder_batches)
        }
        
        for future in as_completed(future_to_batch):
            batch_docs, batch_skipped = future.result()
            batch_num = future_to_batch[future]
            
            if batch_docs:
                # Index the batch
                index(batch_docs)
                indexed_count += len(batch_docs)
                print(f"✅ Indexed batch {batch_num + 1}/{len(folder_batches)}: {len(batch_docs)} folders")
                sleep(2)  # Brief pause between batches
            
            skipped_count += batch_skipped
            
            # Progress update
            processed = min((batch_num + 1) * batch_size, len(new_folders))
            print(f"📊 Progress: {processed}/{len(new_folders)} processed, {indexed_count} indexed, {skipped_count} skipped")
    
    if indexed_count > 0:
        print(f"✅ Successfully completed indexing:")
        print(f"   📁 {indexed_count} folders indexed")
        print(f"   ⚠️ {skipped_count} empty folders skipped") 
        print(f"   📊 {len(new_folders)} total folders processed")
    else:
        if skipped_count > 0:
            print(f"⚠️ No folders indexed - all {skipped_count} folders were empty")
        else:
            print("No new folders to index.")

def get_indexed_folder_paths():
    """Get all indexed folder paths."""
    try:
        data = vector_store.get(limit=None, include=["metadatas"])
        return [data["metadatas"][i]["folder_path"] for i in range(len(data["metadatas"]))]
    except:
        return []

def build_single_document_index(root_path, additional_paths=None):
    """Build a single large document containing all folder and file information using multi-threading.
    
    Args:
        root_path: Root directory to index
        additional_paths: Optional list of additional paths to include
    """
    print(f"🧵 Building single document index for: {root_path} (multi-threaded)")
    
    # Combine root path with additional paths
    paths_to_index = [root_path]
    if additional_paths:
        paths_to_index.extend(additional_paths)
    
    # Get all folders from all paths using multi-threading
    all_folders = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_path = {
            executor.submit(get_all_folders, path): path 
            for path in paths_to_index
        }
        
        for future in as_completed(future_to_path):
            path_folders = future.result()
            all_folders.extend(path_folders)
    
    print(f"📁 Found {len(all_folders)} folders to process.")
    
    # Process folders in parallel to collect file information
    def process_folder_for_content(folder_path):
        """Process a single folder and return content info."""
        files = get_files_in_folder(folder_path)
        if files:  # Only include non-empty folders
            folder_name = os.path.basename(folder_path)
            filenames = [os.path.basename(f) for f in files]
            folder_content = f"{folder_name}: {' '.join(filenames)}"
            return {
                "content": folder_content,
                "folder_path": folder_path,
                "file_count": len(files),
                "files": files
            }
        return None
    
    # Collect all folder and file information using threading
    all_content = []
    all_files = []
    folder_info = []
    
    print("🔄 Processing folders for content extraction...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_folder = {
            executor.submit(process_folder_for_content, folder_path): folder_path
            for folder_path in all_folders
        }
        
        completed = 0
        for future in as_completed(future_to_folder):
            result = future.result()
            completed += 1
            
            if result:
                all_content.append(result["content"])
                all_files.extend(result["files"])
                folder_info.append({
                    "folder_path": result["folder_path"],
                    "file_count": result["file_count"],
                    "files": result["files"]
                })
            
            # Progress update every 100 folders
            if completed % 100 == 0:
                print(f"📊 Processed {completed}/{len(all_folders)} folders...")
    
    if not all_content:
        print("No folders with files found.")
        return
    
    # Create one big document
    combined_text = " | ".join(all_content)
    
    # Create metadata summary
    total_files = len(all_files)
    total_folders = len(folder_info)
    
    # Clear existing index
    try:
        # Delete all existing documents
        existing_data = vector_store.get(limit=None)
        if existing_data['ids']:
            vector_store.delete(ids=existing_data['ids'])
            print(f"🗑️ Cleared {len(existing_data['ids'])} existing documents")
    except Exception as e:
        print(f"❌ Error clearing existing index: {e}")
    
    # Create the single mega-document
    document = Document(
        page_content=combined_text,
        metadata={
            "index_type": "single_document",
            "root_path": root_path,
            "total_folders": total_folders,
            "total_files": total_files,
            "folder_info": str(folder_info)  # Convert to string for Chroma
        }
    )
    
    # Index the single document
    print("💾 Indexing the mega-document...")
    vector_store.add_documents([document], ids=["master_index"])
    print(f"✅ Successfully created single document index:")
    print(f"   📁 {total_folders} folders")
    print(f"   📄 {total_files} files")
    print(f"   📊 Document size: {len(combined_text):,} characters")


if __name__ == "__main__":
    # Choose indexing method:
    
    # Option 1: Build separate documents per folder (original method)
    # build_index("D:\\CS", max_folders=10)
    
    # Option 2: Build one big document with everything
    build_single_document_index("D:\\CS")

