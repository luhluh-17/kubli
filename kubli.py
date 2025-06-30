import os
import glob
from cryptography.fernet import Fernet
import base64
import hashlib

VERSION = "0.1.0v"
AUTHOR = "https://github.com/luhluh-17"

def generate_key_from_password(password):
    """Generate a Fernet key from a password"""
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_filename(filename, key):
    """Encrypt a filename"""
    try:
        fernet = Fernet(key)
        encrypted_filename = fernet.encrypt(filename.encode())
        # Convert to base64 and remove padding characters that might cause filesystem issues
        safe_filename = base64.urlsafe_b64encode(encrypted_filename).decode().replace('=', '_')
        return safe_filename
    except Exception as e:
        print(f"Error encrypting filename {filename}: {e}")
        return None

def decrypt_filename(encrypted_filename, key):
    """Decrypt a filename"""
    try:
        fernet = Fernet(key)
        # Restore padding and decode
        padded_filename = encrypted_filename.replace('_', '=')
        encrypted_data = base64.urlsafe_b64decode(padded_filename)
        decrypted_filename = fernet.decrypt(encrypted_data).decode()
        return decrypted_filename
    except Exception as e:
        print(f"Error decrypting filename: {e}")
        return None

def encrypt_file(file_path, key):
    """Encrypt a single file with filename encryption"""
    try:
        fernet = Fernet(key)
        
        # Read and encrypt file content
        with open(file_path, 'rb') as file:
            original_data = file.read()
        
        encrypted_data = fernet.encrypt(original_data)
        
        # Encrypt filename
        original_filename = os.path.basename(file_path)
        encrypted_filename = encrypt_filename(original_filename, key)
        
        if encrypted_filename is None:
            return False
        
        # Create new encrypted file path
        directory = os.path.dirname(file_path)
        encrypted_file_path = os.path.join(directory, encrypted_filename + '.kubli')
        
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
        
        return True
    except Exception as e:
        print(f"Error encrypting {file_path}: {e}")
        return False
    
def decrypt_file(file_path, key):
    """Decrypt a single file with filename decryption"""
    try:
        fernet = Fernet(key)
        
        # Read and decrypt file content
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Decrypt filename
        encrypted_filename = os.path.basename(file_path).replace('.kubli', '')
        original_filename = decrypt_filename(encrypted_filename, key)
        
        if original_filename is None:
            return False
        
        # Create original file path
        directory = os.path.dirname(file_path)
        original_file_path = os.path.join(directory, original_filename)
        
        with open(original_file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        
        return True
    except Exception as e:
        print(f"Error decrypting {file_path}: {e}")
        return False
    
def encrypt_directory():
    """Encrypt files in the current directory"""
    print("--- Data Encryption ---")
    
    # Get encryption key from user
    password = input("Enter encryption key: ")
    if not password:
        print("Error: Encryption key cannot be empty!")
        return
    
    key = generate_key_from_password(password)
    
    # Get current directory
    directory = input("Enter directory path (or press Enter for current directory): ").strip()
    if not directory:
        directory = os.getcwd()
    
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist!")
        return
    
    # List all files in directory (excluding this script and already encrypted files)
    script_name = os.path.basename(__file__)
    files_to_encrypt = []
    
    for file_path in glob.glob(os.path.join(directory, "*")):
        if (os.path.isfile(file_path) and 
            not file_path.endswith('.kubli') and 
            os.path.basename(file_path) != script_name):
            files_to_encrypt.append(file_path)
    
    if not files_to_encrypt:
        print("No files found to encrypt!")
        return
    
    print(f"\nFiles to encrypt ({len(files_to_encrypt)}):")
    for file_path in files_to_encrypt:
        print(f"  - {os.path.basename(file_path)}")
    
    confirm = input("\nProceed with encryption? (y/N): ").lower()
    if confirm != 'y':
        print("Encryption cancelled.")
        return
    
    # Encrypt files
    successful_encryptions = []
    for file_path in files_to_encrypt:
        print(f"Encrypting: {os.path.basename(file_path)}")
        if encrypt_file(file_path, key):
            successful_encryptions.append(file_path)
            print(f"  ✓ Encrypted successfully")
        else:
            print(f"  ✗ Failed to encrypt")
    
    # Delete original files if encryption was successful
    if successful_encryptions:
        delete_confirm = input(f"\nDelete {len(successful_encryptions)} original files? (y/N): ").lower()
        if delete_confirm == 'y':
            for file_path in successful_encryptions:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    print(f"\nEncryption complete! {len(successful_encryptions)} files encrypted.")

def decrypt_directory():
    """Decrypt files in the current directory"""
    print("--- Data Decryption ---")
    
    # Get decryption key from user
    password = input("Enter decryption key: ")
    if not password:
        print("Error: Decryption key cannot be empty!")
        return
    
    key = generate_key_from_password(password)
    
    # Get current directory
    directory = input("Enter directory path (or press Enter for current directory): ").strip()
    if not directory:
        directory = os.getcwd()
    
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist!")
        return
    
    # List all encrypted files in directory
    encrypted_files = glob.glob(os.path.join(directory, "*.kubli"))
    
    if not encrypted_files:
        print("No encrypted files found!")
        return
    
    print(f"\nEncrypted files found ({len(encrypted_files)}):")
    for file_path in encrypted_files:
        # Try to decrypt filename for display
        encrypted_filename = os.path.basename(file_path).replace('.kubli', '')
        original_filename = decrypt_filename(encrypted_filename, key)
        if original_filename:
            print(f"  - {os.path.basename(file_path)} → {original_filename}")
        else:
            print(f"  - {os.path.basename(file_path)} (filename decryption failed)")
    
    confirm = input("\nProceed with decryption? (y/N): ").lower()
    if confirm != 'y':
        print("Decryption cancelled.")
        return
    
    # Decrypt files
    successful_decryptions = []
    for file_path in encrypted_files:
        print(f"Decrypting: {os.path.basename(file_path)}")
        if decrypt_file(file_path, key):
            successful_decryptions.append(file_path)
            print(f"  ✓ Decrypted successfully")
        else:
            print(f"  ✗ Failed to decrypt (wrong key?)")
    
    # Delete encrypted files if decryption was successful
    if successful_decryptions:
        delete_confirm = input(f"\nDelete {len(successful_decryptions)} encrypted files? (y/N): ").lower()
        if delete_confirm == 'y':
            for file_path in successful_decryptions:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    print(f"\nDecryption complete! {len(successful_decryptions)} files decrypted.")


print(r"""
+----------------------------------------------------------------+
|                     _           _     _  _                     |
|                    | |         | |   | |(_)                    |
|                    | |  _ _   _| |__ | | _                     |
|                    | |_/ ) | | |  _ \| || |                    |
|                    |  _ (| |_| | |_) ) || |                    |
|                    |_| \_)____/|____/ \_)_|                    |
+----------------------------------------------------------------+
""")

print("In Tagalog, \"kubli\" generally means hidden, concealed, or secret")
print("\n")
print("Version:", VERSION)
print("Author:", AUTHOR)
print("\n")

# User menu options
while True:
    print("Please select an option:")
    print("1. Encrypt")
    print("2. Decrypt")
    print("4. Exit")

    option = input("\nEnter your option: ")

    if option == "1":
        encrypt_directory()
    elif option == "2":
        decrypt_directory()
    elif option == "4":
        print("\nThank you for using Kubli!")
        print("Goodbye!")
        break
    else:
        print("\nInvalid option! Please select a number specified in the menu.")
        print("\n")