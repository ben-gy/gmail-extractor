#!/usr/bin/env python3
"""
Gmail Email Extractor CLI
Extracts emails to/from specific email addresses and organizes them into folders
"""

import os
import sys
import csv
import base64
import pickle
import json
import webbrowser
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# File paths
EMAIL_ADDRESSES_FILE = 'email_addresses.txt'
OUTPUT_DIR = 'extracted_emails'
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

# Console colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.ENDC}")

def print_step(step_num, total, msg):
    print(f"{Colors.BOLD}[Step {step_num}/{total}]{Colors.ENDC} {msg}")


def validate_credentials_file() -> tuple[bool, Optional[str]]:
    """Validate credentials.json file

    Returns:
        tuple: (is_valid, error_message)
    """
    if not os.path.exists(CREDENTIALS_FILE):
        return False, f"{CREDENTIALS_FILE} not found"

    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            data = json.load(f)

        # Check if it's a valid OAuth client credentials file
        if 'installed' not in data and 'web' not in data:
            return False, "Invalid credentials format. Must be OAuth 2.0 Desktop App credentials"

        client_config = data.get('installed') or data.get('web')
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']

        missing_fields = [field for field in required_fields if field not in client_config]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        return True, None

    except json.JSONDecodeError:
        return False, "File is not valid JSON"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def check_authentication_status() -> dict:
    """Check current authentication status

    Returns:
        dict with status information
    """
    status = {
        'has_credentials': os.path.exists(CREDENTIALS_FILE),
        'has_token': os.path.exists(TOKEN_FILE),
        'credentials_valid': False,
        'token_valid': False,
        'authenticated': False
    }

    if status['has_credentials']:
        is_valid, _ = validate_credentials_file()
        status['credentials_valid'] = is_valid

    if status['has_token']:
        try:
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
                status['token_valid'] = creds.valid if creds else False
                status['authenticated'] = status['token_valid']
        except:
            status['token_valid'] = False

    return status


