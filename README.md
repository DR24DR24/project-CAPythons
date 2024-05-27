# project-CAPythons

Поточна структура проекту:
```plaintext
src/
├── application/
│   ├── command_registry.py  # Потрібний для динамічного створення "регістру команд".
│   ├── services.py  # Логіка для роботи з контактами
│   ├── entities.py  # Класи Field, Name, Phone, Birthday, Record
│   └── interfaces.py  # Інтерфейси для взаємодії зі storage (у майбутньому — бази даних, хмарні сервіси тощо)
├── infrastructure
│   └── storage.py  # Реалізація збереження/відновлення контактів, серіалізація
├── presentation
│   ├── cli.py  # Обробка команд та взаємодія з користувачем 
│   └── messages.py # Оформлення повідомлень, до яких (в майбутньому) можна буде застосовувати різні кольорові теми
├── resources
│   ├── messages_en.json  # Шаблони повідомлень (англійські + українські)
│   └── messages_en.json
└── main.py  # Точка входу: для запуску у VS Code всього додатку, потрібно відкрити саме цей файл, і (наприклад) натиснути F5.

tests/ # Імена файлів з тестами могли б виглядати приблизно так
├── test_cli.py
├── test_entities.py
├── test_interfaces.py
├── test_services.py
└── test_storage.py
```

### Налаштування запуску проекту
У теку `.vscode` додати файл `launch.json` з наступним вмістом:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Launch main.py",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal"
        }
    ]
}
```

### Налаштування запуску тестів з теки `src/tests/`
Файл `settings.json` (у теці `.vscode`):
```json
{
    "python.testing.unittestArgs": [
        "-v",
        "-s",
        "./src/tests",
        "-p",
        "test_*.py"
    ],
    "python.testing.pytestEnabled": false,
    "python.testing.unittestEnabled": true
}
```

Or in vscode file->preference->setting, then find unittestArgs and write src\tests in the line after -s

Instruction: https://code.visualstudio.com/docs/python/testing

### Make package

Docs:
https://packaging.python.org/en/latest/flow/
https://packaging.python.org/en/latest/tutorials/packaging-projects/
https://packaging.python.org/en/latest/specifications/pypirc/
https://hatch.pypa.io/latest/config/build/#pyprojecttoml_3
https://twine.readthedocs.io/en/stable/

File .pypirc at $home:

'''[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <token> 
'''

Command:

python -m build

twine upload -r testpypi dist/* --verbose
