from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import UserDict
from colorama import Fore, Style


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
            if p.value == phone.value:
                self.phones.remove(p)
                break

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
