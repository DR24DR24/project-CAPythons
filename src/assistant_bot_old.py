import sys
from typing import Callable, Dict, List, Optional
from collections import UserDict
from colorama import Fore, Style, init
from datetime import datetime, timedelta
import pickle
import re

class Field:
    """Base class for all fields in a record.

    Parameters
    ----------
    value : str
        The value of the field.
    """

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        """Return the string representation of the field.

        Returns
        -------
        str
            The string representation of the field value.
        """
        return str(self.value)


class Name(Field):
    """Class for storing contact names. Inherits from Field.

    Parameters
    ----------
    value : str
        The name of the contact.

    Raises
    ------
    ValueError
        If the name is empty.
    """

    def __init__(self, value: str):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """Class for storing phone numbers. Inherits from Field.

    Parameters
    ----------
    value : str
        The phone number.

    Raises
    ------
    ValueError
        Phone number must be 10-15 digits and may start with +.
    """

    def __init__(self, value: str):
        phone_pattern = re.compile(r"^\+?[1-9]\d{9,14}$")
        if not phone_pattern.match(value):
            raise ValueError("Phone number must be 10-15 digits and may start with +")
        super().__init__(value)

class Email(Field):
    """Class for storing and validating email addresses. Inherits from Field.

    Parameters
    ----------
    value : str
        The email address.

    Raises
    ------
    ValueError
        If the email format is incorrect.
    """
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __init__(self, value: str):
        if not self.EMAIL_REGEX.match(value):
            raise ValueError("Invalid email format")
        super().__init__(value)


class Address(Field):
    """Class for storing contact address. Inherits from Field.

                Parameters
                ----------
                value : str
                    The name of the address.

                Raises
                ------
                ValueError
                    If the address is empty.
                """

    def __init__(self, value: str):
        if not value:
            raise ValueError("Address cannot be empty.")
        super().__init__(value)


class Birthday(Field):
    """Class for storing and validating birthdays. Inherits from Field.

    Parameters
    ----------
    value : str
        The birthday in DD.MM.YYYY format.

    Raises
    ------
    ValueError
        If the date format is incorrect.
    """

    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    """Class for storing contact information, including name, phone numbers, and birthday.

    Parameters
    ----------
    name : Name
        The name of the contact.
    """

    def __init__(self, name: Name):
        self.name = name
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def add_phone(self, phone: Phone):
        """Add a phone number to the contact."""
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        """Remove a phone number from the contact."""
        for p in self.phones:
            if p.value == phone.value:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        """Edit an existing phone number in the contact."""
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_email(self, email: Email):
        """Add an email address to the contact."""
        self.email = email

    def edit_email(self, email: Email):
        """Edit the email address of the contact."""
        self.email = email

    def add_address(self, address: Address):
        """Add the address of the contact"""
        self.address = address

    def edit_address(self, address: Address):
        """Edit the address of the contact"""
        self.address = address

    def add_birthday(self, birthday: Birthday):
        """Add a birthday to the contact."""
        self.birthday = birthday

    def __str__(self):
        """Return the string representation of the contact."""
        phones = "; ".join([str(phone) for phone in self.phones])
        birthday = (
            f"{Fore.GREEN}, birthday: {Fore.CYAN}{self.birthday}{Style.RESET_ALL}"
            if self.birthday
            else ""
        )
        return f"{Fore.GREEN}Contact name: {Fore.CYAN}{self.name}{Fore.GREEN}, phones: {Fore.CYAN}{phones}{birthday}{Style.RESET_ALL}"


