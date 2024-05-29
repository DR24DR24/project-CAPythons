from app import command_registry
from app.interfaces import Command, FieldCommand
from app.entities import (
    Field,
    Name,
    Phone,
    Birthday,
    Record,
    AddressBook,
    NotesBook,
    Email,
    Address,
)
from infrastructure.storage import FileStorage
from presentation.messages import Message
from app.command_registry import register_command, get_command
from app.settings import Settings
from typing import Callable
from colorama import Fore, Style


# Initialize settings
settings = Settings()

# Language mapping
LANGUAGE_MAP = {
    "en": {"en": "English", "ua": "Ukrainian", "de": "German"},
    "ua": {"en": "англійська", "ua": "українська", "de": "німецька"},
    "de": {"en": "Englisch", "ua": "Ukrainisch", "de": "Deutsch"},
}


# Decorator for handling errors in command functions
def input_error(handler: Callable) -> Callable:
    """Decorator for handling errors in command functions."""

    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except TypeError as e:
            print(
                f"{Fore.RED}Error: Incorrect command.\n{Fore.MAGENTA}{e}{Style.RESET_ALL}"
            )
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
def handle_command(
    command: str, address_book: AddressBook, notes_book: NotesBook, *args: str
) -> None:
    """Handles the user command by calling the corresponding method."""
    cmd = get_command(command)
    if cmd:
        cmd_instance = cmd(notes_book if "note" in command else address_book)
        cmd_instance.execute(*args)
    else:
        Message.error("incorrect_command", command=command)


@register_command("hello")
class HelloCommand(Command):
    description = {
        "en": "Displays a greeting message.",
        "ua": "Виводить вітання.",
    }

    def execute(self, *args: str) -> None:
        """Displays a greeting message."""
        Message.info("greeting")


@register_command("all")
class ShowAllContactsCommand(Command):
    description = {
        "en": "Shows all contacts in the address book.",
        "ua": "Виводить всі контакти.",
    }

    def execute(self, *args: str) -> None:
        """Shows all contacts in the address book."""
        if self.book_type.data:
            for record in self.book_type.data.values():
                print(str(record))
        else:
            raise IndexError("No contacts available.")


# Contact commands
@register_command("add")
class AddContactCommand(Command):
    description = {
        "en": "Adds a new contact to the address book.",
        "ua": "Додає новий контакт у адресну книгу.",
    }
    example = {"en": "[name] [phone]", "ua": "[ім'я] [телефон]"}
    expected_fields = [Name]

    def execute(self, *args: str) -> None:
        """Adds a new contact to the address book."""
        if len(args) != 2:
            Message.error("incorrect_arguments")
            return
        name, phone = args
        record = self.book_type.find_by_name(Name(name))
        if record:
            if any(p.value == phone for p in record.fields.get("phones", [])):
                Message.warning("contact_exists", name=name, phone=phone)
            else:
                if not record.fields.get("phones"):
                    record.fields["phones"] = []
                record.fields["phones"].append(Phone(phone))
                Message.info("phone_added", name=name, phone=phone)
        else:
            new_record = Record(Name(name))
            new_record.add_phone(Phone(phone))
            self.book_type.add_record(new_record)
            Message.info("contact_added", name=name, phone=phone)


@register_command("delete")
class DeleteCommand(Command):
    description = {
        "en": "Delete contact.",
        "ua": "Видаляє контакт.",
    }
    example = {"en": "[name]", "ua": "[ім'я]"}
    expected_fields = [Name]

    def execute(self, *args: str) -> None:
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        name = args[0]
        record = self.book_type.find_by_name(Name(name))
        if not record:
            Message.error("contact_not_found", name=name)
            return
        self.book_type.delete(record.id)
        Message.info("contact_deleted", name=name)


