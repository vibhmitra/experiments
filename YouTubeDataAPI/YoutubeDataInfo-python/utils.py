import os
import select

# clear_console()
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    return True

# Function to get available tokens
def get_tokens():
    # Look for all the available .pickle files
    files = os.listdir(os.path.dirname(__file__))
    # Ask user to select one
    print("Select a token file:")
    for i, file in enumerate(files):
        if file.endswith('.pickle'):
            print(f"{i}: {file}")
    # Check if there are no .pickle files
    if not any(file.endswith('.pickle') for file in files):
        print("No token files found. Please create one.")
        return None
    # Get user input
    while True:
        try:
            choice = int(input("Enter the number of the file you want to use: "))
            if choice < 0 or choice >= len(files):
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    # Set the TOKEN_CREDS to the selected file
    selected_file = files[choice]
    TOKEN_CREDS = os.path.join(os.path.dirname(__file__), selected_file)
    return TOKEN_CREDS