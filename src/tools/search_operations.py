"""
Search operation tools for finding and counting files in the vector store.
"""

from typing import List
from langchain_core.tools import tool
from ..db import search, vector_store


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
