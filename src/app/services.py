import sys
from typing import Callable
from colorama import Fore, Style
from src.infrastructure.storage import save_data
from src.app.entities import AddressBook, Name, Phone, Birthday, Record


def input_error(handler: Callable) -> Callable:
    """Decorator for handling errors in command functions."""

    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except TypeError as e:
            print(
                f"{Fore.RED}Error: Incorrect command.\n{Fore.MAGENTA}{e}{Style.RESET_ALL}"
            )
            help_command()
        except ValueError as e:
            print(
                f"{Fore.RED}Error: Incorrect arguments.\n{Fore.MAGENTA}{e}{Style.RESET_ALL}"
            )
        except KeyError as e:
            print(
                f"{Fore.RED}Error: Contact not found.\n{Fore.MAGENTA}{e}{Style.RESET_ALL}"
            )
        except IndexError as e:
            print(
                f"{Fore.RED}Error: Index out of range.\n{Fore.MAGENTA}{e}{Style.RESET_ALL}"
            )
        except Exception as e:
            print(
                f"{Fore.RED}An unexpected error occurred:\n{Fore.MAGENTA}{e}{Style.RESET_ALL}"
            )

    return wrapper


@input_error
def hello() -> None:
    print(f"{Fore.CYAN}How can I help you?{Style.RESET_ALL}")


@input_error
def add_contact(contacts: AddressBook, *args: str) -> None:
    """Add a new contact.

    Parameters
    ----------
    contacts : AddressBook
        The address book containing contacts.
    args : str
        The name and phone number of the new contact.
    """
    if len(args) != 2:
        raise ValueError("Usage: add [name] [phone number]")
    name, phone = args
    record = contacts.find(Name(name))
    if record:
        if any(p.value == phone for p in record.phones):
            print(
                f'{Fore.YELLOW}Contact "{Fore.CYAN}{name}{Fore.YELLOW}" with phone number "{Fore.CYAN}{phone}{Fore.YELLOW}" already exists.{Style.RESET_ALL}'
            )
        else:
            current_phone = record.phones[0].value if record.phones else "No phone"
            print(
                f'{Fore.YELLOW}Contact "{Fore.CYAN}{name}{Fore.YELLOW}" is already added with the number "{Fore.CYAN}{current_phone}{Fore.YELLOW}".\nTo change the number, use the "{Style.RESET_ALL}change{Fore.YELLOW}" command.{Style.RESET_ALL}'
            )
    else:
        new_record = Record(Name(name))
        new_record.add_phone(Phone(phone))
        contacts.add_record(new_record)
        print(
            f'{Fore.GREEN}Contact "{Fore.CYAN}{name}{Fore.GREEN}" added with phone number "{Fore.CYAN}{phone}{Fore.GREEN}".{Style.RESET_ALL}'
        )


@input_error
def change_contact(contacts: AddressBook, *args: str) -> None:
    """Change an existing contact's phone number.

    Parameters
    ----------
    contacts : AddressBook
        The address book containing contacts.
    args : str
        The name and new phone number of the contact.
    """
    if len(args) != 2:
        raise ValueError("Usage: change [name] [new phone number]")
    name, new_phone = args
    record = contacts.find(Name(name))
    if record:
        current_phone = record.phones[0].value if record.phones else None
        if new_phone == current_phone:
            print(
                f'{Fore.YELLOW}Contact "{Fore.CYAN}{name}{Fore.YELLOW}" already has this phone number: "{Fore.CYAN}{new_phone}{Fore.YELLOW}". No changes were made.{Style.RESET_ALL}'
            )
        else:
            record.edit_phone(record.phones[0], Phone(new_phone))
            print(
                f'{Fore.GREEN}For user {Fore.CYAN}"{name}"{Fore.GREEN}, the phone has been changed from "{Fore.CYAN}{current_phone}{Fore.GREEN}" to "{Fore.CYAN}{new_phone}{Fore.GREEN}".{Style.RESET_ALL}'
            )
    else:
        raise KeyError(f"Name '{name}' not found.")


@input_error
def show_phone(contacts: AddressBook, *args: str) -> None:
    """Show the phone number of a contact.

    Parameters
    ----------
    contacts : AddressBook
        The address book containing contacts.
    args : str
        The name of the contact.
    """
    if len(args) != 1:
        raise ValueError("Usage: phone [name]")
    name = args[0]
    record = contacts.find(Name(name))
    if record:
        phones = "; ".join([phone.value for phone in record.phones])
        print(
            f'{Fore.GREEN}Phone number of "{Fore.CYAN}{name}{Fore.GREEN}": {Fore.CYAN}{phones}{Style.RESET_ALL}'
        )
    else:
        raise KeyError(f"Name '{name}' not found.")


