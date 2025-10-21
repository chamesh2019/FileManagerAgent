"""
File operation tools for copying, moving, deleting, and creating files/folders.
"""

from typing import List, Dict
import os
import shutil
from pathlib import Path
from langchain_core.tools import tool
from concurrent.futures import ThreadPoolExecutor


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
def get_files_in_folder(folder_path: str) -> List[str]:
    """Get a list of all files in the specified folder and subfolders.
    
    Args:
        folder_path: Path to the folder
    Returns:
        A list of file paths
    """
    print(f"📂 LISTING ALL FILES: Scanning folder '{folder_path}'")
    files_list = []
    
    def collect_files(root_dir):
        files = []
        try:
            for root, _, filenames in os.walk(root_dir):
                for file in filenames:
                    files.append(os.path.join(root, file))
        except Exception as e:
            print(f"❌ Error scanning {root_dir}: {str(e)}")
        return files
    
    # Use ThreadPoolExecutor for concurrent directory scanning
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit initial walk
        future = executor.submit(collect_files, folder_path)
        files_list = future.result()

    print(f"📋 Found {len(files_list)} files in folder hierarchy")
    return files_list


@tool
def files_and_subfolders_in_folder(folder_path: str) -> Dict[str, List[str]]:
    """Gets lists of files and folders directly within a given folder path.
    
    This function does not recurse into subdirectories.

    Args:
        folder_path (str or Path): The absolute or relative path to the folder.

    Returns:
        dict: A dictionary with two keys:
              'files': A list of filenames (str).
              'folders': A list of folder names (str).
              Returns {'files': [], 'folders': []} if the path is invalid
              or permissions are denied.
    """
    p = Path(folder_path)
    files = []
    folders = []

    print(f"📂 LISTING CONTENTS: Scanning folder '{folder_path}'")

    try:
        # p.iterdir() iterates over the items in the directory *non-recursively*.
        for entry in p.iterdir():
            if entry.is_file():
                files.append(entry.name)
            elif entry.is_dir():
                folders.append(entry.name)
                
    except FileNotFoundError:
        print(f"Error: Path not found: {folder_path}")
        return {"files": [], "folders": []}
    except NotADirectoryError:
        print(f"Error: Path is not a directory: {folder_path}")
        return {"files": [], "folders": []}
    except PermissionError:
        print(f"Error: Permission denied for: {folder_path}")
        return {"files": [], "folders": []}
            
    return {"files": files, "folders": folders}
