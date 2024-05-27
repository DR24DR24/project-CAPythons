import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from typing import List, Tuple, Type

import difflib
import string
from colorama import Fore, Style, init
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML

from app.command_registry import command_registry
from app.entities import (
    FIELD_TYPES,
    AddressBook,
    Birthday,
    Email,
    Field,
    Name,
    NotesBook,
    Phone,
)
from app.interfaces import Command
from app.services import handle_command
from app.settings import Settings
from infrastructure.storage import FileStorage
from presentation.messages import Message


class CommandCompleter(Completer):
    def __init__(self, address_book: AddressBook):
        self.address_book = address_book
        self.current_completions: List[str] = list(command_registry.keys())

    def update_completions(self, command: str = "", args: List[str] = []):
        """Update the list of completions based on the current command and arguments."""
        if command not in command_registry:
            self.current_completions = list(command_registry.keys())
            return

        command_class = command_registry[command]
        if not hasattr(command_class, "expected_fields"):
            self.current_completions = list(command_registry.keys())
            return

        field_index = len(args)
        if field_index > len(command_class.expected_fields):
            self.current_completions = []
            return

        field_type = command_class.expected_fields[field_index - 1]
        if field_type not in FIELD_TYPES.values():
            self.current_completions = []
            return

        if field_index == 1:
            # Suggestions for the first argument (contact name)
            self.current_completions = [
                record.fields["name"].value for record in self.address_book.values()
            ]
        elif field_index > 1 and issubclass(field_type, Field):
            contact_name = args[0] if args else ""
            contact = self.address_book.find_by_name(Name(contact_name))
            if contact:
                self.current_completions = [
                    field.value
                    for field in contact.fields.get(field_type.__name__.lower(), [])
                ]
            else:
                self.current_completions = []
        else:
            self.current_completions = self.get_field_values(field_type)

    def get_field_values(self, field_type: Type) -> List[str]:
        """Retrieve possible field values based on the field type."""
        if field_type == Name:
            return [
                record.fields["name"].value for record in self.address_book.values()
            ]
        elif field_type == Phone:
            return [
                phone.value
                for record in self.address_book.values()
                for phone in record.fields.get("phones", [])
            ]
        elif field_type == Birthday:
            return [
                record.fields["birthday"].value
                for record in self.address_book.values()
                if "birthday" in record.fields
            ]
        elif field_type == Email:
            return [
                email.value
                for record in self.address_book.values()
                for email in record.fields.get("emails", [])
            ]
        # Add other fields as needed
        return []

    def get_completions(self, document: Document, complete_event):
        """Generate completions based on the current input."""
        text = document.text_before_cursor
        words = text.split()
        command = words[0] if words else ""
        # Switch to the next argument if the user has typed a delimiter
        if text and text[-1] in string.punctuation + string.whitespace:
            words.append(" ")
        args = words[1:] if len(words) > 1 else []

        if command:
            self.update_completions(command, args)
        else:
            self.update_completions()

        if words:
            current_word = words[-1]
            matches = difflib.get_close_matches(
                current_word, self.current_completions, n=5, cutoff=0.1
            )
            for match in matches:
                yield Completion(match, start_position=-len(current_word))
        else:
            for completion in self.current_completions:
                yield Completion(completion, start_position=0)


def parse_input(user_input: str) -> Tuple[str, list[str]]:
    """Parse the user input into a command and arguments."""
    parts = user_input.split()
    command = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command, args


def main():
    storage = FileStorage("addressbook.json")
    address_book = AddressBook(
        storage.load_contacts()
    )  # Load the address book from the file
    notes_book = NotesBook()  # Initialize NotesBook

    init(autoreset=True)  # Initialize colorama

    # Initialize settings and load templates
    settings = Settings()
    Message.load_templates(settings.language)

    banner_part_1 = """
                                                                                                          
 ,-----.  ,---.  ,------.            ,--.  ,--.                           ,-----.                ,--.     
'  .--./ /  O  \ |  .--. ',--. ,--.,-'  '-.|  ,---.  ,---. ,--,--,  ,---. |  |) /_  ,---.  ,---. |  |,-.  
|  |    |  .-.  ||  '--' | \  '  / '-.  .-'|  .-.  || .-. ||      \(  .-' |  .-.  \| .-. || .-. ||     /  
'  '--'\|  | |  ||  | --'   \   '    |  |  |  | |  |' '-' '|  ||  |.-'  `)|  '--' /' '-' '' '-' '|  \  \  
 `-----'`--' `--'`--'     .-'  /     `--'  `--' `--' `---' `--''--'`----' `------'  `---'  `---' `--'`--' 
                          `---'                                                                           
"""
    print(f"{Fore.GREEN}{banner_part_1}{Style.RESET_ALL}")
    print()
    print(
        f"{Fore.CYAN}{Style.BRIGHT}Welcome to the CAPythonsBook ver. 1.2 !{Style.RESET_ALL}"
    )
    print()

    # Call the help command to display available commands
    handle_command("help", address_book, notes_book)

    session = PromptSession(
        completer=CommandCompleter(address_book), auto_suggest=AutoSuggestFromHistory()
    )

    while not Command.exit_command_flag:
        enter_command_prompt = Message.format_message("enter_command")
        try:
            user_input = session.prompt(
                HTML(f"<ansiyellow>{enter_command_prompt}</ansiyellow> ")
            )
            command, args = parse_input(user_input)

            # Check if the command is not found and suggest closest matches
            if command not in command_registry:
                suggestions = difflib.get_close_matches(
                    command, command_registry.keys()
                )
                if suggestions:
                    print(f"{Fore.YELLOW}Did you mean:{Style.RESET_ALL}")
                    for suggestion in suggestions:
                        print(f"  {suggestion}")
                    continue

            handle_command(command, address_book, notes_book, *args)
            storage.save_contacts(
                address_book
            )  # Save the contacts after handling the command
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