@input_error
def add_phone_to_contact(address_book: AddressBook, *args: str) -> None:
    """Add an additional phone to a contact."""
    if len(args) != 2:
        raise ValueError("Usage: add-phone [name] [phone number]")
    name, phone = args
    record = address_book.find(Name(name))
    if record:
        record.add_phone(Phone(phone))
        print(
            f"{Fore.GREEN}For user {Fore.CYAN}{name}{Fore.GREEN} added an additional phone number: {Fore.CYAN}{phone}{Style.RESET_ALL}"
        )
    else:
        raise KeyError(f"Name '{name}' not found.")


@input_error
def show_all_contacts(contacts: AddressBook) -> None:
    """Show all contacts.

    Parameters
    ----------
    contacts : AddressBook
        The address book containing contacts.
    """
    if contacts.data:
        for record in contacts.data.values():
            print(str(record))
    else:
        raise IndexError("No contacts available.")


@input_error
def add_birthday(address_book: AddressBook, *args: str) -> None:
    """Add a birthday to a contact."""
    if len(args) != 2:
        raise ValueError("Usage: add-birthday [name] [birthday in DD.MM.YYYY]")
    name, birthday_str = args
    record = address_book.find(Name(name))
    if record:
        record.add_birthday(Birthday(birthday_str))
        print(
            f"{Fore.GREEN}Birthday for {Fore.CYAN}{name}{Fore.GREEN} set to {Fore.CYAN}{birthday_str}{Style.RESET_ALL}"
        )
    else:
        raise KeyError(f"Name '{name}' not found.")


@input_error
def show_birthday(address_book: AddressBook, *args: str) -> None:
    """Show the birthday of a contact."""
    if len(args) != 1:
        raise ValueError("Usage: show-birthday [name]")
    name = args[0]
    record = address_book.find(Name(name))
    if record:
        if record.birthday:
            print(
                f"{Fore.GREEN}Birthday of {Fore.CYAN}{record.name.value}{Fore.GREEN}: {Fore.CYAN}{record.birthday.value}{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.YELLOW}No birthday set for {Fore.CYAN}{name}{Fore.YELLOW}.{Style.RESET_ALL}"
            )
    else:
        raise KeyError(f"Name '{name}' not found.")


@input_error
def birthdays(address_book: AddressBook) -> None:
    """Show the upcoming birthdays within the next 7 days."""
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        for entry in upcoming_birthdays:
            print(
                f"{Fore.GREEN}{entry['name']}: {Fore.CYAN}{entry['congratulation_date']}{Style.RESET_ALL}"
            )
    else:
        print(
            f"{Fore.YELLOW}No upcoming birthdays in the next 7 days.{Style.RESET_ALL}"
        )


def handle_exit(address_book: AddressBook) -> None:
    save_data(address_book)
    print(f"{Fore.GREEN}{Style.BRIGHT}Good bye!{Style.RESET_ALL}")
    sys.exit()


def help_command():
    print(f"{Fore.GREEN}This bot helps you manage your contacts.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}You can use the following commands:{Style.RESET_ALL}")
    print(f"hello{Fore.GREEN} - Greets the user.{Style.RESET_ALL}")
    print(
        f"add [name] [phone number]{Fore.GREEN} - Adds a new contact.{Style.RESET_ALL}"
    )
    print(
        f"change [name] [new phone number]{Fore.GREEN} - Changes the phone number of an existing contact.{Style.RESET_ALL}"
    )
    print(
        f"phone [name]{Fore.GREEN} - Shows the phone number of a contact.{Style.RESET_ALL}"
    )
    print(
        f"add-phone [name] [phone number]{Fore.GREEN} - Adds an additional phone to a contact.{Style.RESET_ALL}"
    )
    print(f"all{Fore.GREEN} - Shows all contacts.{Style.RESET_ALL}")
    print(
        f"add-birthday [name] [birthday]{Fore.GREEN} - Adds a birthday to a contact.{Style.RESET_ALL}"
    )
    print(
        f"show-birthday [name]{Fore.GREEN} - Shows the birthday of a contact.{Style.RESET_ALL}"
    )
    print(
        f"birthdays{Fore.GREEN} - Shows upcoming birthdays in the next 7 days.{Style.RESET_ALL}"
    )
    print(f"close, exit, quit{Fore.GREEN} - Exits the program.{Style.RESET_ALL}")
    print(f"help{Fore.GREEN} - Displays a list of available commands.{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}Example usage:{Style.RESET_ALL}")
    print(
        f"add John 1234567890{Fore.GREEN} - Adds a contact named {Fore.CYAN}John{Fore.GREEN} with phone number {Fore.CYAN}1234567890.{Style.RESET_ALL}"
    )
    print(
        f"phone John{Fore.GREEN} - Shows the phone number of {Fore.CYAN}John.{Fore.GREEN}\n"
    )
