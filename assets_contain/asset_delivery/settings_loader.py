import json
import os


def load_json(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:  # открываем файл на чтение
            data = json.load(fh)
            return data

    except Exception as exception:
        raise exception


def get_processor_settings():
    settings = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'))
    return settings


settings = get_processor_settings()
