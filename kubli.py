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

def encrypt_file(file_path, key):
    """Encrypt a single file"""
    try:
        fernet = Fernet(key)
        with open(file_path, 'rb') as file:
            original_data = file.read()
        
        encrypted_data = fernet.encrypt(original_data)
        
        with open(file_path + '.kubli', 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
        
        return True
    except Exception as e:
        print(f"Error encrypting {file_path}: {e}")
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
        print("\n--- Data Decryption ---")
    elif option == "4":
        print("\nThank you for using Kubli!")
        print("Goodbye!")
        break
    else:
        print("\nInvalid option! Please select a number specified in the menu.")
        print("\n")