import os
import glob
from cryptography.fernet import Fernet
import base64
from colorama import Fore, Style
from .encryption import generate_key_from_password


def decrypt_filename(encrypted_filename, key):
    """
    Decrypt a filename using Fernet decryption.

    Restores the original filename by reversing the encryption process:
    replaces underscores with padding characters, decodes from base64,
    and decrypts using the provided key.

    Args:
        encrypted_filename (str): The encrypted filename to decrypt
        key (bytes): The Fernet decryption key

    Returns:
        str: The original decrypted filename, or None if decryption fails

    Raises:
        Exception: Prints error message and returns None if decryption fails
    """
    try:
        fernet = Fernet(key)
        # Restore padding and decode
        padded_filename = encrypted_filename.replace("_", "=")
        encrypted_data = base64.urlsafe_b64decode(padded_filename)
        decrypted_filename = fernet.decrypt(encrypted_data).decode()
        return decrypted_filename
    except Exception as e:
        print(f"{Fore.RED}Error decrypting filename: {e}")
        return None


def decrypt_file(file_path, key):
    """
    Decrypt a single file with filename decryption.

    Decrypts both the file content and filename using Fernet decryption.
    Reads a .kubli encrypted file, decrypts its content and filename,
    then creates the original file with restored name and content.

    Args:
        file_path (str): Path to the encrypted .kubli file to decrypt
        key (bytes): The Fernet decryption key

    Returns:
        bool: True if decryption successful, False if failed

    Raises:
        Exception: Prints error message and returns False if decryption fails
    """
    try:
        fernet = Fernet(key)

        # Read and decrypt file content
        with open(file_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        # Decrypt filename
        encrypted_filename = os.path.basename(file_path).replace(".kubli", "")
        original_filename = decrypt_filename(encrypted_filename, key)

        if original_filename is None:
            return False

        # Create original file path
        directory = os.path.dirname(file_path)
        original_file_path = os.path.join(directory, original_filename)

        with open(original_file_path, "wb") as decrypted_file:
            decrypted_file.write(decrypted_data)

        return True
    except Exception as e:
        print(f"{Fore.RED}Error decrypting {file_path}: {e}")
        return False


def decrypt_directory():
    """
    Interactive directory decryption function.

    Prompts user for decryption password and directory path, then decrypts all
    .kubli encrypted files in the specified directory. Shows encrypted filenames
    with their corresponding decrypted names for preview before proceeding.
    Optionally deletes encrypted files after successful decryption.

    Process:
        1. Prompts for decryption password
        2. Gets target directory (defaults to current directory)
        3. Scans for .kubli encrypted files
        4. Shows list of encrypted files with decrypted filename preview
        5. Asks for confirmation before proceeding
        6. Decrypts each file using Fernet decryption
        7. Optionally deletes encrypted files after successful decryption
        8. Reports decryption results

    Returns:
        None

    File Filtering:
        - Only processes files with .kubli extension
        - Attempts to decrypt filenames for preview display
    """
    print(f"{Fore.CYAN}{Style.BRIGHT}--- Data Decryption ---")

    # Get decryption key from user
    password = input(f"{Fore.YELLOW}Enter decryption key: ")
    if not password:
        print(f"{Fore.RED}Error: Decryption key cannot be empty!")
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

    # List all encrypted files in directory
    encrypted_files = glob.glob(os.path.join(directory, "*.kubli"))

    if not encrypted_files:
        print(f"{Fore.YELLOW}No encrypted files found!")
        return

    print(f"\n{Fore.BLUE}Encrypted files found ({len(encrypted_files)}):")
    for file_path in encrypted_files:
        # Try to decrypt filename for display
        encrypted_filename = os.path.basename(file_path).replace(".kubli", "")
        original_filename = decrypt_filename(encrypted_filename, key)
        if original_filename:
            print(
                f"  - {Fore.MAGENTA}{os.path.basename(file_path)} {Fore.CYAN}→ {Fore.GREEN}{original_filename}"
            )
        else:
            print(
                f"  - {Fore.MAGENTA}{os.path.basename(file_path)} {Fore.RED}(filename decryption failed)"
            )

    confirm = input(f"\n{Fore.YELLOW}Proceed with decryption? (y/N): ").lower()
    if confirm != "y":
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
        delete_confirm = input(
            f"\n{Fore.YELLOW}Delete {len(successful_decryptions)} encrypted files? (y/N): "
        ).lower()
        if delete_confirm == "y":
            for file_path in successful_decryptions:
                try:
                    os.remove(file_path)
                    print(f"{Fore.GREEN}Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"{Fore.RED}Error deleting {file_path}: {e}")

    print(
        f"\n{Fore.GREEN}{Style.BRIGHT}Decryption complete! {len(successful_decryptions)} files decrypted."
    )