class GmailExtractor:
    """Main class for extracting emails from Gmail"""

    def __init__(self):
        self.service = None
        self.email_addresses = []

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Validate credentials file first
        is_valid, error_msg = validate_credentials_file()
        if not is_valid:
            print_error(f"Credentials validation failed: {error_msg}")
            print_info("\nRun the setup wizard to configure Gmail API access:")
            print(f"  {Colors.BOLD}python gmail_extractor.py{Colors.ENDC} and select option 1 (Setup wizard)")
            print("\nOr manually:")
            print("  1. Go to https://console.cloud.google.com/")
            print("  2. Create a project and enable Gmail API")
            print("  3. Create OAuth 2.0 credentials (Desktop app)")
            print("  4. Download as 'credentials.json'")
            sys.exit(1)

        # Load saved credentials if they exist
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print_warning(f"Could not load saved token: {e}")
                print_info("Will re-authenticate...")

        # If credentials are invalid or don't exist, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print_info("Refreshing expired token...")
                    creds.refresh(Request())
                    print_success("Token refreshed successfully")
                except Exception as e:
                    print_warning(f"Token refresh failed: {e}")
                    print_info("Starting new authentication flow...")
                    creds = None

            if not creds:
                try:
                    print_info("Opening browser for authentication...")
                    print_info("Please sign in and grant permissions in your browser")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                    print_success("Authentication successful!")
                except Exception as e:
                    print_error(f"Authentication failed: {e}")
                    sys.exit(1)

            # Save credentials for future use
            try:
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                print_success(f"Authentication token saved to {TOKEN_FILE}")
            except Exception as e:
                print_warning(f"Could not save token: {e}")
                print_info("You may need to re-authenticate on next run")

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print_success("Successfully connected to Gmail API")
        except Exception as e:
            print_error(f"Failed to connect to Gmail API: {e}")
            sys.exit(1)

    def load_email_addresses(self):
        """Load email addresses from the text file (case-insensitive, deduplicated)"""
        if not os.path.exists(EMAIL_ADDRESSES_FILE):
            print_error(f"{EMAIL_ADDRESSES_FILE} not found!")
            print_info("Please create this file and add email addresses (one per line)")
            print(f"\nRun: {Colors.BOLD}python gmail_extractor.py{Colors.ENDC} and select option 2 (Initialize)")
            sys.exit(1)

        with open(EMAIL_ADDRESSES_FILE, 'r') as f:
            # Normalize to lowercase and remove duplicates while preserving order
            addresses = []
            seen = set()
            for line in f:
                email = line.strip().lower()
                if email and not email.startswith('#') and email not in seen:
                    addresses.append(email)
                    seen.add(email)

        self.email_addresses = addresses

        if not self.email_addresses:
            print_error(f"No email addresses found in {EMAIL_ADDRESSES_FILE}")
            print_info("Add email addresses to the file (one per line)")
            sys.exit(1)

        print_success(f"Loaded {len(self.email_addresses)} unique email address(es):")
        for email in self.email_addresses:
            print(f"  - {email}")

    def build_query(self, email_address: str) -> str:
        """Build Gmail search query for an email address"""
        # Search for emails where the address is in from, to, or cc
        return f"from:{email_address} OR to:{email_address} OR cc:{email_address}"

    def get_messages(self, email_address: str) -> List[str]:
        """Get all message IDs for an email address"""
        try:
            query = self.build_query(email_address)
            print(f"\nSearching for emails related to: {email_address}")

            messages = []
            page_token = None

            while True:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token
                ).execute()

                if 'messages' in results:
                    messages.extend(results['messages'])

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            print(f"Found {len(messages)} email(s)")
            return [msg['id'] for msg in messages]

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_header(self, headers: List[Dict], name: str) -> str:
        """Extract header value from email headers"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''

    def get_email_body_html(self, payload: Dict) -> str:
        """Extract HTML body from email payload"""
        html_body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html_body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='replace')
                        break
                elif part['mimeType'] == 'multipart/alternative':
                    html_body = self.get_email_body_html(part)
                    if html_body:
                        break

        # If no HTML part found, try plain text and wrap in HTML
        if not html_body:
            text_body = self.get_email_body_text(payload)
            if text_body:
                html_body = f"<html><body><pre>{text_body}</pre></body></html>"

        return html_body

    def get_email_body_text(self, payload: Dict) -> str:
        """Extract plain text body from email payload"""
        text_body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        text_body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='replace')
                        break
        elif payload['mimeType'] == 'text/plain':
            if 'data' in payload['body']:
                text_body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='replace')

        return text_body

    def extract_attachments(self, message: Dict, attachments_dir: Path) -> List[str]:
        """Extract and save attachments from an email message

        Args:
            message: The Gmail message object
            attachments_dir: Directory to save attachments to

        Returns:
            List of saved attachment filenames
        """
        saved_attachments = []

        def process_parts(parts):
            """Recursively process message parts to find attachments"""
            for part in parts:
                # Check if part has sub-parts (multipart)
                if 'parts' in part:
                    process_parts(part['parts'])
                    continue

                # Check if this part is an attachment
                filename = part.get('filename', '')
                if filename:
                    # This part has a filename, it's an attachment
                    attachment_id = part['body'].get('attachmentId')

                    if attachment_id:
                        # Download attachment using attachmentId
                        try:
                            attachment = self.service.users().messages().attachments().get(
                                userId='me',
                                messageId=message['id'],
                                id=attachment_id
                            ).execute()

                            # Decode and save attachment
                            file_data = base64.urlsafe_b64decode(attachment['data'])
                            safe_filename = self.sanitize_filename(filename)

                            # Handle duplicate filenames
                            filepath = attachments_dir / safe_filename
                            counter = 1
                            while filepath.exists():
                                name, ext = os.path.splitext(safe_filename)
                                safe_filename = f"{name}_{counter}{ext}"
                                filepath = attachments_dir / safe_filename
                                counter += 1

                            # Save file
                            with open(filepath, 'wb') as f:
                                f.write(file_data)

                            saved_attachments.append(safe_filename)

                        except Exception as e:
                            print_warning(f"Could not download attachment '{filename}': {e}")

                    elif 'data' in part['body']:
                        # Attachment data is inline (not using attachmentId)
                        try:
                            file_data = base64.urlsafe_b64decode(part['body']['data'])
                            safe_filename = self.sanitize_filename(filename)

                            # Handle duplicate filenames
                            filepath = attachments_dir / safe_filename
                            counter = 1
                            while filepath.exists():
                                name, ext = os.path.splitext(safe_filename)
                                safe_filename = f"{name}_{counter}{ext}"
                                filepath = attachments_dir / safe_filename
                                counter += 1

                            # Save file
                            with open(filepath, 'wb') as f:
                                f.write(file_data)

                            saved_attachments.append(safe_filename)

                        except Exception as e:
                            print_warning(f"Could not save attachment '{filename}': {e}")

        # Start processing from payload
        payload = message.get('payload', {})
        if 'parts' in payload:
            process_parts(payload['parts'])

        return saved_attachments

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Limit length

    def extract_emails_for_address(self, email_address: str, download_attachments: bool = False):
        """Extract all emails for a specific email address

        Args:
            email_address: Email address to extract emails for
            download_attachments: Whether to download email attachments
        """
        message_ids = self.get_messages(email_address)

        if not message_ids:
            print(f"No emails found for {email_address}")
            return

        # Create folder for this email address
        safe_email = self.sanitize_filename(email_address)
        email_dir = Path(OUTPUT_DIR) / safe_email
        email_dir.mkdir(parents=True, exist_ok=True)

        # Create CSV file
        csv_file = email_dir / 'emails.csv'
        csv_data = []

        print(f"Extracting {len(message_ids)} emails...")

        for idx, msg_id in enumerate(message_ids, 1):
            try:
                # Get full message
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                headers = message['payload']['headers']

                # Extract metadata
                subject = self.get_header(headers, 'Subject')
                from_addr = self.get_header(headers, 'From')
                to_addr = self.get_header(headers, 'To')
                cc_addr = self.get_header(headers, 'Cc')
                date_str = self.get_header(headers, 'Date')

                # Parse date
                try:
                    date_obj = parsedate_to_datetime(date_str)
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = date_str

                # Get HTML body
                html_body = self.get_email_body_html(message['payload'])

                # Handle attachments if requested
                attachment_filenames = []
                if download_attachments:
                    # Create email-specific directory for attachments
                    email_folder_name = f"{idx:04d}_{self.sanitize_filename(subject if subject else 'no_subject')}"
                    email_folder_path = email_dir / email_folder_name
                    attachments_dir = email_folder_path / "attachments"
                    attachments_dir.mkdir(parents=True, exist_ok=True)

                    # Extract attachments (method handles all cases)
                    attachment_filenames = self.extract_attachments(message, attachments_dir)

                    # Remove directory if no attachments were found
                    if not attachment_filenames and attachments_dir.exists():
                        attachments_dir.rmdir()
                        if email_folder_path.exists() and not any(email_folder_path.iterdir()):
                            email_folder_path.rmdir()

                # Save HTML file
                safe_subject = self.sanitize_filename(subject if subject else 'no_subject')
                html_filename = f"{idx:04d}_{safe_subject}.html"
                html_path = email_dir / html_filename

                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
    <style>
        .email-header {{
            background-color: #f0f0f0;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            font-family: Arial, sans-serif;
        }}
        .email-header p {{
            margin: 5px 0;
        }}
        .email-header strong {{
            display: inline-block;
            width: 80px;
        }}
    </style>
</head>
<body>
    <div class="email-header">
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>From:</strong> {from_addr}</p>
        <p><strong>To:</strong> {to_addr}</p>
        {f'<p><strong>Cc:</strong> {cc_addr}</p>' if cc_addr else ''}
        <p><strong>Date:</strong> {formatted_date}</p>
    </div>
    <div class="email-body">
        {html_body}
    </div>
</body>
</html>""")

                # Add to CSV data
                csv_data.append({
                    'Filename': html_filename,
                    'Subject': subject,
                    'From': from_addr,
                    'To': to_addr,
                    'Cc': cc_addr,
                    'Date': formatted_date,
                    'Message ID': msg_id,
                    'Attachments': ', '.join(attachment_filenames) if attachment_filenames else ''
                })

                if idx % 10 == 0:
                    print(f"  Processed {idx}/{len(message_ids)} emails...")

            except HttpError as error:
                print(f"Error processing message {msg_id}: {error}")
                continue

        # Write CSV file
        if csv_data:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Filename', 'Subject', 'From', 'To', 'Cc', 'Date', 'Message ID', 'Attachments']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            print(f"\nCompleted! Extracted {len(csv_data)} emails to: {email_dir}")
            print(f"  - CSV file: {csv_file}")
            print(f"  - HTML files: {len(csv_data)} files")

    def run(self, download_attachments: bool = False):
        """Main execution method

        Args:
            download_attachments: Whether to download email attachments
        """
        print("=" * 60)
        print("Gmail Email Extractor")
        if download_attachments:
            print("(With Attachments)")
        print("=" * 60)

        # Authenticate
        self.authenticate()

        # Load email addresses
        self.load_email_addresses()

        # Process each email address
        for email_address in self.email_addresses:
            self.extract_emails_for_address(email_address, download_attachments)

        print("\n" + "=" * 60)
        print("Extraction complete!")
        print(f"All emails saved to: {OUTPUT_DIR}/")
        if download_attachments:
            print("Attachments were downloaded and saved")
        print("=" * 60)


