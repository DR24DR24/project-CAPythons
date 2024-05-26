import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from typing import Tuple

import difflib
from colorama import Fore, Style, init
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML


from app.command_registry import command_registry
from app.entities import AddressBook, NotesBook
from app.interfaces import Command
from app.services import handle_command
from app.settings import Settings
from infrastructure.storage import FileStorage
from presentation.messages import Message




class CommandCompleter(Completer):
    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        matches = difflib.get_close_matches(
            text, command_registry.keys(), n=5, cutoff=0.1
        )
        for match in matches:
            yield Completion(match, start_position=-len(text))

def process_string(s: str) -> str:
    parts = s.split(' ', 1)
    if len(parts) < 2:
        return s

    first_part = parts[0]
    remaining_part = parts[1]
    first_part_lower = first_part.lower()

    result = f"{first_part_lower} {remaining_part}"
    return result

def parse_input(user_input: str) -> Tuple[str, list[str]]:
    """Parse the user input into a command and arguments."""
    # is_note = 'note' in user_input.split(" ")[0]
    # parts = user_input.lower().split() if not is_note else process_string(user_input).split()
    parts = process_string(user_input).split()
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
        f"{Fore.CYAN}{Style.BRIGHT}Welcome to the Assistant Bot ver. 2.3 !{
            Style.RESET_ALL}"
    )
    print()

    # Call the help command to display available commands
    handle_command("help", address_book, notes_book)

    session = PromptSession(
        completer=CommandCompleter(), auto_suggest=AutoSuggestFromHistory()
    )

    while not Command.exit_command_flag:
        enter_command_prompt = Message.format_message("enter_command")
        user_input = session.prompt(
            HTML(f"<ansiyellow>{enter_command_prompt}</ansiyellow> ")
        )
        command, args = parse_input(user_input)

        # Check if the command is not found and suggest closest matches
        if command not in command_registry:
            suggestions = difflib.get_close_matches(command, command_registry.keys())
            if suggestions:
                print(f"{Fore.YELLOW}Did you mean:{Style.RESET_ALL}")
                for suggestion in suggestions:
                    print(f"  {suggestion}")
                continue

        handle_command(command, address_book, notes_book, *args)
        storage.save_contacts(
            address_book
        )  # Save the contacts after handling the command


if __name__ == "__main__":
    main()
