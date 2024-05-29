from abc import ABC, abstractmethod
from typing import Dict
from app.entities import Record, Field, AddressBook, Name, NotesBook
from presentation.messages import Message


class Command(ABC):
    description = ""
    exit_command_flag = False

    def __init__(
        self,
        book_type: AddressBook | NotesBook,
    ):
        self.book_type = book_type

    @abstractmethod
    def execute(self, *args: str, **kwargs) -> None:
        pass


class FieldCommand(Command, ABC):
    @abstractmethod
    def execute_field(self, record: Record, field: Field, **kwargs) -> None:
        pass

    def execute(self, *args: str) -> None:
        if len(args) < 2:
            Message.error("incorrect_arguments")
            return
        name, *field_args = args
        # print(f"Arguments received: name={name}, field_args={field_args}")  # Debugging
        record = self.book_type.find_by_name(Name(name))
        if not record:
            Message.error("contact_not_found", name=name)
            return
        command_parameters = self.command_parameters_get()
        # print(f"Command parameters: {command_parameters}")  # Debugging
        field = self.create_field(*field_args, **command_parameters)
        # print(f"Field created: {field}")  # Debugging
        self.execute_field(record, field, **command_parameters)

    def command_parameters_get(self) -> Dict[str, str]:
        return {}

    @abstractmethod
    def create_field(self, *args: str, **kwargs) -> Field:
        pass