@register_command("add-phone")
class AddPhoneCommand(FieldCommand):
    description = {
        "en": "Adds a new phone number to an existing contact.",
        "ua": "Додає новий номер телефону до наявного контакту.",
    }
    example = {"en": "[name] [phone]", "ua": "[ім'я] [телефон]"}
    expected_fields = [Name, Phone]

    def create_field(self, *args: str) -> Field:
        return Phone(args[0])

    def execute_field(self, record: Record, field: Field, **kwargs) -> None:
        """Adds a phone number to an existing contact."""
        if "phones" not in record.fields:
            record.fields["phones"] = []
        elif isinstance(record.fields["phones"], list):
            for existing_phone in record.fields["phones"]:
                if existing_phone.value == field.value:
                    Message.error(
                        "contact_exists", name=record.name.value, phone=field.value
                    )
                    return
        record.add_phone(field)
        Message.info("phone_added", name=record.name.value, value=field.value)


@register_command("edit-phone")
class ChangeContactCommand(Command):
    description = {
        "en": "Changes the phone number of an existing contact.",
        "ua": "Змінює номер телефону існуючого контакту.",
    }
    example = {
        "en": "[name] [old phone] [new phone]",
        "ua": "[ім'я] [попередній номер] [новий]",
    }
    expected_fields = [Name, Phone]

    def execute(self, *args: str) -> None:
        """Changes the phone number of an existing contact."""
        if len(args) != 3:
            Message.error("incorrect_arguments")
            return
        name, old_phone, new_phone = args
        record = self.book_type.find_by_name(Name(name))
        if not record or "phones" not in record.fields:
            Message.error("contact_not_found", name=name)
            return

        try:
            phone_index = record.fields["phones"].index(Phone(old_phone))
            record.fields["phones"][phone_index] = Phone(new_phone)
            Message.info(
                "phone_updated", name=name, old_phone=old_phone, new_phone=new_phone
            )
        except ValueError:
            Message.error("phone_not_found", name=name, phone=old_phone)


@register_command("show-phone")
class ShowPhoneCommand(Command):
    description = {
        "en": "Shows the phone number of a contact.",
        "ua": "Показує номер телефону контакту.",
    }
    example = {"en": "[name]", "ua": "[ім'я]"}
    expected_fields = [Name]

    def execute(self, *args: str) -> None:
        """Shows the phone number of a contact."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        name = args[0]
        record = self.book_type.find_by_name(Name(name))
        if not record:
            Message.error("contact_not_found", name=name)
            return
        if "phones" in record.fields:
            phones = "; ".join(phone.value for phone in record.fields["phones"])
            Message.info("phone_info", name=record.name.value, phone=phones)
        else:
            Message.error("phone_not_found", name=record.name.value)


@register_command("add-email")
class AddEmailToContactCommand(FieldCommand):
    description = {
        "en": "Adds an email to a contact.",
        "ua": "Додає електронну пошту до контакту.",
    }
    example = {"en": "[name] [email]", "ua": "[ім'я] [поштова адреса]"}
    expected_fields = [Name]

    def create_field(self, *args: str) -> Field:
        return Email(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds an email to an existing contact."""
        if "emails" not in record.fields:
            record.fields["emails"] = []
        record.fields["emails"].append(field)
        Message.info("email_added", name=record.name.value, value=field.value)


