import json
import uuid
from typing import Dict
from app.entities import Record, AddressBook, Name, Phone, Birthday, Field


class FileStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_contacts(self, contacts: Dict[uuid.UUID, Record]) -> None:
        data = {
            str(record_id): record.to_dict() for record_id, record in contacts.items()
        }
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_contacts(self) -> Dict[uuid.UUID, Record]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            contacts = {}
            for record_id, fields in data.items():
                name = Name(fields.pop("name"))
                record = Record(name)
                record.id = uuid.UUID(record_id)
                for field_name, field_value in fields.items():
                    print(type(field_value))
                    field_class = globals().get(field_name.capitalize(), Field)
                    if type(field_value)==list:
                        list_of_object=[field_class(items) for items in field_value]
                        record.fields[field_name] = list_of_object
                    # if field_name == "phones":
                    #     phones = [Phone(phone) for phone in field_value]
                    #     record.fields["phones"] = phones
                    #elif field_name == "phones"
                    else:
                        field_class = globals().get(field_name.capitalize(), Field)
                        record.fields[field_name] = field_class(field_value)
                contacts[record.id] = record
            return contacts
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}
