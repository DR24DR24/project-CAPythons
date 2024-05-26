import json
import os
import uuid
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import UserDict, defaultdict
from colorama import Fore, Style


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)
    
    def __eq__(self,other):
        return self.value==other.value


    def to_dict(self):
        return self.value


class Name(Field):
    def __init__(self, value: str):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):

    def __init__(self, value: str):
        phone_pattern = re.compile(r"^\+?[1-9]\d{9,14}$")
        if not phone_pattern.match(value):
            raise ValueError("Phone number must be 10-15 digits and may start with +")
        super().__init__(value)


class Email(Field):
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __init__(self, value: str):
        if not self.EMAIL_REGEX.match(value):
            raise ValueError("Invalid email format")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name: Name, **fields: Any):
        self.id = uuid.uuid4()
        self.name = name
        #self.email = None
        self.fields: Dict[str, Field] = {"name": name}
        self.fields.update(fields)

    def add_field(self, field_name: str, field: Field):
        self.fields[field_name] = field

    def remove_field(self, field_name: str):
        if field_name in self.fields:
            del self.fields[field_name]

    def edit_field(self, field_name: str, new_field: Field):
        if field_name in self.fields:
            self.fields[field_name] = new_field

    def matches_criteria(self, keyword: str) -> bool:
        for field in self.fields.values():
            if keyword.lower() in str(field).lower():
                return True
        return False

    def add_phone(self, phone: Phone):
        if "phones" not in self.fields:
            self.fields["phones"] = []
        self.fields["phones"].append(phone)


    # def add_email(self, email: Email):
    #     """Add an email address to the contact."""
    #     self.email = email


    # def edit_email(self, email: Email):
    #     """Edit the email address of the contact."""
    #     self.email = email


    def to_dict(self):
        return {k: [f.to_dict() for f in v] if isinstance(v, list) else v.to_dict() for k, v in self.fields.items()}

    def __str__(self):
        field_strings = []
        for key, value in self.fields.items():
            if isinstance(value, list):
                field_str = "; ".join(str(v) for v in value)
            else:
                field_str = str(value)
            field_strings.append(f"{key}: {field_str}")
        field_str = "; ".join(field_strings)
        return f"{Fore.GREEN}Contact {field_str}{Style.RESET_ALL}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.id] = record

    def delete(self, record_id: uuid.UUID):
        if record_id in self.data:
            del self.data[record_id]
        else:
            raise KeyError(f"Record with ID '{record_id}' not found")

    def find_by_name(self, name: Name) -> Optional[Record]:
        for record in self.data.values():
            if record.fields["name"].value == name.value:
                return record
        return None

    def get_upcoming_birthdays(self) -> List[Dict[str, str]]:
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if "birthday" in record.fields:
                birthday = datetime.strptime(
                    record.fields["birthday"].value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(
                        year=today.year + 1)

                day_difference = (birthday_this_year - today).days
                if 0 <= day_difference <= 7:
                    congratulation_date = birthday_this_year
                    if birthday_this_year.weekday() > 4:
                        congratulation_date += timedelta(
                            days=7 - birthday_this_year.weekday()
                        )

                    upcoming_birthdays.append(
                        {
                            "name": record.fields["name"].value,
                            "congratulation_date": congratulation_date.strftime(
                                "%d.%m.%Y"
                            ),
                        }
                    )

        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


class NotesBook:
    def __init__(self, file_name: str = 'notes.json') -> None:
        self.file_name = file_name
        self.notes: List[Dict[str, str]] = self.load_notes()

    def load_notes(self) -> List[Dict[str, str]]:
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        return []

    def save_notes(self) -> None:
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(self.notes, file, ensure_ascii=False, indent=4)

    def add_note(self, title: str, text: str, tags: List[str]) -> None:
        note_id = str(uuid.uuid4())
        new_note = {
            "id": note_id,
            "title": title,
            "text": text,
            "tags": tags
        }
        self.notes.append(new_note)
        self.save_notes()

    def edit_note(self, note_id: str, new_title: str, new_text: str) -> None:
        for note in self.notes:
            if note['id'] == note_id:
                note['title'] = new_title
                note['text'] = new_text
                self.save_notes()
                return
        raise KeyError(f"Note with ID '{note_id}' does not exist.")

    def delete_note(self, note_id: str) -> None:
        self.notes = [note for note in self.notes if note['id'] != note_id]
        self.save_notes()

    def search_notes(self, keyword: str) -> List[Dict[str, str]]:
        results = []
        for note in self.notes:
            if (keyword.lower() in note['title'].lower() or
                keyword.lower() in note['text'].lower() or
                    any(keyword.lower() in tag.lower() for tag in note['tags'])):
                results.append(note)
        return results

    def find_notes_with_same_tags(self, tag: str) -> None:
        search_tag = f"#{tag}"
        tagged_notes = [
            note for note in self.notes if search_tag in note['tags']]

        if tagged_notes:
            print(f"Notes with tag '{tag}':")
            for note in tagged_notes:
                print(f"  ID: {note['id']}\n  Title: {note['title']}\n  Text: {
                      note['text']}\n  Tags: {', '.join(note['tags'])}\n  {'-'*40}")
        else:
            raise ValueError(f"No notes found with tag '{tag}'.")

    def display_notes(self) -> None:
        if not self.notes:
            raise ValueError("No notes available.")
        else:
            for note in self.notes:
                print(f"ID: {note['id']}\nTitle: {note['title']}\nText: {
                      note['text']}\nTags: {', '.join(note['tags'])}\n{'-'*40}")