@register_command("show-email")
class ShowEmailCommand(Command):
    description = {
        "en": "Shows the email address(es) of a contact.",
        "ua": "Показує електронну адресу(и) контакту.",
    }
    example = {"en": "[name]", "ua": "[ім'я]"}
    expected_fields = [Name]

    def execute(self, *args: str) -> None:
        """Shows the email address(es) of a contact."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        name = args[0]
        record = self.book_type.find_by_name(Name(name))
        if not record:
            Message.error("contact_not_found", name=name)
            return
        if "emails" in record.fields:
            emails = "; ".join(email.value for email in record.fields["emails"])
            Message.info("email_info", name=record.name.value, email=emails)
        else:
            Message.error("email_not_found", name=record.name.value)


@register_command("edit-email")
class EditEmailOfContactCommand(ChangeContactCommand):
    description = {
        "en": "Edits the email of a contact.",
        "ua": "Редагує електронну пошту контакту.",
    }
    example = {
        "en": "[name] [old email] [new email]",
        "ua": "[ім'я] [старий email] [новий email]",
    }
    expected_fields = [Name, Email]

    def execute(self, *args: str) -> None:
        """Edits the email of a contact."""
        if len(args) != 3:
            Message.error("incorrect_arguments")
            return
        name, old_email, new_email = args
        record = self.book_type.find_by_name(Name(name))
        if not record or "emails" not in record.fields:
            Message.error("contact_not_found", name=name)
            return

        try:
            email_index = record.fields["emails"].index(Email(old_email))
            record.fields["emails"][email_index] = Email(new_email)
            Message.info(
                "email_updated", name=name, old_email=old_email, new_email=new_email
            )
        except ValueError:
            Message.error("email_not_found", name=name, email=old_email)


@register_command("add-address")
class AddAddressToContactCommand(FieldCommand):
    description = {
        "en": "Adds an address to a contact.",
        "ua": "Додає адресу до контакту.",
    }

    example = {"en": "[name] [address]", "ua": "[ім'я] [адреса]"}
    expected_fields = [Name]

    def create_field(self, *args: str) -> Field:
        return Address(args)

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds an address to an existing contact."""
        record.add_field("address", field)
        Message.info("address_added", name=record.name.value, address=field.value)


@register_command("edit-address")
class EditAddressOfContactCommand(Command):
    description = {
        "en": "Edits the address of a contact.",
        "ua": "Редагує адресу контакту.",
    }
    example = {
        "en": "[name] [previous address] [new address]",
        "ua": "[ім'я] [попередня адреса] [нова адреса]",
    }
    expected_fields = [Name, Address]

    def execute(self, *args: str) -> None:
        """Edits the address of a contact."""
        if len(args) < 2:
            Message.error("incorrect_arguments")
            return
        name, *address = args
        record = self.book_type.find_by_name(Name(name))

        if record:
            record.edit_field("address", Address(address))
            Message.info("address_changed", name=name, address=", ".join(address))
        else:
            Message.error("contact_not_found", name=name)


