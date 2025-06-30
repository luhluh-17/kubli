VERSION = "0.1.0v"
AUTHOR = "https://github.com/luhluh-17"

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
    print("1. Decrypt")
    print("2. Encrypt")
    print("4. Exit")

    option = input("\nEnter your option: ")

    if option == "1":
        print("\n--- Data Decryption ---")
    elif option == "2":
        print("\n--- Data Encryption ---")
    elif option == "4":
        print("\nThank you for using Kubli!")
        print("Goodbye!")
        break
    else:
        print("\nInvalid option! Please select a number specified in the menu.")
        print("\n")