def generate_sample_email_file():
    """Generate a sample email addresses file"""
    if os.path.exists(EMAIL_ADDRESSES_FILE):
        print(f"{EMAIL_ADDRESSES_FILE} already exists.")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    sample_content = """# Email addresses to extract (one per line)
# Lines starting with # are ignored
# Email addresses are case-insensitive and will be normalized to lowercase
# Duplicates will be automatically removed

example1@gmail.com
example2@company.com
"""

    with open(EMAIL_ADDRESSES_FILE, 'w') as f:
        f.write(sample_content)

    print_success(f"Created {EMAIL_ADDRESSES_FILE}")
    print_info("Please edit this file and add the email addresses you want to extract.")


def interactive_setup_wizard():
    """Interactive setup wizard for Gmail API credentials"""
    print("=" * 70)
    print(f"{Colors.BOLD}{Colors.HEADER}Gmail Email Extractor - Setup Wizard{Colors.ENDC}")
    print("=" * 70)
    print("\nThis wizard will guide you through setting up Gmail API access.")
    print("Estimated time: 3-5 minutes")
    print("\n" + "=" * 70 + "\n")

    # Step 1: Check current status
    print_step(1, 6, "Checking current setup status")
    status = check_authentication_status()

    if status['authenticated']:
        print_success("Already authenticated!")
        print("\nCurrent status:")
        print(f"  ✓ credentials.json: {'Found' if status['has_credentials'] else 'Not found'}")
        print(f"  ✓ token.pickle: {'Found and valid' if status['token_valid'] else 'Found but invalid'}")
        response = input("\nDo you want to re-authenticate? (y/n): ")
        if response.lower() != 'y':
            print("Setup wizard cancelled.")
            return
        # Delete token to force re-auth
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            print_info("Deleted existing token")

    print("\n" + "-" * 70 + "\n")

    # Step 2: Google Cloud Console setup
    print_step(2, 6, "Google Cloud Console Setup")
    print("\nYou need to create OAuth 2.0 credentials in Google Cloud Console.")
    print("\nI'll open the necessary pages in your browser.")
    print("Please complete these steps:")
    print("\n  1. Create or select a project")
    print("  2. Enable the Gmail API")
    print("  3. Create OAuth 2.0 credentials (Desktop app)")
    print("  4. Download the credentials file")

    input("\nPress Enter to open Google Cloud Console in your browser...")

    # Open Google Cloud Console
    urls = [
        ("https://console.cloud.google.com/projectcreate", "Create Project"),
        ("https://console.cloud.google.com/apis/library/gmail.googleapis.com", "Enable Gmail API"),
        ("https://console.cloud.google.com/apis/credentials", "Create Credentials"),
    ]

    for url, description in urls:
        print_info(f"Opening: {description}")
        try:
            webbrowser.open(url)
            time.sleep(2)  # Brief delay between opening tabs
        except:
            print_warning(f"Could not open browser. Please visit manually: {url}")

    print("\n" + "-" * 70 + "\n")

    # Step 3: Detailed instructions
    print_step(3, 6, "Detailed Instructions")
    print(f"""
{Colors.BOLD}In the Google Cloud Console:{Colors.ENDC}

{Colors.CYAN}A. Create a Project (if you don't have one):{Colors.ENDC}
   - Click "Create Project"
   - Enter a project name (e.g., "Gmail Extractor")
   - Click "Create"
   - Wait for project creation (takes a few seconds)

{Colors.CYAN}B. Enable Gmail API:{Colors.ENDC}
   - Make sure your project is selected (top left)
   - You should see the Gmail API page
   - Click the blue "Enable" button
   - Wait for it to enable (takes a few seconds)

{Colors.CYAN}C. Create OAuth 2.0 Credentials:{Colors.ENDC}
   - Go to "Credentials" page (should already be open)
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted to configure consent screen:
     * Choose "Internal" (for Workspace) or "External" (for personal Gmail)
     * Fill in app name: "Gmail Extractor"
     * Add your email
     * Click "Save and Continue" through the steps
   - Back at "Create OAuth client ID":
     * Application type: {Colors.BOLD}"Desktop app"{Colors.ENDC}
     * Name: "Gmail Extractor CLI"
     * Click "Create"
   - A dialog appears with your client ID and secret
   - Click the {Colors.BOLD}download icon (⬇){Colors.ENDC} to download JSON

{Colors.CYAN}D. Save the credentials file:{Colors.ENDC}
   - Save the downloaded file as: {Colors.BOLD}credentials.json{Colors.ENDC}
   - Place it in this directory: {Colors.BOLD}{os.getcwd()}{Colors.ENDC}
""")

    print("-" * 70 + "\n")

    # Step 4: Wait for credentials file
    print_step(4, 6, "Waiting for credentials file")
    print(f"\nPlease save your downloaded credentials as: {Colors.BOLD}{CREDENTIALS_FILE}{Colors.ENDC}")
    print(f"In this directory: {Colors.BOLD}{os.getcwd()}{Colors.ENDC}")

    while True:
        if os.path.exists(CREDENTIALS_FILE):
            print_success(f"Found {CREDENTIALS_FILE}!")
            break

        response = input("\nFile saved? Press Enter to check (or 'q' to quit): ")
        if response.lower() == 'q':
            print_warning("Setup wizard cancelled")
            return

    print("\n" + "-" * 70 + "\n")

    # Step 5: Validate credentials
    print_step(5, 6, "Validating credentials file")
    is_valid, error_msg = validate_credentials_file()

    if not is_valid:
        print_error(f"Validation failed: {error_msg}")
        print("\nPlease check:")
        print("  1. You downloaded the correct file (OAuth 2.0 Desktop App credentials)")
        print("  2. The file is named exactly 'credentials.json'")
        print("  3. The file is in the current directory")
        return

    print_success("Credentials file is valid!")

    print("\n" + "-" * 70 + "\n")

    # Step 6: Test authentication
    print_step(6, 6, "Testing authentication")
    print("\nNow I'll test the authentication flow.")
    print_info("A browser window will open asking you to sign in and grant permissions.")
    print_info("Please sign in with the Google account you want to extract emails from.")

    input("\nPress Enter to start authentication...")

    try:
        extractor = GmailExtractor()
        extractor.authenticate()
        print_success("Authentication successful!")

        # Test API call
        print_info("Testing Gmail API access...")
        profile = extractor.service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'unknown')
        print_success(f"Connected to Gmail account: {email}")

    except Exception as e:
        print_error(f"Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you granted all requested permissions")
        print("  2. Try running the setup wizard again")
        print("  3. Check that Gmail API is enabled in your project")
        return

    print("\n" + "=" * 70)
    print(f"{Colors.GREEN}{Colors.BOLD}Setup Complete!{Colors.ENDC}")
    print("=" * 70)
    print("\nYou're all set! Next steps:")
    print(f"  1. Run {Colors.BOLD}python gmail_extractor.py{Colors.ENDC} and select option 2 to create {EMAIL_ADDRESSES_FILE}")
    print("  2. Add email addresses to extract")
    print("  3. Run the script again and select option 4 or 5 to extract emails")
    print("\n" + "=" * 70 + "\n")


