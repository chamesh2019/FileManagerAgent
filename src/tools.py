import os
from typing import List
from langchain_core.tools import tool
import shutil
import hashlib
from pathlib import Path

from .db import search, vector_store

@tool
def copy_to_dest(src: List[str], dest: str):
    """Copy files or folders from source to destination.
    
    **Args:**
        src: List of source file/folder paths
        dest: Destination folder path
    
    **Returns:**
        A dictionary with keys 'copied' (list of successfully copied items) and 'errors' (list of tuples with item path and error message)
    """
    print(f"🔄 COPY OPERATION: Copying {len(src)} items to '{dest}'")
    copied = []
    errors = []
    
    # Ensure destination exists
    os.makedirs(dest, exist_ok=True)
    print(f"📁 Created destination directory: {dest}")
    
    for item_path in src:
        try:
            source_path = Path(item_path)
            dest_path = Path(dest)
            
            if source_path.is_file():
                # Copy file
                print(f"📄 Copying file: {item_path}")
                shutil.copy2(item_path, dest)
                copied.append(item_path)
                print(f"✅ File copied successfully")
            elif source_path.is_dir():
                # Copy entire directory tree
                dest_folder = dest_path / source_path.name
                print(f"📁 Copying folder: {item_path}")
                shutil.copytree(item_path, dest_folder, dirs_exist_ok=True)
                copied.append(item_path)
                print(f"✅ Folder copied successfully")
            else:
                print(f"❌ Path not found: {item_path}")
                errors.append((item_path, "Path does not exist or is not accessible"))
                
        except Exception as e:
            print(f"❌ Error copying {item_path}: {str(e)}")
            errors.append((item_path, str(e)))
    
    print(f"🎯 COPY COMPLETE: {len(copied)} items copied, {len(errors)} errors")
    return {
        "copied": copied,
        "errors": errors
    }

@tool
def move_to_dest(src: List[str], dest: str):
    """Move files or folders from source to destination. 
    Creates the destination folder if it does not exist.
    
    **Args:**
        src: List of source file/folder paths
        dest: Destination folder path

    **Returns:**
        A dictionary with keys 'moved' (list of successfully moved items) and 'errors' (list of tuples with item path and error message)
    """
    print(f"🚚 MOVE OPERATION: Moving {len(src)} items to '{dest}'")
    moved = []
    errors = []
    
    # Ensure destination exists
    os.makedirs(dest, exist_ok=True)
    print(f"📁 Created destination directory: {dest}")
    
    for item_path in src:
        try:
            source_path = Path(item_path)
            dest_path = Path(dest) / source_path.name
            
            print(f"➡️ Moving: {item_path} → {dest_path}")
            # Use shutil.move which works for both files and folders
            shutil.move(item_path, str(dest_path))
            moved.append(item_path)
            print(f"✅ Moved successfully")
            
        except Exception as e:
            print(f"❌ Error moving {item_path}: {str(e)}")
            errors.append((item_path, str(e)))
    
    print(f"🎯 MOVE COMPLETE: {len(moved)} items moved, {len(errors)} errors")
    return {
        "moved": moved,
        "errors": errors
    }

@tool
def delete_file(paths: List[str]):
    """Delete the specified files or folders.
    
    **Args:**
        paths: List of file/folder paths to delete
    
    **Returns:**
        A dictionary with keys 'deleted' (list of successfully deleted items) and 'errors' (list of tuples with item path and error message)
    """
    print(f"🗑️ DELETE OPERATION: Deleting {len(paths)} items")
    deleted = []
    errors = []
    
    for item_path in paths:
        try:
            path = Path(item_path)
            
            if path.is_file():
                print(f"🗄️ Deleting file: {item_path}")
                os.remove(item_path)
                deleted.append(item_path)
                print(f"✅ File deleted successfully")
            elif path.is_dir():
                print(f"📁 Deleting folder: {item_path}")
                shutil.rmtree(item_path)
                deleted.append(item_path)
                print(f"✅ Folder deleted successfully")
            else:
                print(f"❌ Path not found: {item_path}")
                errors.append((item_path, "Path does not exist or is not accessible"))
                
        except Exception as e:
            print(f"❌ Error deleting {item_path}: {str(e)}")
            errors.append((item_path, str(e)))
    
    print(f"🎯 DELETE COMPLETE: {len(deleted)} items deleted, {len(errors)} errors")
    return {
        "deleted": deleted,
        "errors": errors
    }

