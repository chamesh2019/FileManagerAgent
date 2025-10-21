# Contributing to FileManagerAgent

Thank you for your interest in contributing to FileManagerAgent! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the Repository**
   - Click the "Fork" button at the top right of the repository page
   - Clone your fork locally:
     ```bash
     git clone https://github.com/YOUR_USERNAME/FileManagerAgent.git
     cd FileManagerAgent
     ```

2. **Set Up Development Environment**
   - Install UV package manager if you haven't already
   - Install dependencies: `uv sync`
   - Set up your `.env` file with your Google API key

3. **Create a Branch**
   - Create a new branch for your feature or bug fix:
     ```bash
     git checkout -b feature/your-feature-name
     ```
   - Use descriptive branch names (e.g., `feature/add-file-preview`, `fix/search-bug`)

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Tools and Functions

When adding new tools:
- Decorate with `@tool` from `langchain_core.tools`
- Include comprehensive docstrings with Args and Returns sections
- Add print statements for debugging and user feedback
- Handle errors gracefully with try-except blocks
- Return structured data (dictionaries or lists) when appropriate

Example:
```python
@tool
def your_new_tool(param: str) -> dict:
    """Brief description of what the tool does.
    
    Args:
        param: Description of parameter
    
    Returns:
        A dictionary with result information
    """
    print(f"🔧 TOOL NAME: Starting operation")
    try:
        # Your implementation
        result = do_something(param)
        print(f"✅ Operation successful")
        return {"status": "success", "result": result}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"status": "error", "message": str(e)}
```

### Safety Considerations

This project interacts with the file system. When contributing:
- Never bypass the confirmation system for destructive operations
- Test thoroughly with non-critical files
- Consider edge cases (empty folders, permission issues, etc.)
- Add appropriate error handling
- Document any limitations or requirements

### Testing

Currently, this project does not have a formal test suite. When making changes:
1. Test your changes manually with various scenarios
2. Verify edge cases and error conditions
3. Test with both valid and invalid inputs
4. Document your testing process in the PR description

## Making Changes

1. **Write Clear Commit Messages**
   - Use present tense ("Add feature" not "Added feature")
   - Keep the first line under 50 characters
   - Add details in the commit body if needed
   - Reference issues when applicable

   Example:
   ```
   Add file preview tool
   
   - Implement preview_file tool for viewing file contents
   - Add support for text files up to 1MB
   - Include error handling for binary files
   
   Fixes #123
   ```

2. **Keep Changes Focused**
   - One feature or bug fix per pull request
   - Avoid mixing unrelated changes
   - Keep pull requests reasonably sized

3. **Update Documentation**
   - Update README.md if you add new features
   - Update docstrings for changed functions
   - Add examples for new functionality

## Submitting a Pull Request

1. **Before Submitting**
   - Ensure your code works as expected
   - Check that you haven't introduced any errors
   - Update documentation as needed
   - Make sure your branch is up to date with main:
     ```bash
     git fetch upstream
     git rebase upstream/main
     ```

2. **Create the Pull Request**
   - Push your changes to your fork
   - Go to the original repository and click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template with:
     - Description of changes
     - Why the changes are needed
     - How you tested the changes
     - Screenshots (if applicable)

3. **PR Template**
   ```markdown
   ## Description
   Brief description of what this PR does
   
   ## Motivation
   Why is this change needed?
   
   ## Changes Made
   - Change 1
   - Change 2
   
   ## Testing
   How did you test these changes?
   
   ## Screenshots (if applicable)
   ```

## Code Review Process

- The maintainer will review your PR
- Be open to feedback and suggestions
- Make requested changes in new commits
- Once approved, your PR will be merged

## Areas for Contribution

Here are some areas where contributions would be particularly welcome:

### Features
- Cross-platform support (Linux, macOS)
- File preview functionality
- Batch operations with progress tracking
- Integration with cloud storage
- GUI interface
- Advanced search filters

### Improvements
- Unit tests and integration tests
- Performance optimizations
- Better error messages
- Logging improvements
- Configuration file support

### Documentation
- Video tutorials
- More usage examples
- API documentation
- Troubleshooting guide
- Best practices guide

## Questions?

If you have questions about contributing:
- Open an issue for discussion
- Check existing issues for similar questions
- Review closed PRs for examples

## Code of Conduct

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

## License

By contributing to FileManagerAgent, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to FileManagerAgent! 🎉
