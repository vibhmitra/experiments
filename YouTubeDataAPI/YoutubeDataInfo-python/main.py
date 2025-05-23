# YoutubeDataInfo-python
# main.py
import os
# from auth import get_credentials
from utils import clear_console


def display_menu():
    print("\nMenu:")
    print("1. Get Subscription Data")
    print("2. Get Playlist Data")
    print("0. Exit")

def handle_choice(choice):
    actions = { 1: "Getting Sub Data...", 2: "Getting Playlist Data...", 0: "Exiting..."}
    
    if choice in actions:
        print(actions[choice])
        return choice == 0  # Return True if exiting
    else:
        print("[!] Invalid choice. Please try again.\n")
        return False

def menu():
    while True:
        display_menu()

        try:
            choice = int(input("Enter your choice: "))  # Ensure numeric input
        except ValueError:
            print("[!] Invalid input. Please enter a number.\n")
            continue

        if handle_choice(choice):
            break

if __name__ == "__main__":
    menu()
    print(os.path.dirname(__file__))