@tool
def create_folder(folder_path: str):
    """Create a new folder at the specified path.
    
    **Args:**
        folder_path: Path of the folder to create
    
    **Returns:**
        A message indicating success or failure.
    """
    print(f"📁 CREATE FOLDER: Creating '{folder_path}'")
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Folder created successfully: {folder_path}")
        return f"Folder created at: {folder_path}"
    except Exception as e:
        print(f"❌ Error creating folder: {str(e)}")
        return f"Error creating folder {folder_path}: {str(e)}"

@tool
def search_with_context(context: str, k: int = 5):
    """Search the vector store to find files and folders by name or content context.
    
    **Args:**
        context: Search query to find matching files or folders
        k: Number of results to return (default: 5)
    
    **Returns:**
        A list of dictionaries containing matched file/folder content and metadata
    """
    print(f"🔍 SEARCH: Looking for '{context}' (max {k} results)")
    results = search(context, k=k)
    print(f"📊 Found {len(results)} matching results")
    
    formatted_results = []
    for i, doc in enumerate(results, 1):
        metadata = getattr(doc, "metadata", {})
        folder_path = metadata.get("folder_path", "Unknown")
        file_count = metadata.get("file_count", 0)
        print(f"  {i}. {folder_path} ({file_count} files)")
        formatted_results.append({
            "content": doc.page_content, 
            "metadata": metadata
        })
    
    return formatted_results

@tool
def get_file_count() -> int:
    """Get the total number of indexed files."""
    print("📊 COUNTING FILES: Getting total indexed file count")
    
    data = vector_store.get(limit=None, include=["metadatas"])
    total_files = 0
    for metadata in data["metadatas"]:
        total_files += metadata.get("file_count", 0)
    
    print(f"📁 Total indexed files: {total_files}")
    return total_files

@tool
def get_file_hash(path: str) -> str:
    """Compute a sha256 hash for a file based on its content
    
    Args:
        path: Path to the file

    Returns:
        A string representing the file hash
    """
    print(f"🔐 HASH: Computing SHA256 hash for '{path}'")
    try:
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        hash_result = sha256_hash.hexdigest()
        print(f"✅ Hash computed: {hash_result[:16]}...")
        return hash_result
    except Exception as e:
        print(f"❌ Error computing hash: {str(e)}")
        return f"Error hashing file {path}: {str(e)}"
    

@tool
def get_files_in_folder(folder_path: str) -> List[str]:
    """Get a list of all files in the specified folder and subfolders.
    
    Args:
        folder_path: Path to the folder
    Returns:
        A list of file paths
    """
    print(f"📂 LISTING FILES: Scanning folder '{folder_path}'")
    files_list = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            files_list.append(os.path.join(root, file))

    print(f"📋 Found {len(files_list)} files in folder hierarchy")
    return files_list

@tool
def open_explorer(path: str) -> str:
    """Open the specified folder in Windows Explorer.
    
    Args:
        path: Path to the folder to open

    Returns:
        A message indicating success or failure.
    """
    print(f"🪟 OPEN EXPLORER: Opening '{path}' in Windows Explorer")
    try:
        os.startfile(path)
        print(f"✅ Explorer opened successfully")
        return f"Opened Explorer at: {path}"
    except Exception as e:
        print(f"❌ Error opening Explorer: {str(e)}")
        return f"Error opening Explorer at {path}: {str(e)}"