from httpx import get
from langchain_chroma import Chroma
from dotenv import load_dotenv
from glob import glob
import os
from pathlib import Path
from collections import defaultdict

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
    """Get all files directly in a folder (not including subfolders)."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return []
    
    files = []
    for item in folder.iterdir():
        if item.is_file():
            files.append(str(item))
    return files

def get_all_folders(root_path, ignore_folders=None):
    """Get all folders recursively from root path, with optional ignore patterns."""
    if ignore_folders is None:
        ignore_folders = ("System Volume Information", "node_modules", ".git", ".venv", 
                         "RECYCLE.BIN", "dev")
    
    root = Path(root_path)
    folders = []
    
    for item in root.rglob("*"):
        if item.is_dir():
            folder_str = str(item.resolve())  # Normalize path
            # Check if any ignore pattern is in the folder path
            if not any(ignored.lower() in folder_str.lower() for ignored in ignore_folders):
                folders.append(folder_str)
    
    # Include the root folder itself if it doesn't match ignore patterns
    root_str = str(root.resolve())
    if not any(ignored.lower() in root_str.lower() for ignored in ignore_folders):
        folders.append(root_str)
    
    print(f"Total folders found under {root_path}: {len(folders)}")
    return folders

def folder_to_document(folder_path):
    """Convert a single folder to a document with its direct files only."""
    files = get_files_in_folder(folder_path)
    
    if not files:  # Skip empty folders
        return None
    
    folder_name = os.path.basename(folder_path)
    filenames = [os.path.basename(f) for f in files]
    combined_content = f"{folder_name} {' '.join(filenames)}"
    
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
    
    # Convert folders to documents and index them one by one
    documents = []
    indexed_count = 0
    
    for i, folder_path in enumerate(new_folders, 1):
        doc = folder_to_document(folder_path)
        if doc:  # Only add non-empty folders
            documents.append(doc)
            
            # Index every 2 folders or at the end
            if len(documents) >= 2 or i == len(new_folders):
                index(documents)
                indexed_count += len(documents)
                print(f"Indexed batch: {len(documents)} folders (Total: {indexed_count}/{len(new_folders)})")
                documents = []  # Reset for next batch
    
    if indexed_count > 0:
        print(f"✅ Successfully completed indexing {indexed_count} folders.")
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
    """Build a single large document containing all folder and file information.
    
    Args:
        root_path: Root directory to index
        additional_paths: Optional list of additional paths to include
    """
    print(f"Building single document index for: {root_path}")
    
    # Combine root path with additional paths
    paths_to_index = [root_path]
    if additional_paths:
        paths_to_index.extend(additional_paths)
    
    # Get all folders from all paths
    all_folders = []
    for path in paths_to_index:
        all_folders.extend(get_all_folders(path))
    
    print(f"Found {len(all_folders)} folders to process.")
    
    # Collect all folder and file information
    all_content = []
    all_files = []
    folder_info = []
    
    for folder_path in all_folders:
        files = get_files_in_folder(folder_path)
        if files:  # Only include non-empty folders
            folder_name = os.path.basename(folder_path)
            filenames = [os.path.basename(f) for f in files]
            
            # Add to combined content
            folder_content = f"{folder_name}: {' '.join(filenames)}"
            all_content.append(folder_content)
            all_files.extend(files)
            
            folder_info.append({
                "folder_path": folder_path,
                "file_count": len(files),
                "files": files
            })
    
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
            print(f"Cleared {len(existing_data['ids'])} existing documents")
    except Exception as e:
        print(f"Error clearing existing index: {e}")
    
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
    vector_store.add_documents([document], ids=["master_index"])
    print(f"✅ Successfully created single document index:")
    print(f"   - {total_folders} folders")
    print(f"   - {total_files} files")
    print(f"   - Document size: {len(combined_text)} characters")


if __name__ == "__main__":
    # Choose indexing method:
    
    # Option 1: Build separate documents per folder (original method)
    # build_index("D:\\CS", max_folders=10)
    
    # Option 2: Build one big document with everything
    build_single_document_index("D:\\CS")

