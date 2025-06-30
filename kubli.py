from colorama import init, Fore, Style
from utils.encryption import encrypt_directory
from utils.decryption import decrypt_directory

# Initialize colorama for cross-platform support
init(autoreset=True)


def display_banner():
    """
    Display the application banner with ASCII art and metadata.

    Shows the Kubli logo, application description, version, author, and GitHub info.

    Returns:
        None
    """
    VERSION = "v0.1.0"
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

    print(f'{Fore.MAGENTA}In Tagalog, "kubli" generally means hidden, concealed, or secret')
    print("\n")
    print(f"{Fore.BLUE}Version: {Fore.WHITE}{VERSION}")
    print(f"{Fore.BLUE}Author: {Fore.WHITE}{AUTHOR}")
    print(f"{Fore.BLUE}GitHub: {Fore.WHITE}{GITHUB}")
    print("\n")


def main_menu():
    """
    Display the main menu interface for the Kubli application.

    Displays a menu with encryption/decryption options and handles user input.
    Runs in an infinite loop until user selects exit option (3).
    Calls encryption and decryption functions from their respective modules.

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
            print(
                f"\n{Fore.RED}Invalid option! Please select a number specified in the menu."
            )
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
