from abc import ABC, abstractmethod
from typing import Dict
from app.entities import Record, Field, AddressBook, Name, NotesBook
import uuid
from presentation.messages import Message


class Command(ABC):
    description = ""
    exit_command_flag = False

    def __init__(
        self,
        book_type: AddressBook | NotesBook,
        #  notes_book: NotesBook
    ):
        self.book_type = book_type
        # self.notes_book = notes_book

    @abstractmethod
    def execute(self, *args: str,**kwargs) -> None:
        pass


# Базовий клас для команд, що працюють з полями (Field). Він наслідує від 'Command' і додає специфічні методи для роботи з полями.
class FieldCommand(Command, ABC):
    @abstractmethod
    def execute_field(self, record: Record, field: Field,**kwargs) -> None:
        pass

    def execute(self, *args: str) -> None:
        if len(args) < 2:
            Message.error("incorrect_arguments")
            return
        name, *field_args = args
        record = self.book_type.find_by_name(Name(name))
        if not record:
            Message.error("contact_not_found", name=name)
            return
        command_parameters=self.command_parameters_get()
        field = self.create_field(*field_args,**command_parameters)
        self.execute_field(record, field,**command_parameters)
    
    def command_parameters_get(self)->Dict[str,str]:
        return {}    

    @abstractmethod
    def create_field(self, *args: str,**kwargs) -> Field:
        pass


# Інтерфейс для класів, які будуть відповідати за збереження і завантаження контактів.
class StorageInterface(ABC):
    @abstractmethod
    def save_contacts(self, contacts: Dict[uuid.UUID, Record]) -> None:
        pass

    @abstractmethod
    def load_contacts(self) -> Dict[uuid.UUID, Record]:
        pass