def validate_setup():
    """Validate setup and show status"""
    print("=" * 60)
    print("Gmail Email Extractor - Setup Validation")
    print("=" * 60 + "\n")

    status = check_authentication_status()

    print("Checking setup status...\n")

    # Check credentials.json
    print(f"1. credentials.json: ", end="")
    if status['credentials_valid']:
        print_success("Found and valid")
    elif status['has_credentials']:
        print_warning("Found but invalid")
        _, error = validate_credentials_file()
        print(f"   Error: {error}")
    else:
        print_error("Not found")

    # Check token.pickle
    print(f"2. token.pickle: ", end="")
    if status['token_valid']:
        print_success("Found and valid")
    elif status['has_token']:
        print_warning("Found but expired/invalid")
    else:
        print_info("Not found (will be created on first auth)")

    # Check email addresses file
    print(f"3. {EMAIL_ADDRESSES_FILE}: ", end="")
    if os.path.exists(EMAIL_ADDRESSES_FILE):
        with open(EMAIL_ADDRESSES_FILE, 'r') as f:
            addresses = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if addresses:
            print_success(f"Found with {len(addresses)} address(es)")
        else:
            print_warning("Found but empty")
    else:
        print_error("Not found")

    # Overall status
    print("\n" + "-" * 60)
    if status['authenticated']:
        print_success("\n✓ Ready to extract emails!")
        print(f"\nRun: {Colors.BOLD}python gmail_extractor.py{Colors.ENDC} and select option 4 or 5")
    elif status['credentials_valid']:
        print_warning("\n⚠ Credentials configured, but not authenticated yet")
        print(f"\nRun: {Colors.BOLD}python gmail_extractor.py{Colors.ENDC} and select option 4 or 5")
        print("(You'll be prompted to authenticate)")
    else:
        print_error("\n✗ Setup incomplete")
        print(f"\nRun: {Colors.BOLD}python gmail_extractor.py{Colors.ENDC} and select option 1 (Setup wizard)")

    print("\n" + "=" * 60 + "\n")


