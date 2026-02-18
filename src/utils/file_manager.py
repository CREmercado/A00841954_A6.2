"""
file_manager.py - File management class

Handles loading and saving of dictonaries
to JSON files with error handling and logging.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import json
import os

from .constants import (
    ERROR_PREFIX,
    SUCCESS_PREFIX,
    WARNING_PREFIX
)


def load_json(file_path, entity_name="Data"):
    """Generic JSON loader."""
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            print(f"{WARNING_PREFIX} {entity_name} file is being loaded...")
            return json.load(file)
    except (json.JSONDecodeError, IOError) as error:
        print(f"{ERROR_PREFIX} Could not load {entity_name} file: {error}")
        return {}


def save_json(file_path, data, entity_name="Data"):
    """Generic JSON saver."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            print(f"{SUCCESS_PREFIX} {entity_name} saved successfully.")
    except IOError as error:
        print(f"{ERROR_PREFIX} Could not save {entity_name} file: {error}")