@register_command("add-birthday")
class AddBirthdayCommand(FieldCommand):
    description = {
        "en": "Adds a birthday to an existing contact.",
        "ua": "Додає день народження до наявного контакту.",
    }
    example = {"en": "[name] [birthday]", "ua": "[ім'я] [дата народження]"}
    expected_fields = [Name]

    def create_field(self, *args: str) -> Field:
        return Birthday(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds a birthday to an existing contact."""
        record.add_field("birthday", field)
        Message.info("birthday_set", name=record.name.value, birthday=field.value)


@register_command("edit-birthday")
class EditBirthdayOfContactCommand(FieldCommand):
    description = {
        "en": "Edits the birthday of a contact.",
        "ua": "Редагує день народження контакту.",
    }
    example = {
        "en": "[name] [new birthday]",
        "ua": "[ім'я] [новий день народження]",
    }
    expected_fields = [Name, Birthday]

    def create_field(self, *args: str) -> Field:
        return Birthday(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Edits the birthday of an existing contact."""
        record.edit_field("birthday", field)
        Message.info("birthday_updated", name=record.name.value, birthday=field.value)


@register_command("birthdays")
class ShowUpcomingBirthdays(Command):
    description = {
        "en": "Shows all upcoming birthdays in a set amount of days.",
        "ua": "Виводить усі дні народження протягом заданої кількості днів.",
    }
    example = {"en": "[number of days]", "ua": "[кількість днів]"}

    def execute(self, *args: str) -> None:
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        set_number = int(args[0])
        upcoming_birthdays = self.book_type.get_upcoming_birthdays(set_number)
        if upcoming_birthdays:
            for entry in upcoming_birthdays:
                Message.info(
                    "upcoming_birthdays",
                    name=entry["name"],
                    congratulation_date=entry["congratulation_date"],
                )
        else:
            Message.error("no_upcoming_birthdays", set_number=set_number)


@register_command("search-contact")
class SearchContactsCommand(Command):
    description = {
        "en": "Searches for contacts matching the given criteria.",
        "ua": "Шукає контакти за заданими критеріями.",
    }
    example = {"en": "[search string]", "ua": "[пошуковий запит]"}

    def execute(self, *args: str) -> None:
        """Searches for contacts matching the given criteria."""
        if len(args) < 1:
            Message.error("incorrect_arguments")
            return
        keyword = " ".join(args).lower()
        results = []
        for record in self.book_type.values():
            for field in record.fields.values():
                if isinstance(field, list):
                    if any(keyword in str(item).lower() for item in field):
                        results.append(record)
                        break
                elif keyword in str(field).lower():
                    results.append(record)
                    break

        if results:
            for record in results:
                print(record)
        else:
            Message.info("no_results_found")


# Note commands
@register_command("add-note")
class AddNoteCommand(Command):
    description = {
        "en": "Adds a new note.",
        "ua": "Додає нову нотатку.",
    }
    example = {"en": "[title] [text] [tags]", "ua": "[заголовок] [текст] [теги]"}

    def execute(self, *args: tuple) -> None:
        """Adds a new note."""
        if len(args) < 2:
            Message.error("incorrect_arguments")
            return
        title, *rest = args
        text = " ".join(rest)
        tags = [tag for tag in rest if tag.startswith("#")]
        self.book_type.add_note(title, text, tags)
        Message.info("note_added", title=title)


@register_command("edit-note")
class EditNoteCommand(Command):
    description = {
        "en": "Edits an existing note.",
        "ua": "Редагує наявну нотатку.",
    }
    example = {"en": "[id] [title] [text]", "ua": "[ID] [заголовок] [текст]"}

    def execute(self, *args: tuple) -> None:
        """Edits an existing note."""
        if len(args) < 3:
            Message.error("incorrect_arguments")
            return
        id_note, title, *text = args
        text = " ".join(text)
        self.book_type.edit_note(id_note, title, text)
        Message.info("note_updated", title=title)


@register_command("delete-note")
class DeleteNoteCommand(Command):
    description = {
        "en": "Deletes an existing note.",
        "ua": "Видаляє наявну нотатку.",
    }
    example = {"en": "[id]", "ua": "[ID]"}

    def execute(self, *args: tuple) -> None:
        """Deletes an existing note."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        note_id = args[0]
        self.book_type.delete_note(note_id)
        Message.info("note_deleted", title=note_id)


@register_command("find-tag-note")
class FindNoteCommand(Command):
    description = {
        "en": "Finds a note by its tag.",
        "ua": "Знаходить нотатку за тегом.",
    }
    example = {"en": "[tag]", "ua": "[тег]"}

    def execute(self, *args: tuple) -> None:
        """Finds a note by its tag."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        tag = args[0]
        notes = self.book_type.find_notes_with_same_tags(tag)
        for note in notes:
            print(
                f"\nID: {note['id']}\nTitle: {note['title']}\nText: {note['text']}\nTags: {', '.join(note['tags'])}\n"
            )
            print("-" * 40)


@register_command("search-notes")
class SearchNotesCommand(Command):
    description = {
        "en": "Searches for notes matching the given criteria.",
        "ua": "Шукає нотатки за заданими критеріями.",
    }
    example = {"en": "[search string]", "ua": "[пошуковий запит]"}

    def execute(self, *args: str) -> None:
        """Searches for notes matching the given criteria."""
        if len(args) < 1:
            Message.error("incorrect_arguments")
            return
        keyword = " ".join(args)
        results = self.book_type.search_notes(keyword)
        if results:
            for note in results:
                print(
                    f"\nID: {note['id']}\nTitle: {note['title']}\nText: {note['text']}\nTags: {', '.join(note['tags'])}\n"
                )
                print("-" * 40)
        else:
            Message.info("no_results_found")


@register_command("display-notes")
class DisplayNotesCommand(Command):
    description = {"en": "Displays all notes.", "ua": "Виводить всі нотатки."}

    def execute(self, *args: str) -> None:
        """Displays all notes."""
        notes = self.book_type.display_notes()
        for note in notes:
            print(
                f"\nID: {note['id']}\nTitle: {note['title']}\nText: {note['text']}\nTags: {', '.join(note['tags'])}\n"
            )
            print("-" * 40)


# Utility commands
@register_command("exit")
@register_command("close")
class ExitCommand(Command):
    description = {
        "en": "Saves the address book and exits the program.",
        "ua": "Зберігає адресну книгу та виходить з програми.",
    }

    def execute(self, *args: str) -> None:
        """Saves the address book and exits the program."""
        storage = FileStorage("addressbook.json")
        storage.save_contacts(self.book_type.data)
        Message.info("exit_message")
        Command.exit_command_flag = True  # sys.exit()


@register_command("help")
class HelpCommand(Command):
    description = {
        "en": "Displays this help message.",
        "ua": "Виводить це повідомлення про доступні команди.",
        "de": "Zeigt diese Hilfenachricht an.",
    }

    def execute(self, *args: str) -> None:
        """Displays this help message."""
        headers = {
            "en": ("Command", "Parameters", "Description"),
            "ua": ("Команда", "Параметри", "Опис"),
            "de": ("Befehl", "Parameter", "Beschreibung"),
        }
        language = settings.language
        max_command_len = max(
            len(command_name)
            for command_name in command_registry.command_registry.keys()
        )
        max_example_len = max(
            (
                len(command_class.example.get(language, ""))
                if hasattr(command_class, "example")
                else 0
            )
            for command_class in command_registry.command_registry.values()
        )

        command_header, example_header, description_header = headers[language]
        print(
            f"\n{Style.BRIGHT}{Fore.CYAN}{command_header.ljust(max_command_len)}\t{example_header.ljust(max_example_len)}\t{description_header}{Style.RESET_ALL}"
        )

        for command_name, command_class in command_registry.command_registry.items():
            description = command_class.description.get(
                language
            ) or command_class.description.get("en", "No description available.")
            example = (
                command_class.example.get(language, "")
                if hasattr(command_class, "example")
                else ""
            )

            command_str = f"{Style.BRIGHT}{Fore.WHITE}{command_name.ljust(max_command_len)}{Style.RESET_ALL}"
            example_str = (
                f"{Fore.WHITE}{example.ljust(max_example_len)}{Style.RESET_ALL}"
            )
            description_str = f"{Fore.GREEN}{description}{Style.RESET_ALL}"

            print(f"{command_str}\t{example_str}\t{description_str}")

        print()


@register_command("set-language")
class SetLanguageCommand(Command):
    description = {
        "en": "Sets the application language.",
        "ua": "Встановлює мову застосунку.",
        "de": "Stellt die Anwendungssprache ein.",
    }

    example = {
        "en": "['en', 'ua', 'de']",
        "ua": "['en', 'ua', 'de']",
        "de": "['en', 'ua', 'de']",
    }

    def execute(self, *args: str) -> None:
        """Sets the application language."""
        if len(args) != 1:
            available_languages = ", ".join(LANGUAGE_MAP[settings.language].keys())
            Message.error("incorrect_arguments")
            print(f"Available languages: {available_languages}")
            return
        language = args[0]
        if language not in LANGUAGE_MAP["en"]:  # зміна з settings.language на "en"
            Message.error("incorrect_arguments")
            available_languages = ", ".join(LANGUAGE_MAP[settings.language].keys())
            print(f"Available languages: {available_languages}")
            return
        settings.set_language(language)
        Message.load_templates(language)
        user_friendly_language_name = LANGUAGE_MAP[language][language]
        Message.info("set_language", language=user_friendly_language_name)
