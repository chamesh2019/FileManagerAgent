"""
File utility tools for hashing and file analysis.
"""

import hashlib
from langchain_core.tools import tool


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
