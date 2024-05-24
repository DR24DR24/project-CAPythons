import json
import os
from colorama import Fore, Style


class Message:
    LANGUAGE_MAP = {"en": "English", "uk": "українська"}
    templates = {}
    colors = {
        "info": Fore.GREEN,
        "highlight": Fore.CYAN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "param": Fore.MAGENTA,  # Колір для параметрів
        "reset": Style.RESET_ALL,
    }

    @classmethod
    def load_templates(cls, language):
        """Load message templates based on the selected language."""
        try:
            with open(
                os.path.join(
                    os.path.dirname(
                        __file__), f"../resources/messages_{language}.json"
                ),
                "r",
                encoding="utf-8",
            ) as file:
                cls.templates = json.load(file)
        except FileNotFoundError:
            print(
                f"Language file for '{language}' not found. Loading default (English) templates."
            )
            with open(
                os.path.join(
                    os.path.dirname(__file__), "../resources/messages_en.json"
                ),
                "r",
                encoding="utf-8",
            ) as file:
                cls.templates = json.load(file)

    @classmethod
    def format_message(cls, template_name: str, **kwargs) -> str:
        """Format the message with provided parameters."""
        # print(cls.templates)
        # print("\n" + template_name)

        # print(cls.templates.get('note_added'))
        template = cls.templates.get(
            template_name, "Message template not found")
        formatted_message = template.format(
            **{
                k: f"{cls.colors['param']}{v}{cls.colors['reset']}{cls.colors['info']}"
                for k, v in kwargs.items()
            }
        )
        return formatted_message

    @classmethod
    def info(cls, template_name, **kwargs):
        """Display an informational message."""
        message = cls.format_message(template_name, **kwargs)
        print(f"{cls.colors['info']}{message}{cls.colors['reset']}")

    @classmethod
    def warning(cls, template_name, **kwargs):
        """Display a warning message."""
        message = cls.format_message(template_name, **kwargs)
        print(f"{cls.colors['warning']}{message}{cls.colors['reset']}")

    @classmethod
    def error(cls, template_name, **kwargs):
        """Display an error message."""
        message = cls.format_message(template_name, **kwargs)
        print(f"{cls.colors['error']}{message}{cls.colors['reset']}")

    @classmethod
    def apply_theme(cls, message: str) -> str:
        """Apply color themes to the message."""
        for key, color in cls.colors.items():
            message = message.replace(f"{{{key}}}", color)
        return message
