#!/usr/bin/env python3
"""
Test suite for Gmail Email Extractor

Run with: pytest test_gmail_extractor.py -v
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import functions to test
import sys
sys.path.insert(0, os.path.dirname(__file__))
from gmail_extractor import (
    validate_credentials_file,
    check_authentication_status,
    GmailExtractor
)


class TestCredentialsValidation:
    """Test credentials file validation"""

    def test_missing_credentials_file(self, tmp_path):
        """Test validation fails when file doesn't exist"""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            is_valid, error = validate_credentials_file()
            assert is_valid is False
            assert "not found" in error.lower()
        finally:
            os.chdir(original_dir)

    def test_invalid_json_file(self, tmp_path):
        """Test validation fails for invalid JSON"""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{ invalid json }")

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            is_valid, error = validate_credentials_file()
            assert is_valid is False
            assert "not valid JSON" in error or "invalid" in error.lower()
        finally:
            os.chdir(original_dir)

    def test_missing_oauth_structure(self, tmp_path):
        """Test validation fails when OAuth structure is missing"""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text(json.dumps({"some": "data"}))

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            is_valid, error = validate_credentials_file()
            assert is_valid is False
            assert "invalid credentials format" in error.lower() or "desktop app" in error.lower()
        finally:
            os.chdir(original_dir)

    def test_missing_required_fields(self, tmp_path):
        """Test validation fails when required fields are missing"""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text(json.dumps({
            "installed": {
                "client_id": "test123"
                # Missing client_secret, auth_uri, token_uri
            }
        }))

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            is_valid, error = validate_credentials_file()
            assert is_valid is False
            assert "missing required fields" in error.lower()
        finally:
            os.chdir(original_dir)

    def test_valid_credentials_file(self, tmp_path):
        """Test validation passes for valid credentials"""
        valid_creds = {
            "installed": {
                "client_id": "test_client_id.apps.googleusercontent.com",
                "client_secret": "test_secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        }

        creds_file = tmp_path / "credentials.json"
        creds_file.write_text(json.dumps(valid_creds))

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            is_valid, error = validate_credentials_file()
            assert is_valid is True
            assert error is None
        finally:
            os.chdir(original_dir)


class TestEmailAddressLoading:
    """Test email address loading and normalization"""

    def test_case_insensitive_normalization(self, tmp_path):
        """Test that email addresses are normalized to lowercase"""
        emails_file = tmp_path / "email_addresses.txt"
        emails_file.write_text("""
John.Doe@Example.COM
jane.smith@company.com
ADMIN@SITE.ORG
""")

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = GmailExtractor()
            extractor.load_email_addresses()

            assert len(extractor.email_addresses) == 3
            assert all(email.islower() for email in extractor.email_addresses)
            assert "john.doe@example.com" in extractor.email_addresses
            assert "jane.smith@company.com" in extractor.email_addresses
            assert "admin@site.org" in extractor.email_addresses
        finally:
            os.chdir(original_dir)

    def test_duplicate_removal(self, tmp_path):
        """Test that duplicate email addresses are removed"""
        emails_file = tmp_path / "email_addresses.txt"
        emails_file.write_text("""
john.doe@example.com
John.Doe@Example.COM
JOHN.DOE@EXAMPLE.COM
jane.smith@company.com
jane.smith@company.com
""")

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = GmailExtractor()
            extractor.load_email_addresses()

            assert len(extractor.email_addresses) == 2
            assert "john.doe@example.com" in extractor.email_addresses
            assert "jane.smith@company.com" in extractor.email_addresses
        finally:
            os.chdir(original_dir)

    def test_comment_lines_ignored(self, tmp_path):
        """Test that comment lines are ignored"""
        emails_file = tmp_path / "email_addresses.txt"
        emails_file.write_text("""
# This is a comment
john.doe@example.com
# Another comment
jane.smith@company.com
""")

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = GmailExtractor()
            extractor.load_email_addresses()

            assert len(extractor.email_addresses) == 2
            assert not any(email.startswith('#') for email in extractor.email_addresses)
        finally:
            os.chdir(original_dir)

    def test_empty_lines_ignored(self, tmp_path):
        """Test that empty lines are ignored"""
        emails_file = tmp_path / "email_addresses.txt"
        emails_file.write_text("""

john.doe@example.com


jane.smith@company.com

""")

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = GmailExtractor()
            extractor.load_email_addresses()

            assert len(extractor.email_addresses) == 2
        finally:
            os.chdir(original_dir)

    def test_whitespace_stripped(self, tmp_path):
        """Test that whitespace is stripped from email addresses"""
        emails_file = tmp_path / "email_addresses.txt"
        emails_file.write_text("""
  john.doe@example.com
	jane.smith@company.com
""")

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            extractor = GmailExtractor()
            extractor.load_email_addresses()

            assert len(extractor.email_addresses) == 2
            assert all(email == email.strip() for email in extractor.email_addresses)
        finally:
            os.chdir(original_dir)


class TestGmailExtractor:
    """Test GmailExtractor class methods"""

    def test_build_query(self):
        """Test Gmail search query building"""
        extractor = GmailExtractor()
        query = extractor.build_query("test@example.com")

        assert "from:test@example.com" in query
        assert "to:test@example.com" in query
        assert "cc:test@example.com" in query
        assert " OR " in query

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        extractor = GmailExtractor()

        # Test invalid characters are replaced
        result = extractor.sanitize_filename('test<>:"/\\|?*file.txt')
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert '"' not in result
        assert '/' not in result
        assert '\\' not in result
        assert '|' not in result
        assert '?' not in result
        assert '*' not in result

        # Test normal characters are preserved
        result = extractor.sanitize_filename('normal_filename-123.txt')
        assert result == 'normal_filename-123.txt'

        # Test length limit
        long_name = 'a' * 300
        result = extractor.sanitize_filename(long_name)
        assert len(result) <= 200

    def test_get_header(self):
        """Test email header extraction"""
        extractor = GmailExtractor()

        headers = [
            {'name': 'Subject', 'value': 'Test Subject'},
            {'name': 'From', 'value': 'sender@example.com'},
            {'name': 'To', 'value': 'recipient@example.com'},
        ]

        assert extractor.get_header(headers, 'Subject') == 'Test Subject'
        assert extractor.get_header(headers, 'From') == 'sender@example.com'
        assert extractor.get_header(headers, 'To') == 'recipient@example.com'
        assert extractor.get_header(headers, 'Nonexistent') == ''

        # Test case-insensitive header names
        assert extractor.get_header(headers, 'subject') == 'Test Subject'
        assert extractor.get_header(headers, 'SUBJECT') == 'Test Subject'


class TestAuthenticationStatus:
    """Test authentication status checking"""

    def test_no_files_exist(self, tmp_path):
        """Test status when no credentials or token exist"""
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            status = check_authentication_status()

            assert status['has_credentials'] is False
            assert status['has_token'] is False
            assert status['credentials_valid'] is False
            assert status['token_valid'] is False
            assert status['authenticated'] is False
        finally:
            os.chdir(original_dir)

    def test_valid_credentials_exist(self, tmp_path):
        """Test status when valid credentials exist"""
        valid_creds = {
            "installed": {
                "client_id": "test.apps.googleusercontent.com",
                "client_secret": "secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        creds_file = tmp_path / "credentials.json"
        creds_file.write_text(json.dumps(valid_creds))

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            status = check_authentication_status()

            assert status['has_credentials'] is True
            assert status['credentials_valid'] is True
        finally:
            os.chdir(original_dir)


class TestFilenameEdgeCases:
    """Test edge cases in filename handling"""

    def test_unicode_in_filename(self):
        """Test handling of unicode characters in filenames"""
        extractor = GmailExtractor()

        # Unicode characters should be preserved
        result = extractor.sanitize_filename('test_文件_😀.txt')
        # Should not crash and should return something
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_filename(self):
        """Test handling of empty filename"""
        extractor = GmailExtractor()
        result = extractor.sanitize_filename('')
        assert result == ''

    def test_only_invalid_chars(self):
        """Test filename with only invalid characters"""
        extractor = GmailExtractor()
        result = extractor.sanitize_filename('<>:"/\\|?*')
        # Should replace all with underscores
        assert result == '_________'


class TestAttachmentExtraction:
    """Test attachment extraction functionality"""

    def test_extract_attachment_with_attachment_id(self, tmp_path):
        """Test extracting attachment using attachmentId"""
        import base64

        extractor = GmailExtractor()

        # Mock Gmail service
        mock_service = MagicMock()
        extractor.service = mock_service

        # Mock attachment data
        test_data = b"Test file content"
        encoded_data = base64.urlsafe_b64encode(test_data).decode('utf-8')

        # Setup mock to return attachment
        mock_service.users().messages().attachments().get().execute.return_value = {
            'data': encoded_data
        }

        # Create test message with attachment
        message = {
            'id': 'test_msg_123',
            'payload': {
                'parts': [
                    {
                        'filename': 'test.pdf',
                        'mimeType': 'application/pdf',
                        'body': {
                            'attachmentId': 'att_123',
                            'size': len(test_data)
                        }
                    }
                ]
            }
        }

        # Create attachments directory
        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir()

        # Extract attachments
        result = extractor.extract_attachments(message, attachments_dir)

        # Verify
        assert len(result) == 1
        assert result[0] == 'test.pdf'
        assert (attachments_dir / 'test.pdf').exists()
        assert (attachments_dir / 'test.pdf').read_bytes() == test_data

    def test_extract_inline_attachment(self, tmp_path):
        """Test extracting inline attachment (no attachmentId)"""
        import base64

        extractor = GmailExtractor()
        extractor.service = MagicMock()

        # Mock attachment data
        test_data = b"Inline image content"
        encoded_data = base64.urlsafe_b64encode(test_data).decode('utf-8')

        # Create test message with inline attachment
        message = {
            'id': 'test_msg_456',
            'payload': {
                'parts': [
                    {
                        'filename': 'image.png',
                        'mimeType': 'image/png',
                        'body': {
                            'data': encoded_data,
                            'size': len(test_data)
                        }
                    }
                ]
            }
        }

        # Create attachments directory
        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir()

        # Extract attachments
        result = extractor.extract_attachments(message, attachments_dir)

        # Verify
        assert len(result) == 1
        assert result[0] == 'image.png'
        assert (attachments_dir / 'image.png').exists()
        assert (attachments_dir / 'image.png').read_bytes() == test_data

    def test_sanitize_attachment_filename(self, tmp_path):
        """Test that attachment filenames are sanitized"""
        import base64

        extractor = GmailExtractor()
        extractor.service = MagicMock()

        test_data = b"Test content"
        encoded_data = base64.urlsafe_b64encode(test_data).decode('utf-8')

        # Create message with invalid filename characters
        message = {
            'id': 'test_msg_789',
            'payload': {
                'parts': [
                    {
                        'filename': 'test:file<name>.pdf',
                        'body': {
                            'data': encoded_data
                        }
                    }
                ]
            }
        }

        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir()

        result = extractor.extract_attachments(message, attachments_dir)

        # Filename should be sanitized
        assert len(result) == 1
        assert ':' not in result[0]
        assert '<' not in result[0]
        assert '>' not in result[0]

    def test_duplicate_attachment_filenames(self, tmp_path):
        """Test handling of duplicate attachment filenames"""
        import base64

        extractor = GmailExtractor()
        extractor.service = MagicMock()

        test_data1 = b"First file"
        test_data2 = b"Second file"
        encoded_data1 = base64.urlsafe_b64encode(test_data1).decode('utf-8')
        encoded_data2 = base64.urlsafe_b64encode(test_data2).decode('utf-8')

        # Create message with two attachments with same name
        message = {
            'id': 'test_msg_dup',
            'payload': {
                'parts': [
                    {
                        'filename': 'document.pdf',
                        'body': {'data': encoded_data1}
                    },
                    {
                        'filename': 'document.pdf',
                        'body': {'data': encoded_data2}
                    }
                ]
            }
        }

        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir()

        result = extractor.extract_attachments(message, attachments_dir)

        # Should have two different filenames
        assert len(result) == 2
        assert 'document.pdf' in result
        assert 'document_1.pdf' in result

    def test_nested_multipart_attachments(self, tmp_path):
        """Test extracting attachments from nested multipart messages"""
        import base64

        extractor = GmailExtractor()
        extractor.service = MagicMock()

        test_data = b"Nested attachment"
        encoded_data = base64.urlsafe_b64encode(test_data).decode('utf-8')

        # Create message with nested parts
        message = {
            'id': 'test_msg_nested',
            'payload': {
                'parts': [
                    {
                        'mimeType': 'multipart/alternative',
                        'parts': [
                            {
                                'filename': 'nested.txt',
                                'body': {'data': encoded_data}
                            }
                        ]
                    }
                ]
            }
        }

        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir()

        result = extractor.extract_attachments(message, attachments_dir)

        # Should find nested attachment
        assert len(result) == 1
        assert result[0] == 'nested.txt'
        assert (attachments_dir / 'nested.txt').read_bytes() == test_data

    def test_no_attachments(self, tmp_path):
        """Test message with no attachments returns empty list"""
        extractor = GmailExtractor()
        extractor.service = MagicMock()

        # Message with only text content, no attachments
        message = {
            'id': 'test_msg_no_att',
            'payload': {
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {'data': 'SGVsbG8gV29ybGQ='}
                    }
                ]
            }
        }

        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir()

        result = extractor.extract_attachments(message, attachments_dir)

        # Should return empty list
        assert len(result) == 0


# Fixtures for pytest
@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service"""
    service = MagicMock()
    return service


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
