# YoutubeDataInfo-python
# main.py

from auth import get_credentials
from utils import clear_console


def menu():
    while True:
        print("1. Get Subscription Data")
        print("2. Get Playlist Data")
        print("0. Exit")

        try:
            choice = int(input("Enter your choice: "))  # Ensure numeric input
        except ValueError:
            print("Invalid input. Please enter a number.\n")
            continue

        if choice == 1:
            print("Getting Credentials...")
        elif choice == 2:
            print("Getting Playlist Data...")
        elif choice == 0:
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    menu()
        
