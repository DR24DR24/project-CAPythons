import sys
from typing import Callable, Dict, List, Optional
from colorama import Fore, Style, init

from src.app.entities import AddressBook
from src.app.services import (
    add_birthday,
    add_contact,
    add_phone_to_contact,
    birthdays,
    change_contact,
    hello,
    help_command,
    input_error,
    show_all_contacts,
    show_birthday,
    show_phone,
)
from src.infrastructure.storage import load_data, save_data


def parse_input(user_input: str) -> tuple[str, List[str]]:
    parts = user_input.lower().split()
    command = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command, args


@input_error
def handle_command(
    command_handlers: Dict[str, Callable[[Optional[List[str]]], None]],
    command: str,
    args: Optional[List[str]],
) -> None:
    if command in command_handlers:
        if args is None:
            args = []
        command_handlers[command](args)
    else:
        raise TypeError(f"Unknown command '{command}'")


def handle_exit(address_book: AddressBook) -> None:
    save_data(address_book)
    print(f"{Fore.GREEN}{Style.BRIGHT}Good bye!{Style.RESET_ALL}")
    sys.exit()


def main():
    address_book = load_data()
    command_handlers: Dict[str, Callable[[Optional[List[str]]], None]] = {
        "hello": lambda _: hello(),
        "add": lambda args: add_contact(address_book, *args),
        "change": lambda args: change_contact(address_book, *args),
        "phone": lambda args: show_phone(address_book, *args),
        "add-phone": lambda args: add_phone_to_contact(address_book, *args),
        "all": lambda _: show_all_contacts(address_book),
        "add-birthday": lambda args: add_birthday(address_book, *args),
        "show-birthday": lambda args: show_birthday(address_book, *args),
        "birthdays": lambda _: birthdays(address_book),
        "close": lambda _: handle_exit(address_book),
        "exit": lambda _: handle_exit(address_book),
        "quit": lambda _: handle_exit(address_book),
        "help": lambda _: help_command(),
    }

    init(autoreset=True)
    banner_part_1 = """
     _               _       _                 _     ____          _                ____  
    / \\    ___  ___ (_) ___ | |_  __ _  _ __  | |_  | __ )   ___  | |_    __   __  |___ \\ 
   / _ \\  / __|/ __|| |/ __|| __|/ _` || '_ \\ | __| |  _ \\  / _ \\ | __|   \\ \\ / /    __) |
  / ___ \\ \\__ \\\\__ \\| |\\__ \\| |_| (_| || | | || |_  | |_) || (_) || |_     \\ V /_   / __/ 
 /_/   \\_\\|___/|___/|_||___/ \\__|\\__,_||_| |_| \\__| |____/  \\___/  \\__|     \\_/(_) |_____|
                                                                                          
"""
    print(f"{Fore.GREEN}{banner_part_1}{Style.RESET_ALL}")
    print()
    print(
        f"{Fore.CYAN}{Style.BRIGHT}Welcome to the Assistant Bot ver. 2.3 !{Style.RESET_ALL}"
    )
    print()
    help_command()

    while True:
        user_input = input(f"{Fore.YELLOW}Enter a command: {Style.RESET_ALL}").strip()
        command, args = parse_input(user_input)
        handle_command(command_handlers, command, args)


if __name__ == "__main__":
    main()
