# FileManagerAgent

A Windows file management agent powered by Google Gemini AI and LangGraph. This intelligent agent helps you manage your files through natural language commands, using vector search to efficiently locate files and folders on your system.

## Overview

FileManagerAgent is a personal project that combines the power of large language models with file system operations. It indexes your files into a vector database and allows you to interact with your file system through natural language conversations. The agent can:

- 🔍 Search for files and folders using semantic search
- 📁 Create, copy, move, and delete files and folders
- 🔐 Compute file hashes
- 📊 Count and list files in directories
- 🪟 Open folders in Windows Explorer
- ✅ Ask for confirmation before destructive operations

## Features

- **Intelligent File Search**: Uses vector embeddings to find files based on content and context
- **Safe Operations**: Always asks for confirmation before performing destructive actions
- **Recursive Indexing**: Automatically indexes folder structures for quick access
- **Natural Language Interface**: Interact with your file system using conversational commands
- **Windows Integration**: Direct integration with Windows Explorer

## Prerequisites

- Python 3.10 or higher
- [UV package manager](https://github.com/astral-sh/uv)
- Google API Key (for Gemini AI)
- Windows OS (for Explorer integration)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/chamesh2019/FileManagerAgent.git
   cd FileManagerAgent
   ```

2. **Install UV package manager** (if not already installed)
   ```bash
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install dependencies using UV**
   ```bash
   uv sync
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Configuration

### Environment Variables

The project requires the following environment variable:

- `GOOGLE_API_KEY`: Your Google API key for accessing Gemini AI services
  - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Indexing Your Files

Before using the agent, you need to index your file system. Edit `src/db.py` and uncomment the indexing section at the bottom:

```python
if __name__ == "__main__":
    # Option 1: Build separate documents per folder
    build_index("C:\\Your\\Path", max_folders=10)
    
    # Option 2: Build one big document with everything
    build_single_document_index("C:\\Your\\Path")
```

Then run:
```bash
uv run python src/db.py
```

**Note**: You can customize which folders to ignore by modifying the `ignore_folders` parameter in `get_all_folders()` function in `src/db.py`.

## Usage

### Starting the Agent

Run the main script to start the interactive file management agent:

```bash
uv run python main.py
```

### Example Commands

Once the agent is running, you can interact with it using natural language:

```
User: Find all my Python files in the Documents folder
User: Create a new folder called "Backups" in D:\
User: Move all .log files from C:\Temp to D:\Backups
User: Delete all temporary files in the Downloads folder
User: Show me files that contain "report" in their name
User: Open the folder where my tax documents are stored
```

### Indexing Options

The project supports two indexing strategies:

1. **Multiple Documents** (`build_index`): Creates separate vector documents for each folder
   - Better for large file systems
   - More granular search results

2. **Single Document** (`build_single_document_index`): Creates one large document with all file information
   - Faster initial queries
   - Better for smaller file systems

You can also index additional paths by using:
```python
build_single_document_index(
    root_path="D:/", 
    additional_paths=["C:/Users/username/Downloads"]
)
```

## Project Structure

```
FileManagerAgent/
├── src/
│   ├── file_manager_agent.py  # Main agent logic and LangGraph setup
│   ├── db.py                  # Vector database and indexing functions
│   └── tools.py               # File operation tools
├── main.py                    # Entry point for the application
├── pyproject.toml             # Project dependencies and metadata
├── .env                       # Environment variables (not in repo)
├── .env.example               # Example environment configuration
└── README.md                  # This file
```

## Available Tools

The agent has access to the following tools:

- `search_with_context(context, k)`: Search for files/folders using semantic search
- `copy_to_dest(src, dest)`: Copy files or folders to a destination
- `move_to_dest(src, dest)`: Move files or folders to a destination
- `delete_file(paths)`: Delete specified files or folders
- `create_folder(folder_path)`: Create a new directory
- `get_file_count()`: Get total number of indexed files
- `get_files_in_folder(folder_path)`: List all files in a folder (recursive)
- `get_file_hash(path)`: Compute SHA256 hash of a file
- `open_explorer(path)`: Open a folder in Windows Explorer

## Safety Features

The agent implements several safety measures:

1. **Confirmation Required**: Asks for explicit confirmation before any destructive operation
2. **Dry Run**: Performs a search preview before moving or deleting files
3. **Clear Communication**: Presents a plan before executing operations
4. **Error Handling**: Gracefully handles errors and reports them to the user

## Contributing

This is a personal project, but contributions are welcome! If you'd like to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

**Issue**: "Module not found" errors
- **Solution**: Ensure you've run `uv sync` to install all dependencies

**Issue**: "GOOGLE_API_KEY not found"
- **Solution**: Make sure you've created a `.env` file with your Google API key

**Issue**: No search results
- **Solution**: You need to index your files first by running `python src/db.py`

**Issue**: Agent is slow
- **Solution**: Consider using the single document indexing method for smaller file systems

## Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage

## Disclaimer

This tool performs actual file system operations. Always:
- Back up important files before using
- Review the agent's plan before confirming operations
- Test with non-critical files first
- Be cautious with delete operations

The author is not responsible for any data loss or system issues that may occur from using this tool.
