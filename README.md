# Gmail Email Extractor

> **⚠️ AI-Generated Code**: This project, including the code and this README, was generated using Claude (Anthropic's AI assistant). While functional, please review and test thoroughly before use in production environments.

A CLI tool to extract emails to/from specific email addresses from your Gmail account. The tool organizes extracted emails into folders and generates CSV files with email metadata.

## Features

- **Interactive Setup Wizard** - Guided Gmail API setup in 3-5 minutes
- **Continuous Interactive Menu** - Simple menu that loops after each operation, no need to restart
- **Attachment Download** - Optional download of email attachments
- Extract emails where specific addresses appear in From, To, or CC fields
- **Case-insensitive email matching** - Handles emails regardless of capitalization
- Automatic folder organization by email address
- HTML email files with headers and formatting
- CSV file with email metadata (subject, date, from, to, cc, attachments)
- Support for Google Workspace accounts
- Handles pagination for large email volumes
- **Enhanced error messages** with helpful troubleshooting
- **Setup validation** to verify configuration
- **Easy authentication reset**
- Automatic deduplication of email addresses

## Quick Start (3 Steps)

### 1. Run the script

```bash
./run.sh
```

**That's it!** The script automatically:
- Creates a virtual environment if needed
- Installs dependencies if needed
- Runs the gmail extractor

### 2. First-time setup (one time only)

When the menu appears, select option **1 (Setup wizard)**. The wizard will:
- Guide you through Google Cloud Console setup
- Automatically open the necessary pages in your browser
- Validate your credentials
- Test authentication
- **Setup time: 3-5 minutes**

### 3. Create email list and extract

```bash
./run.sh  # Run again
```

1. Select option **2 (Initialize)** to create `email_addresses.txt`
2. Edit the file and add email addresses (one per line)
3. Run `./run.sh` again and select option **4** (metadata only) or **5** (with attachments)

Done! Your emails will be in the `extracted_emails/` folder.

## Prerequisites

- Python 3.7 or higher
- A Google account with Gmail
- Google Cloud Console access (free - no billing required)

## Detailed Setup Guide

### Option 1: Interactive Setup Wizard (Recommended)

The setup wizard automatically guides you through the process:

```bash
./run.sh
```

Then select option **1 (Setup wizard)** from the menu. The wizard will:
1. Check your current setup status
2. Open Google Cloud Console pages in your browser
3. Provide step-by-step instructions for:
   - Creating a Google Cloud project
   - Enabling Gmail API
   - Creating OAuth 2.0 credentials
   - Downloading credentials.json
4. Validate your credentials file
5. Test authentication
6. Confirm everything is working

### Option 2: Manual Setup

If you prefer to set up manually:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Click "Enable APIs and Services"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - Choose "Internal" for Workspace or "External" for personal Gmail
     - Fill in app name: "Gmail Extractor"
     - Add your email
     - Click through the steps
   - Choose **"Desktop app"** as the application type
   - Give it a name (e.g., "Gmail Extractor CLI")
   - Click "Create"
5. Download the credentials:
   - Click the download icon next to your OAuth client
   - Save the file as **`credentials.json`** in this directory

Then validate your setup:

```bash
./run.sh
# Select option 3 (Validate setup)
```

## Usage

The tool uses an interactive menu system that loops continuously. Simply run:

```bash
./run.sh
```

*Note: You can also use `python3 gmail_extractor.py` if you've manually set up a venv*

You'll see a menu with these options:
1. **Setup wizard** - Configure Gmail API (first-time setup)
2. **Initialize** - Create email_addresses.txt template
3. **Validate setup** - Check configuration status
4. **Extract emails (metadata only)** - Extract emails without attachments
5. **Extract emails (with attachments)** - Extract emails and download attachments
6. **Reset authentication** - Delete saved tokens
7. **Exit** - Quit the program

**The menu will automatically return after each operation**, allowing you to perform multiple tasks in one session. Select option 7 when you're done to exit.

### Create email addresses file

Run the script and select option **2 (Initialize)**

Edit `email_addresses.txt` and add email addresses (one per line):

```
john.doe@company.com
jane.smith@example.com
# Lines starting with # are comments

# Email addresses are case-insensitive
# These are treated as the same:
# John.Doe@Company.com
# john.doe@company.com
```

**Note**: Email addresses are automatically normalized to lowercase and duplicates are removed.

### Extract emails

Run the script:

```bash
./run.sh
```

Then choose:
- Option **4** for metadata-only extraction (faster, no attachments)
- Option **5** to extract emails with attachments

On first extraction, the tool will:
1. Open your browser for Google authentication
2. Ask you to sign in and grant permissions
3. Save authentication token (in `token.pickle`)

Future runs use the saved token automatically.

### Attachment Download

When selecting option **5 (Extract emails with attachments)**:
- Attachments are saved in an `attachments/` subfolder for each email
- Attachment filenames are recorded in the CSV metadata file
- All attachment types are supported (PDFs, images, documents, etc.)
- Duplicate attachment filenames are automatically handled

## Output Structure

```
extracted_emails/
├── john.doe@company.com/
│   ├── emails.csv
│   ├── 0001_Meeting_notes.html
│   ├── 0002_Project_update.html
│   ├── 0003_Invoice/
│   │   └── attachments/
│   │       ├── invoice.pdf
│   │       └── receipt.png
│   └── ...
└── jane.smith@example.com/
    ├── emails.csv
    ├── 0001_Introduction.html
    └── ...
```

**Note**: When attachments are downloaded, emails with attachments get their own subfolder containing an `attachments/` directory.

### CSV Format

Each `emails.csv` contains:

| Filename | Subject | From | To | Cc | Date | Message ID | Attachments |
|----------|---------|------|----|----|------|------------|-------------|
| 0001_Meeting_notes.html | Meeting notes | sender@email.com | you@email.com | colleague@email.com | 2025-01-15 14:30:00 | abc123... | |
| 0003_Invoice.html | Invoice for January | billing@company.com | you@email.com | | 2025-01-16 09:15:00 | def456... | invoice.pdf, receipt.png |

### HTML Files

Each email is saved as an HTML file with:
- Email headers (Subject, From, To, Cc, Date) in a styled header section
- Full email body content
- Viewable in any web browser

## Interactive Menu Reference

The tool uses a unified interactive menu that continuously loops, allowing you to perform multiple operations without restarting. Simply run:

```bash
python gmail_extractor.py
```

Menu options:

1. **Setup wizard** - First-time Gmail API configuration (guided)
2. **Initialize** - Create email_addresses.txt template file
3. **Validate setup** - Check your configuration and authentication status
4. **Extract emails (metadata only)** - Fast extraction without attachments
5. **Extract emails (with attachments)** - Full extraction including attachments
6. **Reset authentication** - Delete saved tokens (useful for switching accounts)
7. **Exit** - Quit the program

After each operation completes, you'll be returned to the menu. This allows you to chain operations together (e.g., setup → validate → extract) in a single session.

### Workflow Example

**First-time setup (all in one session):**
```bash
./run.sh

# The menu appears - select options in sequence:
# 1. Select option 1 (Setup wizard) - Follow the guided setup
# 2. Menu returns - Select option 2 (Initialize) - Creates email_addresses.txt
# 3. Exit (option 7) and edit email_addresses.txt to add addresses
# 4. Run ./run.sh again

# Now extract:
# 5. Select option 5 (Extract emails with attachments)
# 6. Select option 7 (Exit) when done
```

**Typical usage (after setup):**
```bash
./run.sh

# Menu appears - choose what you need:
# - Option 4 or 5 to extract emails
# - Option 3 to validate setup
# - Option 6 to reset authentication if issues occur
# - Option 7 to exit

# The menu returns after each operation, so you can:
# - Extract multiple times
# - Validate between operations
# - Perform multiple tasks without restarting
```

## Files Created

- `run.sh` - Convenience script that handles venv automatically (included)
- `venv/` - Virtual environment (auto-created by run.sh)
- `email_addresses.txt` - List of email addresses to extract
- `credentials.json` - Google API credentials (you provide this)
- `token.pickle` - Saved authentication token (auto-generated)
- `extracted_emails/` - Directory containing all extracted emails

## Troubleshooting

### Check your setup status

```bash
./run.sh
# Select option 3 (Validate setup)
```

This will show the status of all required files and authentication.

### Common Issues

#### "credentials.json not found" or "invalid"

**Solution:**
- Run the script and select option 1 (Setup wizard)
- Or manually download OAuth 2.0 **Desktop App** credentials from Google Cloud Console
- Make sure the file is named exactly `credentials.json`
- Use option 3 (Validate setup) to check status

#### "Permission denied" or "Access not configured"

**Solution:**
- Ensure Gmail API is enabled in your Google Cloud project
- Run the script and select option 1 (Setup wizard)
- Check that you selected the correct project in Google Cloud Console

#### Authentication errors or expired token

**Solution:**
```bash
./run.sh
# Select option 6 (Reset authentication) to delete old tokens
# Then run ./run.sh again and select option 4 or 5 to extract (will re-authenticate)
```

#### Rate limiting

If you're extracting a very large number of emails, you might hit Gmail API rate limits. The script will show errors for failed requests. Simply re-run to continue - it will skip already downloaded emails.

#### Setup wizard not opening browser

The wizard will print URLs if it can't open your browser automatically. Copy and paste them into your browser manually.

### Getting Help

If you encounter issues:
1. Run the script and select option 3 (Validate setup) to check your configuration
2. Check that you're using Python 3.7 or higher: `python --version`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Review the error messages - they include helpful troubleshooting tips

## Privacy & Security

- Your credentials and tokens are stored locally
- The app only requests read-only access to Gmail
- No data is sent to any third-party servers
- Email data is saved locally on your computer

## Testing

This project includes a test suite to ensure code quality and robustness.

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest test_gmail_extractor.py -v

# Run tests with coverage report
pytest test_gmail_extractor.py --cov=gmail_extractor --cov-report=term-missing

# Run specific test class
pytest test_gmail_extractor.py::TestEmailAddressLoading -v
```

### Test Coverage

The test suite covers:
- ✅ Credentials file validation
- ✅ Email address loading and normalization
- ✅ Case-insensitive duplicate removal
- ✅ Comment and whitespace handling
- ✅ Filename sanitization
- ✅ Gmail query building
- ✅ Authentication status checking
- ✅ Attachment extraction (with attachmentId)
- ✅ Inline attachment handling
- ✅ Duplicate attachment filename handling
- ✅ Nested multipart message attachments
- ✅ Edge cases (unicode, empty strings, etc.)

Current coverage includes core utility functions and attachment extraction logic

### Writing Tests

When contributing, please:
1. Add tests for new features
2. Ensure existing tests still pass
3. Aim for meaningful coverage of critical paths
4. Use pytest fixtures for test data

## Workspace Admin Notes

As a Google Workspace administrator:
- You can extract emails from any account you have access to
- Use "Internal" OAuth consent screen type for easier setup
- Consider creating a service account if you need to automate this for multiple users

## Use Cases

- **Email archival**: Backup emails from specific contacts
- **Legal/compliance**: Extract communications for discovery or audit
- **Research**: Analyze email patterns or content
- **Migration**: Export emails before switching platforms
- **Personal organization**: Create local backups of important correspondence

## Contributing

Contributions are welcome! This is an open-source project under the MIT License.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Improvement

- Implement incremental extraction (only new emails)
- Add support for filtering by date range
- Add export to other formats (PDF, TXT, MBOX)
- Improve error handling and retry logic
- Add progress bars for large extractions
- Support for batch processing multiple accounts
- Add command-line arguments for automation/scripting

## Credits

- **Created by**: Ben Richardson
- **Generated with**: Claude (Anthropic AI)
- **Built with**:
  - [Google Gmail API](https://developers.google.com/gmail/api)
  - [google-api-python-client](https://github.com/googleapis/google-api-python-client)
  - [google-auth](https://github.com/googleapis/google-auth-library-python)

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Ben Richardson

**Note**: This software is provided "as is", without warranty of any kind. See the LICENSE file for full terms.

## Disclaimer

This tool accesses your Gmail account with read-only permissions. Your credentials are stored locally and never transmitted to third parties. However:

- Always review code before granting access to your email
- Use at your own risk
- The authors are not responsible for any data loss or security issues
- Ensure you comply with your organization's policies before extracting emails
- Be mindful of privacy laws and regulations when handling email data

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Check existing issues for solutions

---

**AI Generation Notice**: This entire project (code, documentation, and README) was created using Claude AI. While care has been taken to ensure quality and security, users should review the code and understand its functionality before use.
