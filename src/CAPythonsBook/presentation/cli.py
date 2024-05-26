import sys
import os
from typing import Tuple

from app.interfaces import Command

# Add project root directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.entities import AddressBook, NotesBook
from app.services import handle_command
from presentation.messages import Message
from infrastructure.storage import FileStorage
from app.settings import Settings
from colorama import init, Fore, Style


def parse_input(user_input: str) -> Tuple[str, list[str]]:
    """Parse the user input into a command and arguments."""
    parts = user_input.lower().split()
    command = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command, args


def main():
    storage = FileStorage("addressbook.json")
    address_book = AddressBook(
        storage.load_contacts()
    )  # Load the address book from the file

    notes_book = NotesBook()

    init(autoreset=True)  # Initialize colorama

    # Initialize settings and load templates
    settings = Settings()
    Message.load_templates(settings.language)

    banner_part_1 = """
     _               _       _                 _     ____          _                ____  
    / \\    ___  ___ (_) ___ | |_  __ _  _ __  | |_  | __ )   ___  | |_    __   __  |___ \\ 
   / _ \\  / __|/ __|| |/ __|| __|/ _` || '_ \\ | __| |  _ \\  / _ \\ | __|   \\ \\ / /    __) |
  / ___ \\ \\_  \\\\ _ \\| |\\__ \\| |_| (_| || | | || |_  | |_) || (_) || |_     \\ V /_   / __/ 
 /_/   \\_\\|___/|___/|_||___/ \\__|\\__,_||_| |_| \\__| |____/  \\___/  \\__|     \\_/(_) |_____|
                                                                                         
"""
    print(f"{Fore.GREEN}{banner_part_1}{Style.RESET_ALL}")
    print()
    print(
        f"{Fore.CYAN}{Style.BRIGHT}Welcome to the Assistant Bot ver. 2.3 !{Style.RESET_ALL}"
    )
    print()

    handle_command("help", address_book, notes_book)

    while not Command.exit_command_flag:
        enter_command_prompt = Message.format_message("enter_command")
        user_input = input(
            f"{Fore.YELLOW}{enter_command_prompt}{Style.RESET_ALL}"
        ).strip()
        command, args = parse_input(user_input)
        handle_command(command, address_book, notes_book, *args)
        storage.save_contacts(
            address_book
        )  # Save the contacts after handling the command