class AddressBook(UserDict):
    """Class for storing and managing contact records."""

    def add_record(self, record: Record):
        """Add a record to the address book."""
        self.data[record.name.value] = record

    def delete(self, name: Name):
        """Delete a record from the address book by name."""
        if name.value in self.data:
            del self.data[name.value]
        else:
            raise KeyError(f"Record with name '{name}' not found")

    def find(self, name: Name) -> Optional[Record]:
        """Find a record in the address book by name."""
        return self.data.get(name.value, None)

    def get_upcoming_birthdays(self, set_number: int) -> List[Dict[str, str]]:
        """Get upcoming birthdays within a set amount of days for contacts."""
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                day_difference = (birthday_this_year - today).days
                if 0 <= day_difference <= set_number:
                    congratulation_date = birthday_this_year
                    if (
                        birthday_this_year.weekday() > 4
                    ):  # If Saturday (5) or Sunday (6)
                        congratulation_date += timedelta(
                            days=7 - birthday_this_year.weekday()
                        )

                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "congratulation_date": congratulation_date.strftime(
                                "%d.%m.%Y"
                            ),
                        }
                    )

        return upcoming_birthdays

    def __str__(self):
        """Return the string representation of the address book."""
        return "\n".join(str(record) for record in self.data.values())


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


def parse_input(user_input: str) -> tuple[str, List[str]]:
    """Parse the user input into a command and arguments.

    Parameters
    ----------
    user_input : str
        The input string from the user.

    Returns
    -------
    tuple[str, List[str]]
        The command and a list of arguments.
    """
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
    """Handle the given command using the appropriate handler.

    Parameters
    ----------
    command_handlers : Dict[str, Callable[[Optional[List[str]]], None]]
        A dictionary mapping commands to their handlers.
    command : str
        The command to handle.
    args : Optional[List[str]]
        The arguments for the command.
    """
    if command in command_handlers:
        if args is None:
            args = []  # Use an empty list if no arguments are provided
        command_handlers[command](args)
    else:
        raise TypeError(f"Unknown command '{command}'")


@input_error
def hello() -> None:
    """Greet the user."""
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
        phone_pattern = re.compile(r"^\+?[1-9]\d{9,14}$")
        if not phone_pattern.match(new_phone):
            raise ValueError("Phone number must be 10-15 digits and may start with +")
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
def add_email_to_contact(contacts: AddressBook, *args: str) -> None:
    """Add an email to a contact."""
    if len(args) != 2:
        raise ValueError("Usage: add-email [name] [email]")
    name, email = args
    record = contacts.find(Name(name))
    if record:
        record.add_email(Email(email))
        print(
            f"{Fore.GREEN}Email for {Fore.CYAN}{name}{Fore.GREEN} set to {Fore.CYAN}{email}{Style.RESET_ALL}"
        )
    else:
        raise KeyError(f"Name '{name}' not found.")

@input_error
def edit_email_of_contact(contacts: AddressBook, *args: str) -> None:
    """Edit the email of a contact."""
    if len(args) != 2:
        raise ValueError("Usage: edit-email [name] [new email]")
    name, email = args
    record = contacts.find(Name(name))
    if record:
        record.edit_email(Email(email))
        print(
            f"{Fore.GREEN}Email for {Fore.CYAN}{name}{Fore.GREEN} changed to {Fore.CYAN}{email}{Style.RESET_ALL}"
        )
    else:
        raise KeyError(f"Name '{name}' not found.")

@input_error
def add_address_to_contact(contacts: AddressBook, *args: str) -> None:
    """Add the address to a contact."""
    if len(args) <= 2:
        raise ValueError("Usage: add-address [name] [address separated with spaces]")
    name = args[0]
    address_str = ", ".join([str(address_part) for address_part in args[1:]])
    record = contacts.find(Name(name))
    if record:
        record.add_address(Address(address_str))
        print(
            f"{Fore.GREEN}Address for {Fore.CYAN}{name}{Fore.GREEN} set to {Fore.CYAN}{address_str}{Style.RESET_ALL}"
        )
    else:
        raise KeyError(f"Name '{name}' not found.")

