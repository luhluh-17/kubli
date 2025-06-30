import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from cryptography.fernet import Fernet
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.encryption import (
    generate_key_from_password,
    encrypt_filename,
    encrypt_file,
    encrypt_directory
)


class TestEncryption:
    """Test cases for encryption module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_password = "test_password_123"
        self.test_key = generate_key_from_password(self.test_password)
        self.test_filename = "test_file.txt"
        self.test_content = b"This is test content for encryption."

    def test_generate_key_from_password(self):
        """Test key generation from password."""
        key1 = generate_key_from_password(self.test_password)
        key2 = generate_key_from_password(self.test_password)
        
        # Same password should generate same key
        assert key1 == key2
        
        # Key should be valid for Fernet
        fernet = Fernet(key1)
        assert fernet is not None
        
        # Different passwords should generate different keys
        different_key = generate_key_from_password("different_password")
        assert key1 != different_key

    def test_encrypt_filename(self):
        """Test filename encryption."""
        encrypted_filename = encrypt_filename(self.test_filename, self.test_key)
        
        # Should return a string
        assert isinstance(encrypted_filename, str)
        
        # Should not be the same as original
        assert encrypted_filename != self.test_filename
        
        # Should not contain '=' characters (replaced with '_')
        assert '=' not in encrypted_filename
        
        # Should be a valid base64-like string (letters, numbers, underscores)
        import string
        valid_chars = string.ascii_letters + string.digits + '_-'
        assert all(c in valid_chars for c in encrypted_filename)

    def test_encrypt_filename_with_invalid_key(self):
        """Test filename encryption with invalid key."""
        invalid_key = b"invalid_key"
        result = encrypt_filename(self.test_filename, invalid_key)
        assert result is None

    def test_encrypt_file(self):
        """Test file encryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file_path = os.path.join(temp_dir, self.test_filename)
            with open(test_file_path, 'wb') as f:
                f.write(self.test_content)
            
            # Encrypt the file
            result = encrypt_file(test_file_path, self.test_key)
            assert result is True
            
            # Check that encrypted file was created
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            assert len(encrypted_files) == 1
            
            # Verify encrypted file has content
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            assert os.path.getsize(encrypted_file_path) > 0
            
            # Verify encrypted content is different from original
            with open(encrypted_file_path, 'rb') as f:
                encrypted_content = f.read()
            assert encrypted_content != self.test_content

    def test_encrypt_file_nonexistent(self):
        """Test encrypting a non-existent file."""
        result = encrypt_file("/nonexistent/file.txt", self.test_key)
        assert result is False

    @patch('builtins.input')
    @patch('glob.glob')
    @patch('os.getcwd')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_encrypt_directory_empty_password(self, mock_isfile, mock_exists, mock_getcwd, mock_glob, mock_input):
        """Test encrypt_directory with empty password."""
        mock_input.return_value = ""  # Empty password
        
        # Capture the function call - it should return early due to empty password
        with patch('builtins.print') as mock_print:
            encrypt_directory()
            # Should print error message about empty key
            mock_print.assert_any_call('\x1b[31mError: Encryption key cannot be empty!')

    @patch('builtins.input')
    @patch('os.path.exists')
    def test_encrypt_directory_nonexistent_directory(self, mock_exists, mock_input):
        """Test encrypt_directory with non-existent directory."""
        mock_input.side_effect = ["test_password", "/nonexistent/directory"]
        mock_exists.return_value = False
        
        with patch('builtins.print') as mock_print:
            encrypt_directory()
            # Should print error message about directory not existing
            mock_print.assert_any_call('\x1b[31mError: Directory \'/nonexistent/directory\' does not exist!')

    @patch('builtins.input')
    @patch('glob.glob')
    @patch('os.getcwd')
    @patch('os.path.exists')
    def test_encrypt_directory_no_files(self, mock_exists, mock_getcwd, mock_glob, mock_input):
        """Test encrypt_directory with no files to encrypt."""
        mock_input.side_effect = ["test_password", ""]  # Use current directory
        mock_exists.return_value = True
        mock_getcwd.return_value = "/test/directory"
        mock_glob.return_value = []  # No files found
        
        with patch('builtins.print') as mock_print:
            encrypt_directory()
            # Should print message about no files found
            mock_print.assert_any_call('\x1b[33mNo files found to encrypt!')

    @patch('builtins.input')
    @patch('glob.glob')
    @patch('os.getcwd')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.basename')
    def test_encrypt_directory_user_cancels(self, mock_basename, mock_isfile, mock_exists, mock_getcwd, mock_glob, mock_input):
        """Test encrypt_directory when user cancels operation."""
        mock_input.side_effect = ["test_password", "", "n"]  # Cancel operation
        mock_exists.return_value = True
        mock_getcwd.return_value = "/test/directory"
        mock_glob.return_value = ["/test/directory/file1.txt"]
        mock_isfile.return_value = True
        mock_basename.return_value = "file1.txt"
        
        with patch('builtins.print') as mock_print:
            encrypt_directory()
            # Should print cancellation message
            mock_print.assert_any_call('\x1b[33mEncryption cancelled.')

    def test_encrypt_file_integration(self):
        """Integration test for file encryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple test files
            test_files = ["file1.txt", "file2.doc", "file3.pdf"]
            for filename in test_files:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(f"Content of {filename}")
            
            # Encrypt each file
            for filename in test_files:
                file_path = os.path.join(temp_dir, filename)
                result = encrypt_file(file_path, self.test_key)
                assert result is True
            
            # Verify encrypted files exist
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            assert len(encrypted_files) == len(test_files)


if __name__ == '__main__':
    pytest.main([__file__])