def reset_authentication():
    """Reset authentication by deleting token file"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print_success(f"Deleted {TOKEN_FILE}")
        print_info("You'll need to re-authenticate on next run")
    else:
        print_info(f"{TOKEN_FILE} doesn't exist - nothing to reset")

    response = input("\nDo you also want to delete credentials.json? (y/n): ")
    if response.lower() == 'y':
        if os.path.exists(CREDENTIALS_FILE):
            os.remove(CREDENTIALS_FILE)
            print_success(f"Deleted {CREDENTIALS_FILE}")
        else:
            print_info(f"{CREDENTIALS_FILE} doesn't exist")


def main():
    """Main CLI entry point"""
    print("=" * 60)
    print(f"{Colors.BOLD}{Colors.HEADER}Gmail Email Extractor CLI{Colors.ENDC}")
    print("=" * 60)
    print("\nWhat would you like to do?\n")
    print(f"{Colors.CYAN}1.{Colors.ENDC} Setup wizard (configure Gmail API)")
    print(f"{Colors.CYAN}2.{Colors.ENDC} Initialize (create email_addresses.txt)")
    print(f"{Colors.CYAN}3.{Colors.ENDC} Validate setup")
    print(f"{Colors.CYAN}4.{Colors.ENDC} Extract emails (metadata only)")
    print(f"{Colors.CYAN}5.{Colors.ENDC} Extract emails (with attachments)")
    print(f"{Colors.CYAN}6.{Colors.ENDC} Reset authentication")
    print(f"{Colors.CYAN}7.{Colors.ENDC} Exit")

    choice = input(f"\n{Colors.BOLD}Enter choice (1-7):{Colors.ENDC} ").strip()

    if choice == '1':
        interactive_setup_wizard()
    elif choice == '2':
        generate_sample_email_file()
    elif choice == '3':
        validate_setup()
    elif choice == '4':
        extractor = GmailExtractor()
        extractor.run(download_attachments=False)
    elif choice == '5':
        extractor = GmailExtractor()
        extractor.run(download_attachments=True)
    elif choice == '6':
        reset_authentication()
    elif choice == '7':
        print("\nGoodbye!")
    else:
        print_error("\nInvalid choice. Please run the script again and choose 1-7.")


if __name__ == '__main__':
    main()
