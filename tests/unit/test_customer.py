"""
test_customer.py - Unit tests for the Customer class.

Tests cover creation, deletion, display and modification,
including negative cases.

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

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "customers.json")
        
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            Customer.create_customer(
                "C001", "Allan", "Flores", "aflores@mail.com", "5555555555"
            )
            Customer.create_customer(
                "C002", "Erick", "Mercado", "cmercado@mail.com", "4444444444"
            )
            Customer.create_customer(
                "C003", "Sara", "Hasso", "hasso@mail.com", "33333333"
            )
    
    def test_save_and_load_customers(self):
        """Customers saved and reloaded match original data."""
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
        """[NEGATIVE] _save_customers handles IOError when saving file."""
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
        """Customer initializes with correct attributes."""
        customer = Customer("C005", "Edgardo", "Perex", "ep@mail.com", "5551234")
        self.assertEqual(customer.customer_id, "C005")
        self.assertEqual(customer.name, "Edgardo Perex")
        self.assertEqual(customer.email, "ep@mail.com")
        self.assertEqual(customer.phone, "5551234")
    
    def test_to_dict_values_match(self):
        """to_dict values match the customer attributes."""
        customer = Customer("C005", "Edgardo", "Perex", "ep@mail.com", "5551234")
        data = customer.to_dict()
        self.assertEqual(data["customer_id"], "C005")
        self.assertEqual(data["email"], "ep@mail.com")
    
    def test_from_dict_missing_fields_raises_error(self):
        """[NEGATIVE] from_dict raises KeyError if required fields are missing."""
        incomplete_data = {
            "customer_id": "C010",
            "name": "NoLastName"
            # missing email, phone
        }
        with self.assertRaises(KeyError):
            Customer.from_dict(incomplete_data)

    def test_from_dict_creates_customer(self):
        """from_dict correctly reconstructs a Customer object."""
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
        """create_customer returns a Customer object on success."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            customer = Customer.create_customer(
                "C005", "Edgardo", "Perex", "ep@mail.com", "5551234"
            )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.customer_id, "C005")

    def test_create_customer_duplicate_id_returns_none(self):
        """[NEGATIVE] create_customer returns None if customer ID already exists."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.create_customer(
                "C001", "Other", "Person", "other@mail.com", "0000000"
            )
        self.assertIsNone(result)

    def test_create_customer_duplicate_does_not_overwrite(self):
        """[NEGATIVE] Duplicate create_customer does not overwrite existing data."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            Customer.create_customer(
                "C001", "Allan", "Flores", "af@mail.com", "5551234"
            )
            Customer.create_customer(
                "C001", "Hacker", "Smith", "hack@mail.com", "9999999"
            )
            customers = _load_customers()
        self.assertEqual(customers["C001"]["name"], "Allan")
    
    def test_delete_customer_success(self):
        """delete_customer returns True and removes customer from file."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.delete_customer("C003")
            customers = _load_customers()
        self.assertTrue(result)
        self.assertNotIn("C003", customers)
    
    def test_delete_customer_nonexistent_returns_false(self):
        """[NEGATIVE] delete_customer returns False for a non-existent customer ID."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.delete_customer("C999")
        self.assertFalse(result)

    def test_modify_customer_nonexistent_returns_false(self):
        """[NEGATIVE] modify_customer returns False for a non-existent customer ID."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.modify_customer("C999", email="ghost@mail.com")
        self.assertFalse(result)
    
    def test_modify_customer_does_not_change_unspecified_fields(self):
        """modify_customer leaves unspecified fields unchanged."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            Customer.modify_customer("C001", email="new@mail.com")
            customers = _load_customers()
        self.assertEqual(customers["C001"]["name"], "Allan")
        self.assertEqual(customers["C001"]["phone"], "5555555555")
    
    def test_display_customer_returns_customer_object(self):
        """display_customer returns a Customer instance for an existing ID."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.display_customer("C001")
        self.assertIsInstance(result, Customer)
        self.assertEqual(result.customer_id, "C001")
    
    def test_display_customer_nonexistent_returns_none(self):
        """[NEGATIVE] display_customer returns None for a non-existent customer ID."""
        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = Customer.display_customer("C999")
        self.assertIsNone(result)

    def test_load_customers_with_corrupted_file(self):
        """[NEGATIVE] _load_customers handles corrupted JSON file."""
        with open(self.temp_file, "w") as f:
            f.write("INVALID JSON")

        with patch("src.customer.CUSTOMERS_FILE", self.temp_file):
            result = _load_customers()

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
