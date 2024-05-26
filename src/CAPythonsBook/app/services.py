from app import command_registry
import re
from app.interfaces import Command, FieldCommand
from app.entities import Field, Name, Phone, Email, Address, Birthday, Record, AddressBook, NotesBook
from infrastructure.storage import FileStorage
from presentation.messages import Message
from app.command_registry import register_command, get_command
from infrastructure.storage import FileStorage
from app.settings import Settings
from typing import Callable
from colorama import Fore, Style
import sys


# Initialize settings
settings = Settings()

# Language mapping
LANGUAGE_MAP = {
    "en": {"en": "English", "uk": "Ukrainian"},
    "uk": {"en": "англійська", "uk": "українська"},
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
def handle_command(command: str, address_book: AddressBook, notes_book: NotesBook, *args: str) -> None:
    """Handles the user command by calling the corresponding method."""
    cmd = get_command(command)
    if cmd:
        cmd_instance = cmd(
            notes_book if 'note' in command else address_book)
        # cmd_instance = cmd(command.includes('note') ? notes_book: address_book)
        cmd_instance.execute(*args)
    else:
        Message.error("incorrect_command", command=command)


@register_command("hello")
class HelloCommand(Command):
    description = {
        "en": "Displays a greeting message.",
        "uk": "Виводить вітання.",
    }

    def execute(self, *args: str) -> None:
        """Displays a greeting message."""
        Message.info("greeting")


@register_command("add")
class AddContactCommand(Command):
    description = {
        "en": "Adds a new contact to the address book.",
        "uk": "Додає новий контакт у адресну книгу.",
    }
    example = {
        "en": "[name] [phone]",
        "uk": "[ім'я] [телефон]"
    }

    def execute(self, *args: str) -> None:
        """Adds a new contact to the address book."""
        if len(args) != 2:
            Message.error("incorrect_arguments")
            return
        name, phone = args
        record = self.book_type.find_by_name(Name(name))
        if record:
            if any(p.value == phone for p in record.phones):
                Message.warning("contact_exists", name=name, phone=phone)
            else:
                current_phone = record.phones[0].value if record.phones else "No phone"
                Message.warning("contact_exists", name=name,
                                phone=current_phone)
        else:
            new_record = Record(Name(name))
            new_record.add_phone(Phone(phone))
            self.book_type.add_record(new_record)
            Message.info("contact_added", name=name, phone=phone)


@register_command("change")
class ChangeContactCommand(Command):
    description = {
        "en": "Changes the phone number of an existing contact.",
        "uk": "Змінює номер телефону існуючого контакту."
    }
    example = {
        "en": "[name] [phone]",
        "uk": "[ім'я] [телефон]"
    }

    def execute(self, *args: str) -> None:
        """Changes the phone number of an existing contact."""
        if len(args) != 2:
            Message.error("incorrect_arguments")
            return
        name, new_phone = args
        record = self.book_type.find_by_name(Name(name))
        if record:
            current_phone = record.phones[0].value if record.phones else None
            if new_phone == current_phone:
                Message.warning("contact_exists", name=name, phone=new_phone)
            else:
                record.edit_phone(record.phones[0], Phone(new_phone))
                Message.info("contact_updated", name=name,
                             old_phone=current_phone, new_phone=new_phone)
        else:
            Message.error("contact_not_found", name=name)


@register_command("add-phone")
class AddPhoneCommand(FieldCommand):
    description = {
        "en": "Adds a new phone number to an existing contact.",
        "uk": "Додає новий номер телефону до наявного контакту.",
    }
    example = {
        "en": "[name] [phone]",
        "uk": "[ім'я] [телефон]"
    }

    def create_field(self, *args: str) -> Field:
        return Phone(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds a new phone number to an existing contact."""
        if any(p.value == field.value for p in record.phones):
            Message.warning("contact_exists",
                            name=record.name.value, phone=field.value)
        else:
            record.add_phone(field)
            Message.info("contact_added", name=record.name.value,
                         phone=field.value)


@register_command("add-email")
class AddEmailCommand(FieldCommand):
    description = {
        "en": "Adds a new email to an existing contact.",
        "uk": "Додає нову електронну пошту до наявного контакту.",
    }

    def create_field(self, *args: str) -> Field:
        return Email(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds a new email to an existing contact."""
        if "email" in record.fields:
            Message.warning("email_exists", name=record.name.value,
                            email=field.value)
        else:
            record.add_field("email", field)
            Message.info("email_added", name=record.name.value,
                         email=field.value)


@register_command("add-address")
class AddAddressCommand(FieldCommand):
    description = {
        "en": "Adds a new address to an existing contact.",
        "uk": "Додає нову адресу до наявного контакту.",
    }

    def create_field(self, *args: str) -> Field:
        return Address(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds a new address to an existing contact."""
        if "address" in record.fields:
            Message.warning("address_exists", name=record.name.value,
                            email=field.value)
        else:
            record.add_field("address", field)
            Message.info("address_added", name=record.name.value,
                         email=field.value)


@register_command("add-birthday")
class AddBirthdayCommand(FieldCommand):
    description = {
        "en": "Adds a birthday to an existing contact.",
        "uk": "Додає день народження до наявного контакту.",
    }
    example = {
        "en": "[name] [birthday]",
        "uk": "[ім'я] [дата народження]"
    }

    def create_field(self, *args: str) -> Field:
        return Birthday(args[0])

    def execute_field(self, record: Record, field: Field) -> None:
        """Adds a birthday to an existing contact."""
        record.add_field("Birthday", field)
        Message.info("birthday_set", name=record.name.value,
                     birthday=field.value)


@register_command("all")
class ShowAllContactsCommand(Command):
    description = {
        "en": "Shows all contacts in the address book.",
        "uk": "Виводить всі контакти.",
    }

    def execute(self, *args: str) -> None:
        """Shows all contacts in the address book."""
        if self.book_type.data:
            for record in self.book_type.data.values():
                print(str(record))
        else:
            raise IndexError("No contacts available.")

@register_command("search-contact")
class SearchContactsCommand(Command):
    description = {
        "en": "Searches for contacts matching the given criteria.",
        "uk": "Шукає контакти за заданими критеріями."
    }
    example = {
        "en": "[search string]",
        "uk": "[пошуковий запит]"
    }

    def execute(self, *args: str) -> None:
        """Searches for contacts matching the given criteria."""
        if len(args) < 1:
            Message.error("incorrect_arguments")
            return
        keyword = " ".join(args)
        results = [record for record in self.book_type.values() if record.matches_criteria(keyword)]
        if results:
            for record in results:
                print(record)
        else:
            Message.info("no_results_found")

@register_command("show-phone")
class ShowPhoneCommand(Command):
    description = {
        "en": "Shows the phone number of a contact.",
        "uk": "Показує номер телефону контакту.",
    }
    example = {
        "en": "[name]",
        "uk": "[ім'я]"
    }

    def execute(self, *args: str) -> None:
        """Shows the phone number of a contact."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        name = args[0]
        record = self.book_type.find_by_name(Name(name))
        if record:
            phones = "; ".join([phone.value for phone in record.phones])
            Message.info("phone_info", name=name, phone=phones)
        else:
            Message.error("contact_not_found", name=name)

@register_command("add-note")
class AddNoteCommand(Command):
    description = {
        "en": "Adds a new note.",
        "uk": "Додає нову нотатку.",
    }
    example = {
        "en": "[title] [text] [tags]",
        "uk": "[заголовок] [текст] [теги]"
    }

    def execute(self, *args: tuple) -> None:
        """Додає нову нотатку."""
        def remove_hash_words(s: str) -> str:
            return re.sub(r'\s*#[\w-]+', '', s).strip()

        def extract_hash_words(s: str) -> list:
            hash_words = re.findall(r'#[\w-]+', s)
            return hash_words

        title = args[0]
        text = remove_hash_words(' '.join(args[1:]))
        tags = extract_hash_words(' '.join(args[1:]))
        if len(args) < 2:
            Message.error("incorrect_arguments")
            return
        self.book_type.add_note(title, text, tags)
        Message.info("note_added", title=title)


@register_command("edit-note")
class EditNoteCommand(Command):
    description = {
        "en": "Edits an existing note.",
        "uk": "Редагує наявну нотатку.",
    }
    example = {
        "en": "[title] [text] [tags]",
        "uk": "[заголовок] [текст] [теги]"
    }

    def execute(self, *args: tuple) -> None:
        """Редагує наявну нотатку."""
        id_note = args[0]
        title = args[1]
        text = ' '.join(args[2:])
        if len(args) < 2:
            Message.error("incorrect_arguments")
            return

        self.book_type.edit_note(id_note, title, text)
        Message.info("note_updated", title=title, text=text)


@register_command("delete-note")
class DeleteNoteCommand(Command):
    description = {
        "en": "Deletes an existing note.",
        "uk": "Видаляє наявну нотатку.",
    }
    example = {
        "en": "[title]",
        "uk": "[заголовок]"
    }

    def execute(self, *args: tuple) -> None:
        """Видаляє наявну нотатку."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        title = args[0]
        self.book_type.delete_note(title)
        Message.info("note_deleted", title=title)

@register_command("search-notes")
class SearchNotesCommand(Command):
    description = {
        "en": "Searches for notes matching the given criteria.",
        "uk": "Шукає нотатки за заданими критеріями."
    }
    example = {
        "en": "[search string]",
        "uk": "[пошуковий запит]"
    }

    def execute(self, *args: str) -> None:
        """Searches for notes matching the given criteria."""
        if len(args) < 1:
            Message.error("incorrect_arguments")
            return
        keyword = " ".join(args)
        results = self.book_type.search_notes(keyword)
        if results:
            for note in results:
                print(f"\nID: {note['id']}\nTitle: {note['title']}\nText: {note['text']}\nTags: {', '.join(note['tags'])}\n")
                print('-'*40)
        else:
            Message.info("no_results_found")

@register_command("display-notes")
class DisplayNotesCommand(Command):
    description = {
        "en":  "Displays all notes.",
        "uk": "Виводить всі нотатки."
    }

    def execute(self, *args: str) -> None:
        """Виводить всі нотатки."""
        self.book_type.display_notes()



@register_command("exit")
@register_command("close")
class ExitCommand(Command):
    description = {
        "en": "Saves the address book and exits the program.",
        "uk": "Зберігає адресну книгу та виходить з програми.",
    }

    def execute(self, *args: str) -> None:
        """Saves the address book and exits the program."""
        storage = FileStorage("addressbook.json")
        storage.save_contacts(self.book_type.data)
        Message.info("exit_message")
        sys.exit()


@register_command("help")
class HelpCommand(Command):
    description = {
        "en": "Displays this help message.",
        "uk": "Виводить це повідомлення про доступні команди."
    }

    def execute(self, *args: str) -> None:
        """Displays this help message."""
        headers = {
            "en": ("Command", "Parameters", "Description"),
            "uk": ("Команда", "Параметри", "Опис")
        }
        language = settings.language
        max_command_len = max(len(command_name) for command_name in command_registry.command_registry.keys())
        max_example_len = max(
            len(command_class.example.get(language, "")) if hasattr(command_class, 'example') else 0
            for command_class in command_registry.command_registry.values()
        )

        command_header, example_header, description_header = headers[language]
        print(f"\n{Style.BRIGHT}{Fore.CYAN}{command_header.ljust(max_command_len)}\t{example_header.ljust(max_example_len)}\t{description_header}{Style.RESET_ALL}")


        for command_name, command_class in command_registry.command_registry.items():
            description = command_class.description.get(language, "No description available.")
            example = command_class.example.get(language, "") if hasattr(command_class, 'example') else ""
            
            command_str = f"{Style.BRIGHT}{Fore.WHITE}{command_name.ljust(max_command_len)}{Style.RESET_ALL}"
            example_str = f"{Fore.WHITE}{example.ljust(max_example_len)}{Style.RESET_ALL}"
            description_str = f"{Fore.GREEN}{description}{Style.RESET_ALL}"
            
            print(f"{command_str}\t{example_str}\t{description_str}")
        
        print()

@register_command("set-language")
class SetLanguageCommand(Command):
    description = {
        "en": "Sets the application language.",
        "uk": "Встановлює мову застосунку."
    }

    example = {
        "en": "['en' or 'uk']",
        "uk": "['en' або 'uk']"
    }

    def execute(self, *args: str) -> None:
        """Sets the application language."""
        if len(args) != 1:
            Message.error("incorrect_arguments")
            return
        language = args[0]
        if language not in LANGUAGE_MAP[settings.language]:
            Message.error("incorrect_arguments")
            return
        settings.set_language(language)
        Message.load_templates(language)
        user_friendly_language_name = Message.LANGUAGE_MAP[language]
        Message.info("set_language", language=user_friendly_language_name)
