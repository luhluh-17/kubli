# Kubli Test Suite

This directory contains comprehensive test scripts for the Kubli encryption/decryption application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_encryption.py          # Unit tests for encryption module
├── test_decryption.py          # Unit tests for decryption module
├── test_integration.py         # End-to-end integration tests
├── test_sample_files.py        # Tests for sample encrypted files
└── README.md                   # This file
```

## Test Categories

### 1. Unit Tests (`test_encryption.py`, `test_decryption.py`)
- Test individual functions in isolation
- Mock external dependencies
- Fast execution
- High coverage of edge cases

**Encryption Tests:**
- Key generation from password
- Filename encryption/decryption
- File encryption with various scenarios
- Error handling for invalid inputs
- Directory encryption workflow

**Decryption Tests:**
- Filename decryption
- File decryption with correct/incorrect keys
- Directory decryption workflow
- Error handling and validation

### 2. Integration Tests (`test_integration.py`)
- Test complete workflows end-to-end
- Real file system operations
- Multi-file scenarios
- Performance with larger files

**Integration Scenarios:**
- Full encryption-decryption roundtrip
- Multiple file handling
- Wrong password scenarios
- Empty file handling
- Large file processing
- Special characters in filenames

### 3. Sample File Tests (`test_sample_files.py`)
- Validate sample encrypted files
- Ensure files are properly encrypted
- Test against common wrong passwords
- Verify file structure integrity

## Running Tests

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
```

### Quick Start
```bash
# Run all tests
python run_tests.py

# Or use the Makefile
make test
```

### Specific Test Categories
```bash
# Unit tests only
python run_tests.py --unit
make test-unit

# Integration tests only
python run_tests.py --integration
make test-integration

# Sample file tests only
python run_tests.py --file test_sample_files
make test-samples

# Specific test file
python run_tests.py --file test_encryption
```

### Coverage Reports
```bash
# Run with coverage
python run_tests.py
make coverage

# View HTML coverage report
open coverage_html/index.html
```

### Advanced Options
```bash
# Verbose output
python run_tests.py --verbose

# Skip coverage reporting
python run_tests.py --no-coverage

# Run specific test method
python -m pytest tests/test_encryption.py::TestEncryption::test_generate_key_from_password -v
```

## Test Configuration

### pytest.ini
Configuration file for pytest with:
- Test discovery patterns
- Coverage settings
- Output formatting
- Warning filters

### Coverage Settings
- Minimum coverage threshold: 80%
- HTML reports generated in `coverage_html/`
- Terminal output with missing lines
- Covers `utils/` and `kubli.py` modules

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
import pytest
import tempfile
import os
from unittest.mock import patch

class TestMyFeature:
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.test_data = "example"
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function(self.test_data)
        
        # Assert
        assert actual == expected
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies."""
        mock_dependency.return_value = "mocked"
        result = my_function()
        assert result == "expected"
```

### Best Practices
1. **Isolation**: Each test should be independent
2. **Arrange-Act-Assert**: Clear test structure
3. **Descriptive Names**: Test names should describe what is being tested
4. **Edge Cases**: Test boundary conditions and error scenarios
5. **Mocking**: Mock external dependencies for unit tests
6. **Temporary Files**: Use `tempfile` for file system tests
7. **Cleanup**: Tests should clean up after themselves

## Continuous Integration

### GitHub Actions (Example)
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: python run_tests.py
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd /path/to/kubli
   python run_tests.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Permission Errors**
   ```bash
   # Make test runner executable
   chmod +x run_tests.py
   ```

4. **Coverage Not Working**
   ```bash
   # Install coverage plugin
   pip install pytest-cov
   ```

### Debug Mode
```bash
# Run with maximum verbosity
python -m pytest tests/ -vvv --tb=long

# Run specific test with debugging
python -m pytest tests/test_encryption.py::TestEncryption::test_encrypt_file -vvv --pdb
```

## Performance Testing

### Timing Tests
```python
import time

def test_performance():
    start_time = time.time()
    # Your test code here
    end_time = time.time()
    
    execution_time = end_time - start_time
    assert execution_time < 1.0  # Should complete in under 1 second
```

### Memory Usage
```python
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Your test code here
    
    final_memory = process.memory_info().rss
    memory_used = final_memory - initial_memory
    
    # Should not use more than 10MB
    assert memory_used < 10 * 1024 * 1024
```

## Test Data Management

### Using Fixtures
```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        'password': 'test_password',
        'content': b'test content',
        'filename': 'test.txt'
    }

def test_with_fixture(sample_data):
    """Test using fixture data."""
    assert sample_data['password'] == 'test_password'
```

### Temporary Files
```python
def test_with_temp_files():
    """Test with temporary files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Your test code here
        
        # Files are automatically cleaned up
```

## Reporting Issues

If you find bugs or have suggestions for improving the tests:

1. Check existing issues in the project repository
2. Create a new issue with:
   - Test output/error messages
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)

## Contributing

When contributing new tests:

1. Follow the existing test patterns
2. Add appropriate documentation
3. Ensure all tests pass
4. Maintain or improve coverage
5. Update this README if needed
