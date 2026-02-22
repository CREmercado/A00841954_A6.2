"""
test_reservation.py - Unit tests for the Reservation class.

Tests cover creation, cancellation and display of reservations,
including negative cases and cross-entity validation.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from src.hotel import Hotel
from src.customer import Customer
from src.reservation import (
    Reservation,
    _load_reservations,
    _save_reservations,
)
from src.utils.constants import ACTIVE_STATUS, CANCELED_STATUS


class TestReservation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hotels_file = os.path.join(self.temp_dir, "hotels.json")
        self.customers_file = os.path.join(self.temp_dir, "customers.json")
        self.reservations_file = os.path.join(self.temp_dir, "reservations.json")

        self.patch_hotels = patch("src.hotel.HOTELS_FILE", self.hotels_file)
        self.patch_customers = patch("src.customer.CUSTOMERS_FILE", self.customers_file)
        self.patch_reservations = patch("src.reservation.RESERVATIONS_FILE", self.reservations_file)
        
        with self.patch_hotels:
            Hotel.create_hotel("H001", "Grand Plaza", "New York", 15)
            Hotel.create_hotel("H002", "Pacific Ocean View", "Los Angeles", 10)
            Hotel.create_hotel("H003", "Mision", "San Diego", 1)

        with self.patch_customers:
            Customer.create_customer(
                "C001", "Allan Flores", "af@mail.com", "5551234"
            )
            Customer.create_customer(
                "C002", "Erick Mercado", "cmercado@mail.com", "4444444444"
            )
            Customer.create_customer(
                "C003", "Sara Hasso", "hasso@mail.com", "33333333"
            )
        
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.create_reservation(
                "R001", "C001", "H001", "2026-02-01", "2026-02-05"
            )
            Reservation.create_reservation(
                "R002", "C002", "H002", "2026-02-03", "2026-02-08"
            )
            Reservation.create_reservation(
                "R003", "C003", "H002", "2026-02-18", "2026-02-19"
            )

    def test_save_and_load_reservations(self):
        """Reservations saved and reloaded match original data."""
        data = {
            "R004": {
                "reservation_id": "R004",
                "customer_id": "C002",
                "hotel_id": "H001",
                "check_in": "2026-03-01",
                "check_out": "2026-03-05",
                "status": ACTIVE_STATUS,
            }
        }
        with self.patch_reservations:
            _save_reservations(data)
            loaded = _load_reservations()
        self.assertEqual(loaded, data)
    
    def test_save_hotels_ioerror_prints_error(self):
        """[NEGATIVE] _save_hotels handles IOError when saving file."""
        data = {
            "R004": {
                "reservation_id": "R010",
                "customer_id": "C010",
                "hotel_id": "H010",
                "check_in": "2026-03-01",
                "check_out": "2026-03-05",
                "status": ACTIVE_STATUS,
            }
        }
        with self.patch_reservations:
            with patch("builtins.open", side_effect=IOError("Disk error")):
                with patch("builtins.print") as mock_print:
                    _save_reservations(data)

        mock_print.assert_called()

    def test_init_sets_attributes(self):
        """Reservation initializes with correct attributes."""
        reservation = Reservation(
            "R005",
            "C001",
            "H002",
            {
                "check_in": "2026-03-01",
                "check_out": "2026-03-05",
            },
        )

        self.assertEqual(reservation.reservation_id, "R005")
        self.assertEqual(reservation.customer_id, "C001")
        self.assertEqual(reservation.hotel_id, "H002")
        self.assertEqual(reservation.dates["check_in"], "2026-03-01")
        self.assertEqual(reservation.dates["check_out"], "2026-03-05")
        self.assertEqual(reservation.status, ACTIVE_STATUS)

    def test_from_dict_creates_reservation(self):
        """from_dict correctly reconstructs a Reservation object."""
        data = {
            "reservation_id": "R005",
            "customer_id": "C001",
            "hotel_id": "H002",
            "check_in": "2026-03-01",
            "check_out": "2026-03-05",
            "status": CANCELED_STATUS,
        }
        reservation = Reservation.from_dict(data)
        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.status, CANCELED_STATUS)

    def test_create_reservation_success(self):
        """create_reservation returns a Reservation object on success."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.create_reservation(
                "R005", "C003", "H001", "2026-03-01", "2026-03-05"
            )
        self.assertIsNotNone(result)
        self.assertEqual(result.reservation_id, "R005")
        self.assertEqual(result.status, ACTIVE_STATUS)

    def test_create_reservation_duplicate_id_returns_none(self):
        """[NEGATIVE] create_reservation returns None for a duplicate reservation ID."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.create_reservation(
                "R006", "C001", "H001", "2026-02-01", "2026-02-05"
            )
            result = Reservation.create_reservation(
                "R006", "C001", "H001", "2026-02-06", "2026-02-10"
            )
        self.assertIsNone(result)

    def test_create_reservation_invalid_customer_returns_none(self):
        """[NEGATIVE] create_reservation returns None when customer does not exist."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.create_reservation(
                "R007", "C999", "H001", "2026-02-01", "2026-02-05"
            )
        self.assertIsNone(result)

    def test_create_reservation_invalid_hotel_returns_none(self):
        """[NEGATIVE] create_reservation returns None when hotel does not exist."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.create_reservation(
                "R007", "C001", "H999", "2026-02-01", "2026-02-05"
            )
        self.assertIsNone(result)
    
    def test_create_reservation_no_rooms_available_returns_none(self):
        """[NEGATIVE] create_reservation returns None when hotel has no available rooms."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.create_reservation(
                "R007", "C001", "H003", "2026-02-01", "2026-02-05"
            )
            result = Reservation.create_reservation(
                "R008", "C002", "H003", "2026-02-06", "2026-02-10"
            )
        self.assertIsNone(result)

    def test_cancel_reservation_success(self):
        """cancel_reservation returns True and sets status to canceled."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.cancel_reservation("R001")
            reservations = _load_reservations()
        self.assertTrue(result)
        self.assertEqual(reservations["R001"]["status"], CANCELED_STATUS)
    
    def test_cancel_reservation_nonexistent_returns_false(self):
        """[NEGATIVE] cancel_reservation returns False for a non-existent reservation."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.cancel_reservation("R999")
        self.assertFalse(result)

    def test_cancel_already_canceled_reservation_returns_false(self):
        """[NEGATIVE] cancel_reservation returns False when already canceled."""
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.cancel_reservation("R001")
            result = Reservation.cancel_reservation("R001")
        self.assertFalse(result)

    def test_display_reservation_returns_reservation_object(self):
        """display_reservation returns a Reservation instance for existing ID."""
        with self.patch_reservations:
            result = Reservation.display_reservation("R002")
        self.assertIsInstance(result, Reservation)
        self.assertEqual(result.reservation_id, "R002")

    def test_display_reservation_nonexistent_returns_none(self):
        """[NEGATIVE] display_reservation returns None for a non-existent reservation."""
        with self.patch_reservations:
            result = Reservation.display_reservation("R999")
        self.assertIsNone(result)

    def test_load_reservations_with_corrupted_file(self):
        """[NEGATIVE] _load_reservations handles corrupted JSON file."""
        with open(self.reservations_file, "w") as f:
            f.write("INVALID JSON")

        with self.patch_reservations:
            result = _load_reservations()

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
