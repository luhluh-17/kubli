import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.decryption import (
    decrypt_filename,
    decrypt_file,
    decrypt_directory
)
from utils.encryption import generate_key_from_password, encrypt_filename, encrypt_file


class TestDecryption:
    """Test cases for decryption module."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_password = "test_password_123"
        self.test_key = generate_key_from_password(self.test_password)
        self.test_filename = "test_file.txt"
        self.test_content = b"This is test content for decryption."

    def test_decrypt_filename(self):
        """Test filename decryption."""
        # First encrypt a filename
        encrypted_filename = encrypt_filename(self.test_filename, self.test_key)
        assert encrypted_filename is not None
        
        # Then decrypt it
        decrypted_filename = decrypt_filename(encrypted_filename, self.test_key)
        
        # Should return the original filename
        assert decrypted_filename == self.test_filename

    def test_decrypt_filename_with_invalid_key(self):
        """Test filename decryption with invalid key."""
        # First encrypt a filename with correct key
        encrypted_filename = encrypt_filename(self.test_filename, self.test_key)
        assert encrypted_filename is not None
        
        # Try to decrypt with wrong key
        wrong_key = generate_key_from_password("wrong_password")
        result = decrypt_filename(encrypted_filename, wrong_key)
        assert result is None

    def test_decrypt_filename_with_invalid_data(self):
        """Test filename decryption with invalid encrypted data."""
        invalid_encrypted_filename = "invalid_encrypted_data"
        result = decrypt_filename(invalid_encrypted_filename, self.test_key)
        assert result is None

    def test_decrypt_file(self):
        """Test file decryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and encrypt a test file
            test_file_path = os.path.join(temp_dir, self.test_filename)
            with open(test_file_path, 'wb') as f:
                f.write(self.test_content)
            
            # Encrypt the file
            encrypt_result = encrypt_file(test_file_path, self.test_key)
            assert encrypt_result is True
            
            # Find the encrypted file
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            assert len(encrypted_files) == 1
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            
            # Remove original file to test decryption
            os.remove(test_file_path)
            
            # Decrypt the file
            decrypt_result = decrypt_file(encrypted_file_path, self.test_key)
            assert decrypt_result is True
            
            # Verify the decrypted file exists and has correct content
            assert os.path.exists(test_file_path)
            with open(test_file_path, 'rb') as f:
                decrypted_content = f.read()
            assert decrypted_content == self.test_content

    def test_decrypt_file_with_wrong_key(self):
        """Test file decryption with wrong key."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and encrypt a test file
            test_file_path = os.path.join(temp_dir, self.test_filename)
            with open(test_file_path, 'wb') as f:
                f.write(self.test_content)
            
            encrypt_result = encrypt_file(test_file_path, self.test_key)
            assert encrypt_result is True
            
            # Find the encrypted file
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            
            # Try to decrypt with wrong key
            wrong_key = generate_key_from_password("wrong_password")
            decrypt_result = decrypt_file(encrypted_file_path, wrong_key)
            assert decrypt_result is False

    def test_decrypt_file_nonexistent(self):
        """Test decrypting a non-existent file."""
        result = decrypt_file("/nonexistent/file.kubli", self.test_key)
        assert result is False

    @patch('builtins.input')
    @patch('glob.glob')
    @patch('os.getcwd')
    @patch('os.path.exists')
    def test_decrypt_directory_empty_password(self, mock_exists, mock_getcwd, mock_glob, mock_input):
        """Test decrypt_directory with empty password."""
        mock_input.return_value = ""  # Empty password
        
        with patch('builtins.print') as mock_print:
            decrypt_directory()
            # Should print error message about empty key
            mock_print.assert_any_call('\x1b[31mError: Decryption key cannot be empty!')

    @patch('builtins.input')
    @patch('os.path.exists')
    def test_decrypt_directory_nonexistent_directory(self, mock_exists, mock_input):
        """Test decrypt_directory with non-existent directory."""
        mock_input.side_effect = ["test_password", "/nonexistent/directory"]
        mock_exists.return_value = False
        
        with patch('builtins.print') as mock_print:
            decrypt_directory()
            # Should print error message about directory not existing
            mock_print.assert_any_call('\x1b[31mError: Directory \'/nonexistent/directory\' does not exist!')

    @patch('builtins.input')
    @patch('glob.glob')
    @patch('os.getcwd')
    @patch('os.path.exists')
    def test_decrypt_directory_no_files(self, mock_exists, mock_getcwd, mock_glob, mock_input):
        """Test decrypt_directory with no encrypted files."""
        mock_input.side_effect = ["test_password", ""]  # Use current directory
        mock_exists.return_value = True
        mock_getcwd.return_value = "/test/directory"
        mock_glob.return_value = []  # No .kubli files found
        
        with patch('builtins.print') as mock_print:
            decrypt_directory()
            # Should print message about no encrypted files found
            mock_print.assert_any_call('\x1b[33mNo encrypted files found!')

    @patch('builtins.input')
    @patch('glob.glob')
    @patch('os.getcwd')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_decrypt_directory_user_cancels(self, mock_basename, mock_exists, mock_getcwd, mock_glob, mock_input):
        """Test decrypt_directory when user cancels operation."""
        mock_input.side_effect = ["test_password", "", "n"]  # Cancel operation
        mock_exists.return_value = True
        mock_getcwd.return_value = "/test/directory"
        mock_glob.return_value = ["/test/directory/file1.kubli"]
        mock_basename.return_value = "file1.kubli"
        
        # Mock decrypt_filename to return a valid filename for display
        with patch('utils.decryption.decrypt_filename', return_value="file1.txt"):
            with patch('builtins.print') as mock_print:
                decrypt_directory()
                # Should print cancellation message
                mock_print.assert_any_call('\x1b[33mDecryption cancelled.')

    def test_encrypt_decrypt_roundtrip(self):
        """Integration test for encrypt-decrypt roundtrip."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file_path = os.path.join(temp_dir, self.test_filename)
            with open(test_file_path, 'wb') as f:
                f.write(self.test_content)
            
            # Encrypt the file
            encrypt_result = encrypt_file(test_file_path, self.test_key)
            assert encrypt_result is True
            
            # Remove original file
            os.remove(test_file_path)
            
            # Find and decrypt the encrypted file
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            assert len(encrypted_files) == 1
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            
            decrypt_result = decrypt_file(encrypted_file_path, self.test_key)
            assert decrypt_result is True
            
            # Verify the roundtrip worked
            assert os.path.exists(test_file_path)
            with open(test_file_path, 'rb') as f:
                final_content = f.read()
            assert final_content == self.test_content

    def test_multiple_files_decrypt(self):
        """Test decrypting multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and encrypt multiple test files
            test_files = ["file1.txt", "file2.doc", "file3.pdf"]
            file_contents = {}
            
            for filename in test_files:
                content = f"Content of {filename}".encode()
                file_contents[filename] = content
                file_path = os.path.join(temp_dir, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Encrypt the file
                encrypt_result = encrypt_file(file_path, self.test_key)
                assert encrypt_result is True
                
                # Remove original
                os.remove(file_path)
            
            # Decrypt all files
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            assert len(encrypted_files) == len(test_files)
            
            for encrypted_file in encrypted_files:
                encrypted_file_path = os.path.join(temp_dir, encrypted_file)
                decrypt_result = decrypt_file(encrypted_file_path, self.test_key)
                assert decrypt_result is True
            
            # Verify all files were decrypted correctly
            for filename, expected_content in file_contents.items():
                file_path = os.path.join(temp_dir, filename)
                assert os.path.exists(file_path)
                with open(file_path, 'rb') as f:
                    actual_content = f.read()
                assert actual_content == expected_content


if __name__ == '__main__':
    pytest.main([__file__])
