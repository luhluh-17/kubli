import os
import glob
from cryptography.fernet import Fernet
import base64
import hashlib
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform support
init(autoreset=True)


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
        print(f"{Fore.RED}Error encrypting filename {filename}: {e}")
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
        print(f"{Fore.RED}Error decrypting filename: {e}")
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
        print(f"{Fore.RED}Error encrypting {file_path}: {e}")
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
        print(f"{Fore.RED}Error decrypting {file_path}: {e}")
        return False
    
def encrypt_directory():
    """Encrypt files in the current directory"""
    print(f"{Fore.CYAN}{Style.BRIGHT}--- Data Encryption ---")
    
    # Get encryption key from user
    password = input(f"{Fore.YELLOW}Enter encryption key: ")
    if not password:
        print(f"{Fore.RED}Error: Encryption key cannot be empty!")
        return
    
    key = generate_key_from_password(password)
    
    # Get current directory
    directory = input(f"{Fore.YELLOW}Enter directory path (or press Enter for current directory): ").strip()
    if not directory:
        directory = os.getcwd()
    
    if not os.path.exists(directory):
        print(f"{Fore.RED}Error: Directory '{directory}' does not exist!")
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
        print(f"{Fore.YELLOW}No files found to encrypt!")
        return
    
    print(f"\n{Fore.BLUE}Files to encrypt ({len(files_to_encrypt)}):")
    for file_path in files_to_encrypt:
        print(f"  - {Fore.WHITE}{os.path.basename(file_path)}")
    
    confirm = input(f"\n{Fore.YELLOW}Proceed with encryption? (y/N): ").lower()
    if confirm != 'y':
        print(f"{Fore.YELLOW}Encryption cancelled.")
        return
    
    # Encrypt files
    successful_encryptions = []
    for file_path in files_to_encrypt:
        print(f"Encrypting: {Fore.WHITE}{os.path.basename(file_path)}")
        if encrypt_file(file_path, key):
            successful_encryptions.append(file_path)
            print(f"  {Fore.GREEN}✓ Encrypted successfully")
        else:
            print(f"  {Fore.RED}✗ Failed to encrypt")
    
    # Delete original files if encryption was successful
    if successful_encryptions:
        delete_confirm = input(f"\n{Fore.YELLOW}Delete {len(successful_encryptions)} original files? (y/N): ").lower()
        if delete_confirm == 'y':
            for file_path in successful_encryptions:
                try:
                    os.remove(file_path)
                    print(f"{Fore.GREEN}Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"{Fore.RED}Error deleting {file_path}: {e}")
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Encryption complete! {len(successful_encryptions)} files encrypted.")

def decrypt_directory():
    """Decrypt files in the current directory"""
    print(f"{Fore.CYAN}{Style.BRIGHT}--- Data Decryption ---")
    
    # Get decryption key from user
    password = input(f"{Fore.YELLOW}Enter decryption key: ")
    if not password:
        print(f"{Fore.RED}Error: Decryption key cannot be empty!")
        return
    
    key = generate_key_from_password(password)
    
    # Get current directory
    directory = input(f"{Fore.YELLOW}Enter directory path (or press Enter for current directory): ").strip()
    if not directory:
        directory = os.getcwd()
    
    if not os.path.exists(directory):
        print(f"{Fore.RED}Error: Directory '{directory}' does not exist!")
        return
    
    # List all encrypted files in directory
    encrypted_files = glob.glob(os.path.join(directory, "*.kubli"))
    
    if not encrypted_files:
        print(f"{Fore.YELLOW}No encrypted files found!")
        return
    
    print(f"\n{Fore.BLUE}Encrypted files found ({len(encrypted_files)}):")
    for file_path in encrypted_files:
        # Try to decrypt filename for display
        encrypted_filename = os.path.basename(file_path).replace('.kubli', '')
        original_filename = decrypt_filename(encrypted_filename, key)
        if original_filename:
            print(f"  - {Fore.MAGENTA}{os.path.basename(file_path)} {Fore.CYAN}→ {Fore.GREEN}{original_filename}")
        else:
            print(f"  - {Fore.MAGENTA}{os.path.basename(file_path)} {Fore.RED}(filename decryption failed)")
    
    confirm = input(f"\n{Fore.YELLOW}Proceed with decryption? (y/N): ").lower()
    if confirm != 'y':
        print(f"{Fore.YELLOW}Decryption cancelled.")
        return
    
    # Decrypt files
    successful_decryptions = []
    for file_path in encrypted_files:
        print(f"Decrypting: {Fore.WHITE}{os.path.basename(file_path)}")
        if decrypt_file(file_path, key):
            successful_decryptions.append(file_path)
            print(f"  {Fore.GREEN}✓ Decrypted successfully")
        else:
            print(f"  {Fore.RED}✗ Failed to decrypt (wrong key?)")
    
    # Delete encrypted files if decryption was successful
    if successful_decryptions:
        delete_confirm = input(f"\n{Fore.YELLOW}Delete {len(successful_decryptions)} encrypted files? (y/N): ").lower()
        if delete_confirm == 'y':
            for file_path in successful_decryptions:
                try:
                    os.remove(file_path)
                    print(f"{Fore.GREEN}Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"{Fore.RED}Error deleting {file_path}: {e}")
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Decryption complete! {len(successful_decryptions)} files decrypted.")

def display_banner():
    """
    Display the application banner with ASCII art and metadata.
    
    Shows the Kubli logo, application description, version, author, and GitHub info.
    
    Returns:
        None
    """
    VERSION = "0.1.0v"
    AUTHOR = "Ralph Joseph Castro"
    GITHUB = "https://github.com/luhluh-17"

    print(f"{Fore.MAGENTA}{Style.BRIGHT}+----------------------------------------------------------------+")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}|                     _           _     _  _                     |")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}|                    | |         | |   | |(_)                    |")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}|                    | |  _ _   _| |__ | | _                     |")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}|                    | |_/ ) | | |  _ \\| || |                    |")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}|                    |  _ (| |_| | |_) ) || |                    |")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}|                    |_| \\_)____/|____/ \\_)_|                    |")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}+----------------------------------------------------------------+")
    
    print(f"{Fore.MAGENTA}In Tagalog, \"kubli\" generally means hidden, concealed, or secret")
    print("\n")
    print(f"{Fore.BLUE}Version: {Fore.WHITE}{VERSION}")
    print(f"{Fore.BLUE}Author: {Fore.WHITE}{AUTHOR}")
    print(f"{Fore.BLUE}GitHub: {Fore.WHITE}{GITHUB}")
    print("\n")
    
def main_menu():
    """
    
    Displays a menu with encryption/decryption options and handles user input.
    Runs in an infinite loop until user selects exit option (3).
    
    Returns:
        None
    """
    while True:
        print(f"{Fore.CYAN}Please select an option:")
        print(f"{Fore.GREEN}1. Encrypt")
        print(f"{Fore.GREEN}2. Decrypt")
        print(f"{Fore.RED}3. Exit")

        option = input(f"\n{Fore.YELLOW}Enter your option: ")

        if option == "1":
            encrypt_directory()
        elif option == "2":
            decrypt_directory()
        elif option == "3":
            print(f"\n{Fore.GREEN}Thank you for using Kubli!")
            print(f"{Fore.GREEN}Goodbye!")
            break
        else:
            print(f"\n{Fore.RED}Invalid option! Please select a number specified in the menu.")
            print("\n")

def main():
    """
    Main entry point for the Kubli file encryption/decryption application.
    
    Returns:
        None
    """
    display_banner()
    main_menu()

# Run the application
if __name__ == "__main__":
    main()