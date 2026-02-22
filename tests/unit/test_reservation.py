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
    """
    Test suite for the Reservation class and its persistence layer.

    This suite validates:
    - Reservation lifecycle (create, cancel, display)
    - Cross-entity integrity (Customer ↔ Hotel ↔ Reservation)
    - Persistence consistency
    - Robust handling of invalid and edge-case scenarios
    """

    def setUp(self):
        """
        Create an isolated temporary environment for each test case.

        Each entity (Hotel, Customer, Reservation) is redirected to a
        temporary JSON file using patch to ensure:
        - No interference with production data
        - Test independence
        - Deterministic execution
        """

        # Create isolated temporary directory for test storage
        self.temp_dir = tempfile.mkdtemp()

        # Define temporary file paths for each persistence layer
        self.hotels_file = os.path.join(self.temp_dir, "hotels.json")
        self.customers_file = os.path.join(self.temp_dir, "customers.json")
        self.reservations_file = os.path.join(self.temp_dir,
                                              "reservations.json")

        # Patch file constants to redirect storage during tests
        self.patch_hotels = patch("src.hotel.HOTELS_FILE", self.hotels_file)
        self.patch_customers = patch("src.customer.CUSTOMERS_FILE",
                                     self.customers_file)
        self.patch_reservations = patch("src.reservation.RESERVATIONS_FILE",
                                        self.reservations_file)

        # Initialize baseline hotels
        with self.patch_hotels:
            Hotel.create_hotel("H001", "Grand Plaza", "New York", 15)
            Hotel.create_hotel("H002", "Pacific Ocean View", "Los Angeles", 10)
            Hotel.create_hotel("H003", "Mision", "San Diego", 1)

        # Initialize baseline customers
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

        # Pre-create reservations to validate state transitions
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
        """
        Verify that reservations are correctly serialized and deserialized.

        Ensures persistence integrity by comparing stored data
        with reloaded content.
        """
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
        """
        [NEGATIVE] Ensure _save_reservations handles file write errors.

        Simulates an IOError and verifies that the function
        reports the error instead of raising an unhandled exception.
        """
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
            # Force file write failure
            with patch("builtins.open", side_effect=IOError("Disk error")):
                with patch("builtins.print") as mock_print:
                    _save_reservations(data)

        mock_print.assert_called()

    def test_init_sets_attributes(self):
        """
        Verify that Reservation constructor initializes attributes properly.

        Ensures default status is ACTIVE when not explicitly provided.
        """
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
        """
        Validate that from_dict reconstructs a Reservation instance
        with accurate state restoration.
        """
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
        """
        Verify successful reservation creation when all constraints are valid.

        Validates:
        - Existing customer
        - Existing hotel
        - Room availability
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.create_reservation(
                "R005", "C003", "H001", "2026-03-01", "2026-03-05"
            )

        self.assertIsNotNone(result)
        self.assertEqual(result.reservation_id, "R005")
        self.assertEqual(result.status, ACTIVE_STATUS)

    def test_create_reservation_duplicate_id_returns_none(self):
        """
        [NEGATIVE] Duplicate reservation IDs must be rejected
        to preserve data integrity.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.create_reservation(
                "R006", "C001", "H001", "2026-02-01", "2026-02-05"
            )
            result = Reservation.create_reservation(
                "R006", "C001", "H001", "2026-02-06", "2026-02-10"
            )

        self.assertIsNone(result)

    def test_create_reservation_invalid_customer_returns_none(self):
        """
        [NEGATIVE] Reservation creation must fail if customer does not exist.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.create_reservation(
                "R007", "C999", "H001", "2026-02-01", "2026-02-05"
            )

        self.assertIsNone(result)

    def test_create_reservation_invalid_hotel_returns_none(self):
        """
        [NEGATIVE] Reservation creation must fail if hotel does not exist.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.create_reservation(
                "R007", "C001", "H999", "2026-02-01", "2026-02-05"
            )

        self.assertIsNone(result)

    def test_create_reservation_no_rooms_available_returns_none(self):
        """
        [NEGATIVE] Reservation must fail when no rooms are available.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.create_reservation(
                "R007", "C001", "H003", "2026-02-01", "2026-02-05"
            )
            result = Reservation.create_reservation(
                "R008", "C002", "H003", "2026-02-06", "2026-02-10"
            )

        self.assertIsNone(result)

    def test_cancel_reservation_success(self):
        """
        Verify that cancellation updates reservation status
        and persists the change.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.cancel_reservation("R001")
            reservations = _load_reservations()

        self.assertTrue(result)
        self.assertEqual(reservations["R001"]["status"], CANCELED_STATUS)

    def test_cancel_reservation_nonexistent_returns_false(self):
        """
        [NEGATIVE] Cancellation must fail for unknown reservation IDs.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            result = Reservation.cancel_reservation("R999")

        self.assertFalse(result)

    def test_cancel_already_canceled_reservation_returns_false(self):
        """
        [NEGATIVE] Cancellation must fail if reservation
        is already in CANCELED state.
        """
        with self.patch_hotels, self.patch_customers, self.patch_reservations:
            Reservation.cancel_reservation("R001")
            result = Reservation.cancel_reservation("R001")

        self.assertFalse(result)

    def test_display_reservation_returns_reservation_object(self):
        """
        Verify that display_reservation returns a valid
        Reservation instance when ID exists.
        """
        with self.patch_reservations:
            result = Reservation.display_reservation("R002")

        self.assertIsInstance(result, Reservation)
        self.assertEqual(result.reservation_id, "R002")

    def test_display_reservation_nonexistent_returns_none(self):
        """
        [NEGATIVE] display_reservation must return None
        for invalid reservation IDs.
        """
        with self.patch_reservations:
            result = Reservation.display_reservation("R999")

        self.assertIsNone(result)

    def test_load_reservations_with_corrupted_file(self):
        """
        [NEGATIVE] Corrupted JSON files must not crash the system.

        Function should safely return an empty dictionary
        when encountering invalid JSON content.
        """
        with open(self.reservations_file, "w", encoding="utf-8") as f:
            f.write("INVALID JSON")

        with self.patch_reservations:
            result = _load_reservations()

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
