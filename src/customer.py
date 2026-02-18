"""
customer.py - Customer class for the Reservation System.

Handles customer creation, deletion, display and modification
with JSON file persistence.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import json
import os

from .utils.constants import (
    ERROR_PREFIX,
    SUCCESS_PREFIX,
    WARNING_PREFIX,
    CUSTOMERS_FILE,
)


def _load_customers():
    """Load customers from the JSON file."""
    if not os.path.exists(CUSTOMERS_FILE):
        return {}
    try:
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as file:
            print(f"{WARNING_PREFIX} Customers file is being loaded. Ensure it is not corrupted.")
            return json.load(file)
    except (json.JSONDecodeError, IOError) as error:
        print(f"{ERROR_PREFIX} Could not load customers file: {error}")
        return {}


def _save_customers(customers):
    """Save customers dictionary to the JSON file."""
    os.makedirs(os.path.dirname(CUSTOMERS_FILE), exist_ok=True)
    try:
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as file:
            json.dump(customers, file, indent=4)
            print(f"{SUCCESS_PREFIX} Customers saved successfully.")
    except IOError as error:
        print(f"{ERROR_PREFIX} Could not save customers file: {error}")

class Customer:

    def __init__(self):
        pass
    
    @staticmethod
    def create_customer():
        pass

    @staticmethod
    def delete_customer():
        pass

    @staticmethod
    def display_customer():
        pass

    @staticmethod
    def modify_customer():
        pass