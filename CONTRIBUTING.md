# Contributing to Gmail Email Extractor

Thank you for considering contributing to this project! This document provides guidelines for contributing.

## AI-Generated Project Notice

This project was originally generated using Claude AI. We welcome human contributions to improve, extend, and maintain the codebase!

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version)
   - Relevant logs or error messages

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain how it would benefit users
4. Consider implementation complexity

### Code Contributions

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/gmail-extractor.git
cd gmail-extractor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if any)
pip install pytest black flake8
```

#### Making Changes

1. **Fork** the repository
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**:
   - Manually test the functionality
   - Ensure existing features still work
   - Add tests if possible

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

   Good commit messages:
   - Use present tense ("Add feature" not "Added feature")
   - Be descriptive but concise
   - Reference issues if applicable (#123)

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**:
   - Describe what changes you made
   - Explain why these changes are needed
   - Reference any related issues
   - Include screenshots if UI changes

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

### Example

```python
def extract_email_header(headers: List[Dict], header_name: str) -> str:
    """
    Extract a specific header value from email headers.

    Args:
        headers: List of email header dictionaries
        header_name: Name of the header to extract

    Returns:
        Header value as string, or empty string if not found
    """
    for header in headers:
        if header['name'].lower() == header_name.lower():
            return header['value']
    return ''
```

## Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Add unit tests
- [ ] Add attachment download support
- [ ] Implement incremental extraction (only new emails)
- [ ] Add date range filtering
- [ ] Improve error handling

### Medium Priority
- [ ] Add progress bars for long operations
- [ ] Export to additional formats (PDF, MBOX, TXT)
- [ ] Add configuration file support
- [ ] Improve logging
- [ ] Add batch processing for multiple accounts

### Low Priority
- [ ] Create GUI version
- [ ] Add email search by subject/content
- [ ] Add statistics/reporting features
- [ ] Docker support
- [ ] CI/CD pipeline

## Testing

Currently, this project lacks automated tests. Adding tests is a great way to contribute!

### Manual Testing Checklist

Before submitting a PR, please test:

- [ ] Setup wizard completes successfully
- [ ] Credentials validation works
- [ ] Email extraction works for multiple addresses
- [ ] CSV files are generated correctly
- [ ] HTML files render properly
- [ ] Error messages are helpful
- [ ] Help command shows all options
- [ ] Validate command shows correct status
- [ ] Reset command clears authentication

## Documentation

Good documentation is crucial! When contributing:

- Update README.md if adding features
- Add docstrings to new functions
- Update command help text if changing CLI
- Add examples for new functionality
- Keep the AI generation notice intact

## Questions?

- Open an issue with the `question` label
- Be patient - this is a community project
- Search existing issues first

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve Gmail Email Extractor! 🎉
