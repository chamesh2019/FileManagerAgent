"""
UI operation tools for opening files, applications, and URIs.
"""

import os
import subprocess
import webbrowser
from langchain_core.tools import tool


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


@tool
def open_application(app_path: str) -> str:
    """Open the specified application.
    
    Args:
        app_path: Path to the application executable

    Returns:
        A message indicating success or failure.
    """
    print(f"🪟 OPEN APPLICATION: Opening application at '{app_path}'")
    app_dir = os.path.dirname(app_path)

    try:
        print(f"Starting {app_path}...")
        print(f"Setting working directory to: {app_dir}")

        # Check if the file exists before trying to open it
        if not os.path.exists(app_path):
            return (f"Error: The file was not found at {app_path}")

        try:
            # Use shell=True with 'start' command on Windows
            subprocess.Popen(f'start "" "{app_path}"', shell=True, cwd=app_dir)
            return (f"Application {app_path} started successfully.")

        except PermissionError:
            return (f"Error: Insufficient permissions to run {app_path}")
        except Exception as e:
            return (f"An unexpected error occurred: {e}")
    except Exception as e:
        print(f"❌ Error opening application: {str(e)}")
        return f"Error opening application at {app_path}: {str(e)}"


@tool
def open_uri(uri):
    """
    Opens a given URI using the system's default application.
    
    This uses the cross-platform 'webbrowser' module, which 
    correctly handles various URI schemes (http:, file:, ms-settings:, etc.)
    on Windows 11.

    Args:
        uri (str): The URI to open (e.g., 'http://google.com', 
                     'ms-settings:display', 'C:\\Users\\')

    Returns:
        bool: True if the call was successful, False otherwise.
    """
    print(f"Attempting to open: {uri}")
    try:
        # webbrowser.open() is the standard, cross-platform way.
        # On Windows, it's smart enough to handle OS-specific URIs.
        success = webbrowser.open(uri)
        if not success:
            print(f"Warning: webbrowser.open() reported failure for {uri}")
        return success
    except Exception as e:
        print(f"Error opening URI '{uri}': {e}")
        return False
