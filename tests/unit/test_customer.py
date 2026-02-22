"""
test_customer.py - Unit tests for the Customer class.

This module contains unit tests that validate the behavior of the
Customer class and its helper persistence functions.

Test coverage includes:
- Object creation and reconstruction
- CRUD operations
- File persistence behavior
- Negative and edge-case scenarios

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from src.customer import (
    Customer,
    _load_customers,
    _save_customers
)


class TestCustomer(unittest.TestCase):
    """
    Test suite for the Customer class.

    Ensures correct functionality of:
    - Data persistence
    - Object serialization/deserialization
    - CRUD operations
    - Error handling scenarios
    """

    def setUp(self):
        """
        Prepare an isolated temporary environment for each test.

        A temporary JSON file is created and injected into the module
        using patch to avoid modifying real application data.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "customers.json")

        # Pre-populate test data for repeatable test execution
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            Customer.create_customer(
                "C001", "Allan Flores", "aflores@mail.com", "5555555555"
            )
            Customer.create_customer(
                "C002", "Erick Mercado", "cmercado@mail.com", "4444444444"
            )
            Customer.create_customer(
                "C003", "Sara Hasso", "hasso@mail.com", "33333333"
            )

    def test_save_and_load_customers(self):
        """
        Verify that customers saved to file can be reloaded correctly.

        Confirms that _save_customers and _load_customers preserve
        data integrity during serialization/deserialization.
        """
        data = {
            "C004": {
                "customer_id": "C004",
                "name": "Arena Suerte",
                "email": "as@mail.com",
                "phone": "777777",
            }
        }
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            _save_customers(data)
            loaded = _load_customers()
        self.assertEqual(loaded, data)

    def test_save_customers_ioerror_prints_error(self):
        """
        [NEGATIVE] Ensure _save_customers handles IOError gracefully.

        Simulates a file write failure and verifies that the
        function does not crash and emits an error message.
        """
        data = {
            "C010": {
                "customer_id": "C010",
                "name": "Test User",
                "email": "test@mail.com",
                "phone": "123456"
            }
        }
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            with patch("builtins.open", side_effect=IOError("Disk error")):
                with patch("builtins.print") as mock_print:
                    _save_customers(data)

        mock_print.assert_called()

    def test_init_sets_attributes(self):
        """
        Verify that the constructor correctly assigns attributes.
        """
        customer = Customer("C005", "Edgardo Perex", "ep@mail.com", "5551234")
        self.assertEqual(customer.customer_id, "C005")
        self.assertEqual(customer.name, "Edgardo Perex")
        self.assertEqual(customer.email, "ep@mail.com")
        self.assertEqual(customer.phone, "5551234")

    def test_to_dict_values_match(self):
        """
        Ensure that to_dict returns accurate attribute mappings.
        """
        customer = Customer("C005", "Edgardo Perex", "ep@mail.com", "5551234")
        data = customer.to_dict()
        self.assertEqual(data["customer_id"], "C005")
        self.assertEqual(data["email"], "ep@mail.com")

    def test_from_dict_missing_fields_raises_error(self):
        """
        [NEGATIVE] Verify that from_dict raises KeyError
        when required fields are missing.
        """
        incomplete_data = {
            "customer_id": "C010",
            "name": "NoLastName"
            # Required fields intentionally omitted
        }
        with self.assertRaises(KeyError):
            Customer.from_dict(incomplete_data)

    def test_from_dict_creates_customer(self):
        """
        Verify that from_dict reconstructs a valid Customer object.
        """
        data = {
            "customer_id": "C005",
            "name": "Edgardo Perex",
            "email": "ep@mail.com",
            "phone": "5551234",
        }
        customer = Customer.from_dict(data)
        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.customer_id, "C005")
        self.assertEqual(customer.email, "ep@mail.com")

    def test_create_customer_success(self):
        """
        Verify that create_customer returns a Customer object
        when the ID does not already exist.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            customer = Customer.create_customer(
                "C005", "Edgardo Perex", "ep@mail.com", "5551234"
            )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.customer_id, "C005")

    def test_create_customer_duplicate_id_returns_none(self):
        """
        [NEGATIVE] Verify that create_customer returns None
        if the customer ID already exists.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.create_customer(
                "C001", "Other Person", "other@mail.com", "0000000"
            )
        self.assertIsNone(result)

    def test_create_customer_duplicate_does_not_overwrite(self):
        """
        [NEGATIVE] Ensure that duplicate creation attempts
        do not overwrite existing customer data.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            Customer.create_customer(
                "C001", "Allan Flores", "af@mail.com", "5551234"
            )
            Customer.create_customer(
                "C001", "Hacker Smith", "hack@mail.com", "9999999"
            )
            customers = _load_customers()
        self.assertEqual(customers["C001"]["name"], "Allan Flores")

    def test_delete_customer_success(self):
        """
        Verify that delete_customer removes an existing customer
        and returns True.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.delete_customer("C003")
            customers = _load_customers()
        self.assertTrue(result)
        self.assertNotIn("C003", customers)

    def test_delete_customer_nonexistent_returns_false(self):
        """
        [NEGATIVE] Verify that delete_customer returns False
        for a non-existent ID.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.delete_customer("C999")
        self.assertFalse(result)

    def test_modify_customer_nonexistent_returns_false(self):
        """
        [NEGATIVE] Verify that modify_customer returns False
        when the customer does not exist.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.modify_customer("C999", email="ghost@mail.com")
        self.assertFalse(result)

    def test_modify_customer_does_not_change_unspecified_fields(self):
        """
        Ensure that modify_customer only updates specified fields
        and preserves other existing values.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            Customer.modify_customer("C001", email="new@mail.com")
            customers = _load_customers()
        self.assertEqual(customers["C001"]["name"], "Allan Flores")
        self.assertEqual(customers["C001"]["phone"], "5555555555")

    def test_display_customer_returns_customer_object(self):
        """
        Verify that display_customer returns a Customer instance
        for an existing ID.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.display_customer("C001")
        self.assertIsInstance(result, Customer)
        self.assertEqual(result.customer_id, "C001")

    def test_display_customer_nonexistent_returns_none(self):
        """
        [NEGATIVE] Verify that display_customer returns None
        when the ID does not exist.
        """
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.display_customer("C999")
        self.assertIsNone(result)

    def test_load_customers_with_corrupted_file(self):
        """
        [NEGATIVE] Verify that _load_customers handles
        corrupted JSON content gracefully.

        The function should return an empty dictionary
        instead of raising an exception.
        """
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("INVALID JSON")

        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = _load_customers()

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
