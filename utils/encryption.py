import os
import glob
from cryptography.fernet import Fernet
import base64
import hashlib
from colorama import Fore, Style


def generate_key_from_password(password):
    """
    Generate a Fernet-compatible encryption key from a password.

    Converts a user password into a cryptographic key using SHA-256 hashing
    and base64 URL-safe encoding for use with the Fernet encryption algorithm.

    Args:
        password (str): The user password to convert into an encryption key

    Returns:
        bytes: A base64 URL-safe encoded key suitable for Fernet encryption
    """
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_filename(filename, key):
    """
    Encrypt a filename using Fernet encryption with filesystem-safe encoding.

    Encrypts the given filename using the provided key and converts it to a
    filesystem-safe format by base64 encoding and replacing padding characters
    with underscores to avoid potential filesystem issues.

    Args:
        filename (str): The original filename to encrypt
        key (bytes): The Fernet encryption key

    Returns:
        str: The encrypted and filesystem-safe encoded filename, or None if encryption fails

    Raises:
        Exception: Prints error message and returns None if encryption fails
    """
    try:
        fernet = Fernet(key)
        encrypted_filename = fernet.encrypt(filename.encode())
        # Convert to base64 and remove padding characters that might cause filesystem issues
        safe_filename = (
            base64.urlsafe_b64encode(encrypted_filename).decode().replace("=", "_")
        )
        return safe_filename
    except Exception as e:
        print(f"{Fore.RED}Error encrypting filename {filename}: {e}")
        return None


def encrypt_file(file_path, key):
    """
    Encrypt a single file with filename encryption.

    Encrypts both the file content and filename using Fernet encryption.
    Creates a new encrypted file with .kubli extension and encrypted filename.

    Args:
        file_path (str): Path to the file to encrypt
        key (bytes): The Fernet encryption key

    Returns:
        bool: True if encryption successful, False if failed

    Raises:
        Exception: Prints error message and returns False if encryption fails
    """
    try:
        fernet = Fernet(key)

        # Read and encrypt file content
        with open(file_path, "rb") as file:
            original_data = file.read()

        encrypted_data = fernet.encrypt(original_data)

        # Encrypt filename
        original_filename = os.path.basename(file_path)
        encrypted_filename = encrypt_filename(original_filename, key)

        if encrypted_filename is None:
            return False

        # Create new encrypted file path
        directory = os.path.dirname(file_path)
        encrypted_file_path = os.path.join(directory, encrypted_filename + ".kubli")

        with open(encrypted_file_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)

        return True
    except Exception as e:
        print(f"{Fore.RED}Error encrypting {file_path}: {e}")
        return False


def encrypt_directory():
    """
    Interactive directory encryption function.

    Prompts user for encryption password and directory path, then encrypts all
    eligible files in the specified directory. Excludes .kubli files and the
    script itself from encryption. Provides user confirmation before proceeding
    and optionally deletes original files after successful encryption.

    Process:
        1. Prompts for encryption password
        2. Gets target directory (defaults to current directory)
        3. Scans for eligible files to encrypt
        4. Shows list of files and asks for confirmation
        5. Encrypts each file using Fernet encryption
        6. Optionally deletes original files after successful encryption
        7. Reports encryption results

    Returns:
        None

    File Filtering:
        - Excludes files with .kubli extension (already encrypted)
        - Excludes the script file itself
        - Only processes regular files (not directories)
    """
    print(f"{Fore.CYAN}{Style.BRIGHT}--- Data Encryption ---")

    # Get encryption key from user
    password = input(f"{Fore.YELLOW}Enter encryption key: ")
    if not password:
        print(f"{Fore.RED}Error: Encryption key cannot be empty!")
        return

    key = generate_key_from_password(password)

    # Get current directory
    directory = input(
        f"{Fore.YELLOW}Enter directory path (or press Enter for current directory): "
    ).strip()
    if not directory:
        directory = os.getcwd()

    if not os.path.exists(directory):
        print(f"{Fore.RED}Error: Directory '{directory}' does not exist!")
        return

    # List all files in directory (excluding this script and already encrypted files)
    # Get the main script name from the calling module
    script_name = "kubli.py"
    files_to_encrypt = []

    for file_path in glob.glob(os.path.join(directory, "*")):
        if (
            os.path.isfile(file_path)
            and not file_path.endswith(".kubli")
            and os.path.basename(file_path) != script_name
            and not os.path.basename(file_path).endswith(".py")  # Exclude Python files
        ):
            files_to_encrypt.append(file_path)

    if not files_to_encrypt:
        print(f"{Fore.YELLOW}No files found to encrypt!")
        return

    print(f"\n{Fore.BLUE}Files to encrypt ({len(files_to_encrypt)}):")
    for file_path in files_to_encrypt:
        print(f"  - {Fore.WHITE}{os.path.basename(file_path)}")

    confirm = input(f"\n{Fore.YELLOW}Proceed with encryption? (y/N): ").lower()
    if confirm != "y":
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
        delete_confirm = input(
            f"\n{Fore.YELLOW}Delete {len(successful_encryptions)} original files? (y/N): "
        ).lower()
        if delete_confirm == "y":
            for file_path in successful_encryptions:
                try:
                    os.remove(file_path)
                    print(f"{Fore.GREEN}Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"{Fore.RED}Error deleting {file_path}: {e}")

    print(
        f"\n{Fore.GREEN}{Style.BRIGHT}Encryption complete! {len(successful_encryptions)} files encrypted."
    )
