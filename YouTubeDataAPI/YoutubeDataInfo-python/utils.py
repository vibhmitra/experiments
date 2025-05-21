import os

# clear_console()
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    return True
