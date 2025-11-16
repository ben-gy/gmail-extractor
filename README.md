# Gmail Email Extractor

> **⚠️ AI-Generated Code**: This project, including the code and this README, was generated using Claude (Anthropic's AI assistant). While functional, please review and test thoroughly before use in production environments.

A CLI tool to extract emails to/from specific email addresses from your Gmail account. The tool organizes extracted emails into folders and generates CSV files with email metadata.

## Features

- **Interactive Setup Wizard** - Guided Gmail API setup in 3-5 minutes
- Extract emails where specific addresses appear in From, To, or CC fields
- Automatic folder organization by email address
- HTML email files with headers and formatting
- CSV file with email metadata (subject, date, from, to, cc)
- Support for Google Workspace accounts
- Handles pagination for large email volumes
- **Enhanced error messages** with helpful troubleshooting
- **Setup validation** to verify configuration
- **Easy authentication reset**

## Quick Start (3 Steps)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the setup wizard

```bash
python gmail_extractor.py setup
```

The interactive wizard will:
- Guide you through Google Cloud Console setup
- Automatically open the necessary pages in your browser
- Validate your credentials
- Test authentication
- **Setup time: 3-5 minutes**

### 3. Extract emails

Create your email list and run extraction:

```bash
# Create email addresses file
python gmail_extractor.py init

# Edit email_addresses.txt and add the email addresses

# Extract emails
python gmail_extractor.py extract
```

Done! Your emails will be in the `extracted_emails/` folder.

## Prerequisites

- Python 3.7 or higher
- A Google account with Gmail
- Google Cloud Console access (free - no billing required)

## Detailed Setup Guide

### Option 1: Interactive Setup Wizard (Recommended)

The setup wizard automatically guides you through the process:

```bash
python gmail_extractor.py setup
```

The wizard will:
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
python gmail_extractor.py validate
```

## Usage

### Create email addresses file

```bash
python gmail_extractor.py init
```

Edit `email_addresses.txt` and add email addresses (one per line):

```
john.doe@company.com
jane.smith@example.com
# Lines starting with # are comments
```

### Extract emails

```bash
python gmail_extractor.py extract
```

Or run interactively:

```bash
python gmail_extractor.py
```

On first extraction, the tool will:
1. Open your browser for Google authentication
2. Ask you to sign in and grant permissions
3. Save authentication token (in `token.pickle`)

Future runs use the saved token automatically.

## Output Structure

```
extracted_emails/
├── john.doe@company.com/
│   ├── emails.csv
│   ├── 0001_Meeting_notes.html
│   ├── 0002_Project_update.html
│   └── ...
└── jane.smith@example.com/
    ├── emails.csv
    ├── 0001_Introduction.html
    └── ...
```

### CSV Format

Each `emails.csv` contains:

| Filename | Subject | From | To | Cc | Date | Message ID |
|----------|---------|------|----|----|------|------------|
| 0001_Meeting_notes.html | Meeting notes | sender@email.com | you@email.com | colleague@email.com | 2025-01-15 14:30:00 | abc123... |

### HTML Files

Each email is saved as an HTML file with:
- Email headers (Subject, From, To, Cc, Date) in a styled header section
- Full email body content
- Viewable in any web browser

## Command Reference

### Setup & Configuration

```bash
# Interactive setup wizard (recommended for first time)
python gmail_extractor.py setup

# Validate your setup and check status
python gmail_extractor.py validate

# Create email_addresses.txt template
python gmail_extractor.py init

# Reset authentication (delete tokens)
python gmail_extractor.py reset
```

### Extraction

```bash
# Extract emails (main operation)
python gmail_extractor.py extract

# Show help
python gmail_extractor.py help

# Interactive mode (no arguments)
python gmail_extractor.py
```

### Workflow Example

```bash
# First time setup
python gmail_extractor.py setup      # Run guided setup wizard
python gmail_extractor.py init       # Create email list file
# Edit email_addresses.txt and add addresses
python gmail_extractor.py extract    # Extract emails

# Subsequent runs
python gmail_extractor.py extract    # Just run extraction

# Troubleshooting
python gmail_extractor.py validate   # Check setup status
python gmail_extractor.py reset      # Reset if authentication issues
```

## Files Created

- `email_addresses.txt` - List of email addresses to extract
- `credentials.json` - Google API credentials (you provide this)
- `token.pickle` - Saved authentication token (auto-generated)
- `extracted_emails/` - Directory containing all extracted emails

## Troubleshooting

### Check your setup status

```bash
python gmail_extractor.py validate
```

This will show the status of all required files and authentication.

### Common Issues

#### "credentials.json not found" or "invalid"

**Solution:**
- Run the setup wizard: `python gmail_extractor.py setup`
- Or manually download OAuth 2.0 **Desktop App** credentials from Google Cloud Console
- Make sure the file is named exactly `credentials.json`
- Use the validate command to check: `python gmail_extractor.py validate`

#### "Permission denied" or "Access not configured"

**Solution:**
- Ensure Gmail API is enabled in your Google Cloud project
- Run the setup wizard: `python gmail_extractor.py setup`
- Check that you selected the correct project in Google Cloud Console

#### Authentication errors or expired token

**Solution:**
```bash
python gmail_extractor.py reset     # Delete old tokens
python gmail_extractor.py extract   # Will re-authenticate
```

#### Rate limiting

If you're extracting a very large number of emails, you might hit Gmail API rate limits. The script will show errors for failed requests. Simply re-run to continue - it will skip already downloaded emails.

#### Setup wizard not opening browser

The wizard will print URLs if it can't open your browser automatically. Copy and paste them into your browser manually.

### Getting Help

If you encounter issues:
1. Run `python gmail_extractor.py validate` to check your setup
2. Check that you're using Python 3.7 or higher: `python --version`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Review the error messages - they include helpful troubleshooting tips

## Privacy & Security

- Your credentials and tokens are stored locally
- The app only requests read-only access to Gmail
- No data is sent to any third-party servers
- Email data is saved locally on your computer

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

- Add support for attachments download
- Implement incremental extraction (only new emails)
- Add support for filtering by date range
- Add export to other formats (PDF, TXT, MBOX)
- Improve error handling and retry logic
- Add progress bars for large extractions
- Support for batch processing multiple accounts

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
