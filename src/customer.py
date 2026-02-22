"""
customer.py - Customer class for the Reservation System.

Handles customer creation, deletion, display, and modification
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
    """
    Load and return the customers dictionary from the JSON file.

    This helper centralizes file access logic to keep persistence
    concerns separated from business logic.
    """
    return load_json(CUSTOMERS_FILE, "Customers")


def _save_customers(customers):
    """
    Persist the given customers dictionary to the JSON file.

    Args:
        customers (dict): Dictionary containing all customer records.
    """
    save_json(CUSTOMERS_FILE, customers, "Customers")


class Customer:
    """
    Represents a customer in the Reservation System.

    This class encapsulates customer data and provides static
    methods to manage persistence operations.
    """

    def __init__(self, customer_id, name, email, phone):
        """
        Initialize a Customer instance.

        Args:
            customer_id (str): Unique identifier of the customer.
            name (str): Full name of the customer.
            email (str): Email address of the customer.
            phone (str): Contact phone number of the customer.
        """
        # Store immutable identity and contact attributes
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        """
        Convert the Customer instance into a serializable dictionary.

        This method prepares the object for JSON persistence.

        Returns:
            dict: Dictionary representation of the customer.
        """
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Customer instance from a dictionary.

        This method reconstructs an object from persisted JSON data.

        Args:
            data (dict): Dictionary containing customer data.

        Returns:
            Customer: A new Customer object initialized with the data.
        """
        return Customer(
            customer_id=data["customer_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
        )

    @staticmethod
    def create_customer(customer_id, name, email, phone):
        """
        Create and persist a new customer if the ID does not already exist.

        Returns:
            Customer | None: The created Customer object if successful,
            otherwise None if the ID already exists.
        """
        print(f"{WARNING_PREFIX} Creating Customer with ID '{customer_id}'...")

        # Load current state from persistence layer
        customers = _load_customers()

        # Ensure customer IDs remain unique
        if customer_id in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' "
                  "already exists.")
            return None

        # Instantiate domain object
        customer = Customer(customer_id, name, email, phone)

        # Store serialized representation in dictionary
        customers[customer_id] = customer.to_dict()

        # Persist updated state
        _save_customers(customers)

        return customer

    @staticmethod
    def delete_customer(customer_id):
        """
        Delete a customer by ID.

        Returns:
            bool: True if the customer was deleted successfully,
            False if the customer was not found.
        """
        print(f"{WARNING_PREFIX} Deleting Customer with ID '{customer_id}'...")

        # Load persisted customers
        customers = _load_customers()

        # Validate that the customer exists before deletion
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' "
                  "not found.")
            return False

        # Remove customer entry from dictionary
        del customers[customer_id]

        # Persist changes after deletion
        _save_customers(customers)

        return True

    @staticmethod
    def modify_customer(customer_id, name=None, email=None, phone=None):
        """
        Modify an existing customer's information.

        Only provided fields will be updated.

        Returns:
            bool: True if modification was successful,
            False if the customer was not found.
        """
        print(f"{WARNING_PREFIX} Modifying Customer with "
              f"ID '{customer_id}'...")

        # Load current customer data
        customers = _load_customers()

        # Ensure the customer exists before attempting update
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' "
                  "not found.")
            return False

        # Update only fields explicitly provided (partial update pattern)
        if name:
            customers[customer_id]["name"] = name

        if email:
            customers[customer_id]["email"] = email

        if phone:
            customers[customer_id]["phone"] = phone

        # Persist updated state
        _save_customers(customers)

        return True

    @staticmethod
    def display_customer(customer_id):
        """
        Display customer information and return the corresponding object.

        Returns:
            Customer | None: Customer instance if found, otherwise None.
        """
        # Load persisted data
        customers = _load_customers()

        # Validate existence of requested customer
        if customer_id not in customers:
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' "
                  "not found.")
            return None

        # Retrieve raw data from storage
        data = customers[customer_id]

        # Present formatted output to the user interface
        print("Customer Information: ")
        print(f"  - ID      : {data['customer_id']}")
        print(f"  - Name    : {data['name']}")
        print(f"  - Email   : {data['email']}")
        print(f"  - Phone   : {data['phone']}")

        # Reconstruct domain object before returning
        return Customer.from_dict(data)
