import pytest
import os
import sys
from unittest.mock import patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.decryption import decrypt_file
from utils.encryption import generate_key_from_password


class TestSampleFiles:
    """Test cases for sample encrypted files in the project."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_dir = os.path.join(os.path.dirname(__file__), '..', 'sample')
        
    def test_sample_directory_exists(self):
        """Test that the sample directory exists."""
        assert os.path.exists(self.sample_dir)
        assert os.path.isdir(self.sample_dir)
    
    def test_sample_files_exist(self):
        """Test that sample encrypted files exist."""
        sample_files = [f for f in os.listdir(self.sample_dir) if f.endswith('.kubli')]
        assert len(sample_files) > 0, "No sample .kubli files found"
        
        # Verify each sample file exists and has content
        for sample_file in sample_files:
            file_path = os.path.join(self.sample_dir, sample_file)
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0, f"Sample file {sample_file} is empty"
    
    def test_sample_filenames_format(self):
        """Test that sample filenames follow expected encrypted format."""
        sample_files = [f for f in os.listdir(self.sample_dir) if f.endswith('.kubli')]
        
        for sample_file in sample_files:
            # Remove .kubli extension to get encrypted filename
            encrypted_name = sample_file.replace('.kubli', '')
            
            # Should be base64-like (letters, numbers, underscores, hyphens)
            allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-')
            filename_chars = set(encrypted_name)
            assert filename_chars.issubset(allowed_chars), f"Invalid characters in {sample_file}"
    
    def test_sample_files_are_encrypted(self):
        """Test that sample files appear to be properly encrypted."""
        sample_files = [f for f in os.listdir(self.sample_dir) if f.endswith('.kubli')]
        
        for sample_file in sample_files:
            file_path = os.path.join(self.sample_dir, sample_file)
            
            # Read the file content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Encrypted content should not contain obvious plain text patterns
            # Check that it doesn't start with common file headers
            plain_text_headers = [
                b'<!DOCTYPE',  # HTML
                b'<html',      # HTML
                b'<?xml',      # XML
                b'%PDF',       # PDF
                b'\x89PNG',    # PNG
                b'\xff\xd8',   # JPEG
                b'PK',         # ZIP
            ]
            
            for header in plain_text_headers:
                assert not content.startswith(header), f"File {sample_file} appears to contain plain text"
    
    @pytest.mark.parametrize("test_password", [
        "wrong_password",
        "test123",
        "admin",
        "password",
        "",
    ])
    def test_sample_files_decrypt_with_wrong_passwords(self, test_password):
        """Test that sample files cannot be decrypted with common wrong passwords."""
        sample_files = [f for f in os.listdir(self.sample_dir) if f.endswith('.kubli')]
        
        if not sample_files:
            pytest.skip("No sample files to test")
        
        # Test with the first sample file
        sample_file = sample_files[0]
        file_path = os.path.join(self.sample_dir, sample_file)
        
        # Generate key from test password
        test_key = generate_key_from_password(test_password)
        
        # Should fail to decrypt
        result = decrypt_file(file_path, test_key)
        assert result is False, f"Sample file was unexpectedly decrypted with password: {test_password}"
    
    def test_sample_file_structure_integrity(self):
        """Test the structural integrity of sample files."""
        sample_files = [f for f in os.listdir(self.sample_dir) if f.endswith('.kubli')]
        
        for sample_file in sample_files:
            file_path = os.path.join(self.sample_dir, sample_file)
            
            # File should be readable
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                assert len(content) > 0
            except Exception as e:
                pytest.fail(f"Could not read sample file {sample_file}: {e}")


if __name__ == '__main__':
    pytest.main([__file__])
