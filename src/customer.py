"""
customer.py - Customer class for the Reservation System.

Handles customer creation, deletion, display and modification
with JSON file persistence.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

from .utils.file_manager import load_json, save_json
from .utils.constants import (
    ERROR_PREFIX,
    WARNING_PREFIX,
    CUSTOMERS_FILE,
)


def _load_customers():
    """Load customers from the JSON file."""
    return load_json(CUSTOMERS_FILE, "Customers")


def _save_customers(customers):
    """Save customers dictionary to the JSON file."""
    save_json(CUSTOMERS_FILE, customers, "Customers")


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
    def create_customer(customer_id, first_name, last_name, email, phone):
        """Create customer."""
        print(f"{WARNING_PREFIX} Creating Customer with ID '{customer_id}'...")
        customers = _load_customers()
        if customer_id in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' already exists.")
            return None
        customer = Customer(customer_id, first_name, last_name, email, phone)
        customers[customer_id] = customer.to_dict()
        _save_customers(customers)
        return customer

    @staticmethod
    def delete_customer(customer_id):
        """Delete customer."""
        print(f"{WARNING_PREFIX} Deleting Customer with ID '{customer_id}'...")
        customers = _load_customers()
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' not found.")
            return False
        del customers[customer_id]
        _save_customers(customers)
        return True

    @staticmethod
    def modify_customer(customer_id, first_name=None, last_name=None, email=None, phone=None):
        """Modify customer."""
        print(f"{WARNING_PREFIX} Modifying Customer with ID '{customer_id}'...")
        customers = _load_customers()
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' not found.")
            return False
        if first_name:
            customers[customer_id]["first_name"] = first_name
        if last_name:
            customers[customer_id]["last_name"] = last_name
        if email:
            customers[customer_id]["email"] = email
        if phone:
            customers[customer_id]["phone"] = phone
        _save_customers(customers)
        return True
    
    @staticmethod
    def display_customer(customer_id):
        """Display customer."""
        customers = _load_customers()
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' not found.")
            return None
        data = customers[customer_id]
        print("Customer Information: ")
        print(f"  - ID          : {data['customer_id']}")
        print(f"  - First Name  : {data['first_name']}")
        print(f"  - Last Name   : {data['last_name']}")
        print(f"  - Email       : {data['email']}")
        print(f"  - Phone       : {data['phone']}")
        return Customer.from_dict(data)