@input_error
def edit_address_of_contact(contacts: AddressBook, *args: str) -> None:
    """Edit the address of a contact"""
    if len(args) <= 2:
        raise ValueError("Usage: edit-address [name] [address separated with spaces]")
    name = args[0]
    address_str = ", ".join([str(address_part) for address_part in args[1:]])
    record = contacts.find(Name(name))
    if record:
        record.edit_address(Address(address_str))
        print(
            f"{Fore.GREEN}Address for {Fore.CYAN}{name}{Fore.GREEN} changed to {Fore.CYAN}{address_str}{Style.RESET_ALL}"
        )

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
def birthdays(address_book: AddressBook, *args: str) -> None:
    """Show the upcoming birthdays within a set amount of days."""
    if len(args) != 1:
        raise ValueError("Usage: birthdays [number of days]")
    set_number = int(args[0])
    upcoming_birthdays = address_book.get_upcoming_birthdays(set_number)
    if upcoming_birthdays:
        for entry in upcoming_birthdays:
            print(
                f"{Fore.GREEN}{entry['name']}: {Fore.CYAN}{entry['congratulation_date']}{Style.RESET_ALL}"
            )
    else:
        print(
            f"{Fore.YELLOW}No upcoming birthdays in {set_number} days.{Style.RESET_ALL}"
        )


def handle_exit(address_book: AddressBook) -> None:
    """Exit the program, saving the address book to a file."""
    save_data(address_book)  # Save the address book before exiting
    print(f"{Fore.GREEN}{Style.BRIGHT}Good bye!{Style.RESET_ALL}")
    sys.exit()


def save_data(book: AddressBook, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl") -> AddressBook:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file is not found


def help_command():
    """Display the help information with available commands."""
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
    print(f"add-email [name] [email]{Fore.GREEN} - Adds an email to a contact.{Style.RESET_ALL}"
    )
    print(f"edit-email [name] [new email]{Fore.GREEN} - Edits the email of a contact.{Style.RESET_ALL}"
    )
    print(f"add-address [name] [address]{Fore.GREEN} - Adds an address to a contact.{Style.RESET_ALL}"
    )
    print(f"edit-address [name] [address]{Fore.GREEN} - Edits the address of a contact{Style.RESET_ALL}"
    )
    print(f"all{Fore.GREEN} - Shows all contacts.{Style.RESET_ALL}")
    print(
        f"add-birthday [name] [birthday]{Fore.GREEN} - Adds a birthday to a contact.{Style.RESET_ALL}"
    )
    print(
        f"show-birthday [name]{Fore.GREEN} - Shows the birthday of a contact.{Style.RESET_ALL}"
    )
    print(
        f"birthdays [number of days]{Fore.GREEN} - Shows upcoming birthdays in a set amount of days.{Style.RESET_ALL}"
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


def main():
    """Main function that runs the command line interface for an assistant bot."""
    address_book = load_data()  # Load the address book from the file
    command_handlers: Dict[str, Callable[[Optional[List[str]]], None]] = {
        "hello": lambda _: hello(),
        "add": lambda args: add_contact(address_book, *args),
        "change": lambda args: change_contact(address_book, *args),
        "phone": lambda args: show_phone(address_book, *args),
        "add-phone": lambda args: add_phone_to_contact(address_book, *args),
        "add-email": lambda args: add_email_to_contact(address_book, *args),
        "edit-email": lambda args: edit_email_of_contact(address_book, *args),
        "add-address": lambda args: add_address_to_contact(address_book, *args),
        "edit-address": lambda args: edit_address_of_contact(address_book, *args),
        "all": lambda _: show_all_contacts(address_book),
        "add-birthday": lambda args: add_birthday(address_book, *args),
        "show-birthday": lambda args: show_birthday(address_book, *args),
        "birthdays": lambda _: birthdays(address_book, *args),
        "close": lambda _: handle_exit(address_book),
        "exit": lambda _: handle_exit(address_book),
        "quit": lambda _: handle_exit(address_book),
        "help": lambda _: help_command(),
    }

    init(autoreset=True)  # Initialize colorama

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
