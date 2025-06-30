# Kubli - File Encryption Tool

**Kubli** (Tagalog for "hidden", "concealed", or "secret") is a Python-based file encryption tool
that provides secure encryption and decryption of files and directories using Fernet symmetric
encryption.

## Example

##![kubli](https://github.com/user-attachments/assets/5221b06e-7b8e-4dbf-823c-e7e316144d80)

 Features

- **Directory-wide encryption/decryption** - Process multiple files at once
- **Filename encryption** - Both file content and filenames are encrypted
- **Interactive interface** - User-friendly command-line menu system
- **Password-based encryption** - Uses SHA-256 derived keys from user passwords
- **Preview functionality** - Shows encrypted/decrypted filename mappings before processing
- **Optional file deletion** - Choose to delete original files after encryption/decryption

## Installation

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Dependencies

Install required packages:

```bash
pip install cryptography colorama
```

### Download

Clone the repository or download the script:

```bash
git clone https://github.com/luhluh-17/kubli.git
cd kubli
```

## Usage

Run the application:

```bash
python kubli.py
```

### Main Menu Options

1. **Encrypt** - Encrypt files in a directory
2. **Decrypt** - Decrypt .kubli files in a directory
3. **Exit** - Close the application

### Encryption Process

1. Enter your encryption password
2. Specify directory path (or press Enter for current directory)
3. Review the list of files to be encrypted
4. Confirm to proceed with encryption
5. Choose whether to delete original files after encryption

### Decryption Process

1. Enter your decryption password
2. Specify directory path (or press Enter for current directory)
3. Review encrypted files with their decrypted filename previews
4. Confirm to proceed with decryption
5. Choose whether to delete encrypted files after decryption

## File Filtering

### Encryption

- Excludes files with `.kubli` extension (already encrypted)
- Excludes the kubli.py script itself
- Only processes regular files (not directories)

### Decryption

- Only processes files with `.kubli` extension
- Attempts to decrypt filenames for preview display

## Security Features

- **Fernet encryption** - Uses cryptographically secure symmetric encryption
- **SHA-256 key derivation** - Passwords are hashed using SHA-256
- **Filename obfuscation** - Both content and filenames are encrypted
- **Base64 encoding** - Encrypted filenames use filesystem-safe encoding

## File Structure

```
original_file.txt → [encrypted_content].kubli
```

Encrypted files:

- Have `.kubli` extension
- Contain encrypted file content
- Have encrypted filenames that are base64 encoded

## Sample Files

The `sample/` folder contains encrypted files that you can use to test the decryption functionality:

### Decrypting Sample Files

To decrypt the sample files:

1. Run the application: `python kubli.py`
2. Select option **2** (Decrypt)
3. Enter the password: `xaltius_academy`
4. Enter the directory path: `sample` (or the full path to the sample folder)
5. Review the encrypted files and their decrypted filename previews
6. Confirm to proceed with decryption
7. Choose whether to delete the encrypted files after decryption

The sample files will be decrypted and you can see the original content and filenames.

### Encrypting Sample Files

To test encryption using the same password:

1. Run the application: `python kubli.py`
2. Select option **1** (Encrypt)
3. Enter any password or use the original password: `xaltius_academy`
4. Enter the directory path containing files you want to encrypt
5. Review the list of files to be encrypted
6. Confirm to proceed with encryption
7. Choose whether to delete original files after encryption

This will create `.kubli` files that can later be decrypted using the same password.

## Error Handling

The application includes comprehensive error handling for:

- Invalid directory paths
- Empty passwords
- File access permissions
- Encryption/decryption failures
- File deletion errors

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues on GitHub.

---

**⚠️ Important Security Notice**: Always backup your files before encryption and remember your
passwords. There is no password recovery mechanism - lost passwords mean permanently lost access to
your encrypted files.
