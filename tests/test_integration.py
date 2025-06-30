import pytest
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import kubli
from utils.encryption import generate_key_from_password, encrypt_file
from utils.decryption import decrypt_file


class TestKubliMain:
    """Integration tests for the main Kubli application."""

    def test_display_banner(self):
        """Test that the banner displays correctly."""
        with patch('builtins.print') as mock_print:
            kubli.display_banner()
            
            # Check that print was called multiple times (for the banner)
            assert mock_print.call_count > 10
            
            # Check that version, author, and GitHub info are displayed
            calls = [str(call) for call in mock_print.call_args_list]
            banner_text = ' '.join(calls)
            
            assert 'v0.1.0' in banner_text
            assert 'Ralph Joseph Castro' in banner_text
            assert 'https://github.com/luhluh-17' in banner_text
            assert 'kubli' in banner_text.lower()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_exit(self, mock_print, mock_input):
        """Test main menu exit option."""
        mock_input.return_value = "3"  # Exit option
        
        kubli.main_menu()
        
        # Should print goodbye messages
        mock_print.assert_any_call('\n\x1b[32mThank you for using Kubli!')
        mock_print.assert_any_call('\x1b[32mGoodbye!')

    @patch('kubli.encrypt_directory')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_encrypt_option(self, mock_print, mock_input, mock_encrypt):
        """Test main menu encrypt option."""
        mock_input.side_effect = ["1", "3"]  # Select encrypt, then exit
        
        kubli.main_menu()
        
        # Should call encrypt_directory
        mock_encrypt.assert_called_once()

    @patch('kubli.decrypt_directory')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_decrypt_option(self, mock_print, mock_input, mock_decrypt):
        """Test main menu decrypt option."""
        mock_input.side_effect = ["2", "3"]  # Select decrypt, then exit
        
        kubli.main_menu()
        
        # Should call decrypt_directory
        mock_decrypt.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_invalid_option(self, mock_print, mock_input):
        """Test main menu with invalid option."""
        mock_input.side_effect = ["invalid", "3"]  # Invalid option, then exit
        
        kubli.main_menu()
        
        # Should print error message
        mock_print.assert_any_call('\n\x1b[31mInvalid option! Please select a number specified in the menu.')

    @patch('kubli.display_banner')
    @patch('kubli.main_menu')
    def test_main_function(self, mock_main_menu, mock_display_banner):
        """Test the main function."""
        kubli.main()
        
        # Should call both banner and main menu
        mock_display_banner.assert_called_once()
        mock_main_menu.assert_called_once()


class TestKubliIntegration:
    """End-to-end integration tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_password = "integration_test_password"
        self.test_key = generate_key_from_password(self.test_password)

    def test_full_encryption_decryption_workflow(self):
        """Test complete workflow from file creation to encryption to decryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = {
                "document.txt": b"This is a test document.",
                "image.jpg": b"Fake image data",
                "data.csv": b"name,age\nJohn,30\nJane,25"
            }
            
            file_paths = []
            for filename, content in test_files.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(content)
                file_paths.append(file_path)
            
            # Encrypt all files
            for file_path in file_paths:
                result = encrypt_file(file_path, self.test_key)
                assert result is True
            
            # Remove original files
            for file_path in file_paths:
                os.remove(file_path)
            
            # Verify encrypted files exist
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            assert len(encrypted_files) == len(test_files)
            
            # Decrypt all files
            for encrypted_file in encrypted_files:
                encrypted_file_path = os.path.join(temp_dir, encrypted_file)
                result = decrypt_file(encrypted_file_path, self.test_key)
                assert result is True
            
            # Verify all original files are restored with correct content
            for filename, expected_content in test_files.items():
                file_path = os.path.join(temp_dir, filename)
                assert os.path.exists(file_path)
                with open(file_path, 'rb') as f:
                    actual_content = f.read()
                assert actual_content == expected_content

    def test_wrong_password_decryption(self):
        """Test that wrong password fails decryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and encrypt a file
            test_file = os.path.join(temp_dir, "secret.txt")
            test_content = b"Secret information"
            
            with open(test_file, 'wb') as f:
                f.write(test_content)
            
            # Encrypt with correct password
            correct_key = generate_key_from_password("correct_password")
            result = encrypt_file(test_file, correct_key)
            assert result is True
            
            # Try to decrypt with wrong password
            wrong_key = generate_key_from_password("wrong_password")
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            
            result = decrypt_file(encrypted_file_path, wrong_key)
            assert result is False

    def test_empty_file_encryption_decryption(self):
        """Test encryption and decryption of empty files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty file
            empty_file = os.path.join(temp_dir, "empty.txt")
            with open(empty_file, 'wb') as f:
                pass  # Create empty file
            
            # Encrypt empty file
            result = encrypt_file(empty_file, self.test_key)
            assert result is True
            
            # Remove original
            os.remove(empty_file)
            
            # Decrypt
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            result = decrypt_file(encrypted_file_path, self.test_key)
            assert result is True
            
            # Verify empty file is restored
            assert os.path.exists(empty_file)
            assert os.path.getsize(empty_file) == 0

    def test_large_file_encryption_decryption(self):
        """Test encryption and decryption of a larger file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a larger test file (1MB)
            large_file = os.path.join(temp_dir, "large_file.bin")
            large_content = b"X" * (1024 * 1024)  # 1MB of 'X' characters
            
            with open(large_file, 'wb') as f:
                f.write(large_content)
            
            # Encrypt
            result = encrypt_file(large_file, self.test_key)
            assert result is True
            
            # Remove original
            os.remove(large_file)
            
            # Decrypt
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            result = decrypt_file(encrypted_file_path, self.test_key)
            assert result is True
            
            # Verify content
            assert os.path.exists(large_file)
            with open(large_file, 'rb') as f:
                decrypted_content = f.read()
            assert decrypted_content == large_content

    def test_special_characters_in_filename(self):
        """Test encryption/decryption with special characters in filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with special characters in name
            special_filename = "test file with spaces & symbols!@#.txt"
            special_file = os.path.join(temp_dir, special_filename)
            test_content = b"Content with special filename"
            
            with open(special_file, 'wb') as f:
                f.write(test_content)
            
            # Encrypt
            result = encrypt_file(special_file, self.test_key)
            assert result is True
            
            # Remove original
            os.remove(special_file)
            
            # Decrypt
            encrypted_files = [f for f in os.listdir(temp_dir) if f.endswith('.kubli')]
            encrypted_file_path = os.path.join(temp_dir, encrypted_files[0])
            result = decrypt_file(encrypted_file_path, self.test_key)
            assert result is True
            
            # Verify restoration
            assert os.path.exists(special_file)
            with open(special_file, 'rb') as f:
                decrypted_content = f.read()
            assert decrypted_content == test_content


if __name__ == '__main__':
    pytest.main([__file__])
