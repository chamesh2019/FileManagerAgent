"""
Tools module for FileManagerAgent.

This module provides various file management and search tools organized
into logical submodules for better maintainability and reusability.
"""

from .file_operations import (
    copy_to_dest,
    move_to_dest,
    delete_file,
    create_folder,
    get_files_in_folder,
    files_and_subfolders_in_folder,
)
from .search_operations import (
    search_with_context,
    get_file_count,
)
from .file_utilities import (
    get_file_hash,
)
from .ui_operations import (
    open_explorer,
    open_application,
    open_uri,
)

__all__ = [
    # File operations
    "copy_to_dest",
    "move_to_dest",
    "delete_file",
    "create_folder",
    "get_files_in_folder",
    "files_and_subfolders_in_folder",
    # Search operations
    "search_with_context",
    "get_file_count",
    # File utilities
    "get_file_hash",
    # UI operations
    "open_explorer",
    "open_application",
    "open_uri",
]
