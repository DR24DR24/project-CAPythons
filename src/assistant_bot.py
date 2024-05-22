import sys
from typing import Callable, Dict, List, Optional
from collections import UserDict
from colorama import Fore, Style, init
from datetime import datetime, timedelta
import pickle

#review: I strongly approve of documenting code.
#However, I propose to distinguish between two situations:
#1. This is a library that will be used heavily by other programmers. 
#In this case, such detailed documentation is welcome.
#2. This is not a library for general use. 
#Then I think a comment like the first line brings the necessary clarity, 
#everything that follows is simply a retelling of the code in other words.
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

#review: Well thought out error handling
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
        If the phone number is not 10 digits long.
    """

    def __init__(self, value: str):
        if not value.isdigit() or len(value.strip()) != 10:
            raise ValueError("Phone number must be 10 digits")
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
            #review: We need to think about doing this and other checks in one place
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

    def add_phone(self, phone: Phone):
        """Add a phone number to the contact."""
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        """Remove a phone number from the contact."""
        for p in self.phones:
#review Alternative (fewer lines of code and faster execution I think):
# phone_objects=[x for x in self.phones if x.value==phone]
            if p.value == phone.value:
                self.phones.remove(p)
                break
#review: bug
    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        """Edit an existing phone number in the contact."""
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday: Birthday):
        """Add a birthday to the contact."""
        self.birthday = birthday

    def __str__(self):
        """Return the string representation of the contact."""
        phones = "; ".join([str(phone) for phone in self.phones])
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
#review: Messages for phones and birthdays are not generated uniformly      
        return f"Contact name: {self.name}, phones: {phones}{birthday}"


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
#review: leap year is not taken into account
    def get_upcoming_birthdays(self) -> List[Dict[str, str]]:
        """Get upcoming birthdays within the next 7 days for contacts."""
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                day_difference = (birthday_this_year - today).days
                if 0 <= day_difference <= 7:
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

#review: Different colors help the user navigate messages
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

#review: It would be nice to mark all print operators a level or two higher, 
#that is, return an error message when calling the handle_command function
@input_error
def handle_command(
    command_handlers: Dict[str, Callable[[Optional[AddressBook],Optional[List[str]]], None]],
    command: str,
    ab:AddressBook,
    args: Optional[List[str]]
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
        command_handlers[command](args,adb=ab)
    else:
        raise TypeError(f"Unknown command '{command}'")


@input_error
def hello() -> None:
    """Greet the user."""
    print(f"{Fore.CYAN}How can I help you?{Style.RESET_ALL}")

@input_error
def add_contact(*args,**kwargs) -> None:
    """Add a new contact.

    Parameters
    ----------
    contacts : AddressBook
        The address book containing contacts.
    args : str
        The name and phone number of the new contact.
    """
    contacts=kwargs["adb"]
    if len(args[0]) != 2:
       raise ValueError("Usage: add [name] [phone number]")
    name, phone = args[0]
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
def add_birthday(args: List[str], address_book: AddressBook):
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
def show_birthday(args: List[str], address_book: AddressBook):
    """Show the birthday of a contact."""
    if len(args) != 1:
        raise ValueError("Usage: show-birthday [name]")
    name = args[0]
    record = address_book.find(Name(name))
    if record:
        if record.birthday:
            print(
                f"{Fore.GREEN}Birthday of {Fore.CYAN}{name}{Fore.GREEN}: {Fore.CYAN}{record.birthday.value}{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.YELLOW}No birthday set for {Fore.CYAN}{name}{Fore.YELLOW}.{Style.RESET_ALL}"
            )
    else:
        raise KeyError(f"Name '{name}' not found.")


@input_error
def birthdays(args: List[str], address_book: AddressBook):
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


def handle_exit(*args) -> None:
    """Exit the program, saving the address book to a file."""
    save_data(args[0])  # Save the address book before exiting
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

#rewiew: help is a good solution
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
#review
#I personally like this design; 
#it can save the number of lines of code and execution time. 
#However, it is more complicated than if/else. 
#Note the possibility of passing arguments using *args *kwargs 
#or not passing arguments at all by declaring these functions as class methods
def main():
    """Main function that runs the command line interface for an assistant bot."""
    address_book = load_data()  # Load the address book from the file
    command_handlers: Dict[str, Callable[[Optional[AddressBook], Optional[List[str]]], None]] = {
        "hello": hello,
        "add":  add_contact,
        "change": lambda args: change_contact(address_book, *args),
        "phone": lambda args: show_phone(address_book, *args),
        "all": lambda _: show_all_contacts(address_book),
        "close": lambda _: handle_exit(address_book),
        "exit": handle_exit,
        "quit": lambda _: handle_exit(address_book),
        "help":  help_command,
        "add-birthday": lambda args: add_birthday(args, address_book),
        "show-birthday": lambda args: show_birthday(args, address_book),
        "birthdays": lambda args: birthdays(args, address_book),
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
        handle_command(command_handlers, command, address_book, args)


if __name__ == "__main__":
    main()
