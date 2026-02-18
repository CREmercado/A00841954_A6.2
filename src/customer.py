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

    def __init__(self, customer_id, first_name, last_name, email, phone):
        """Initialize a Customer."""
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone

    def to_dict(self):
        """Customer to a dictionary."""
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
        }

    @staticmethod
    def from_dict(data):
        """Customer from a dictionary."""
        return Customer(
            customer_id=data["customer_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
        )
    
    @staticmethod
    def create_customer(customer_id, name, email, phone):
        """Create customer."""
        print(f"{WARNING_PREFIX} Creating customer with ID '{customer_id}'...")
        customers = _load_customers()
        if customer_id in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' already exists.")
            return None
        customer = Customer(customer_id, name, email, phone)
        customers[customer_id] = customer.to_dict()
        _save_customers(customers)
        return customer

    @staticmethod
    def delete_customer(customer_id):
        """Delete a customer by their ID."""
        print(f"{WARNING_PREFIX} Deleting customer with ID '{customer_id}'...")
        customers = _load_customers()
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' not found.")
            return False
        del customers[customer_id]
        _save_customers(customers)
        return True

    @staticmethod
    def display_customer():
        pass

    @staticmethod
    def modify_customer():
        pass