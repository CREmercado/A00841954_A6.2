"""
test_hotel.py - Unit tests for the Hotel class.

This module validates the behavior of the Hotel class and its
associated persistence helpers.

The test suite covers:
- Hotel creation and reconstruction
- CRUD operations
- Room reservation and cancellation workflows
- File persistence behavior
- Negative and edge-case scenarios

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from src.hotel import (
    Hotel,
    _load_hotels,
    _save_hotels
)


class TestHotel(unittest.TestCase):
    """
    Test suite for the Hotel class.

    Verifies:
    - Data integrity after persistence
    - Correct room availability management
    - Proper handling of duplicate or invalid operations
    - Robustness against corrupted storage files
    """

    def setUp(self):
        """
        Prepare an isolated temporary environment for each test.

        A temporary JSON file is created and injected into the
        Hotel module using patch to avoid modifying production data.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "hotels.json")

        # Preload consistent baseline data for repeatable tests
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.create_hotel("H001", "Grand Plaza", "New York", 50)
            Hotel.create_hotel("H002", "Pacific Ocean View", "Los Angeles", 30)
            Hotel.create_hotel("H003", "Mision", "San Diego", 2)

            # Pre-create initial reservations for state validation
            Hotel.reserve_room("H001", "R001")
            Hotel.reserve_room("H002", "R002")

    def test_save_and_load_hotels(self):
        """
        Verify that saved hotel data can be reloaded correctly.

        Ensures serialization and deserialization preserve
        the complete hotel structure.
        """
        hotels_data = {
            "H004": {
                "hotel_id": "H004",
                "name": "Test Hotel",
                "city": "Boston",
                "total_rooms": 10,
                "available_rooms": 10,
                "reservations": [],
            }
        }
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            _save_hotels(hotels_data)
            loaded = _load_hotels()

        self.assertEqual(loaded, hotels_data)

    def test_save_hotels_ioerror_prints_error(self):
        """
        [NEGATIVE] Verify that _save_hotels handles IOError gracefully.

        Simulates a file write failure and confirms that
        the function does not crash and reports the error.
        """
        hotels_data = {
            "H010": {
                "hotel_id": "H010",
                "name": "Fail Hotel",
                "city": "Nowhere",
                "total_rooms": 5,
                "available_rooms": 5,
                "reservations": []
            }
        }
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            with patch("builtins.open", side_effect=IOError("Disk error")):
                with patch("builtins.print") as mock_print:
                    _save_hotels(hotels_data)

        mock_print.assert_called()

    def test_init_sets_attributes(self):
        """
        Verify that the constructor correctly initializes attributes.
        """
        hotel = Hotel("H005", "City Express", "Denver", 20)

        self.assertEqual(hotel.hotel_id, "H005")
        self.assertEqual(hotel.name, "City Express")
        self.assertEqual(hotel.city, "Denver")
        self.assertEqual(hotel.total_rooms, 20)
        self.assertEqual(hotel.available_rooms, 20)
        self.assertEqual(hotel.reservations, [])

    def test_to_dict_values_match(self):
        """
        Ensure that to_dict accurately reflects hotel attributes.
        """
        hotel = Hotel("H005", "City Express", "Denver", 20)
        data = hotel.to_dict()

        self.assertEqual(data["hotel_id"], "H005")
        self.assertEqual(data["name"], "City Express")
        self.assertEqual(data["city"], "Denver")
        self.assertEqual(data["total_rooms"], 20)
        self.assertEqual(data["available_rooms"], 20)
        self.assertEqual(data["reservations"], [])

    def test_from_dict_creates_hotel(self):
        """
        Verify that from_dict reconstructs a Hotel instance
        with correct state.
        """
        data = {
            "hotel_id": "H005",
            "name": "City Express",
            "city": "Denver",
            "total_rooms": 20,
            "available_rooms": 18,
            "reservations": ["R003"],
        }
        hotel = Hotel.from_dict(data)

        self.assertEqual(hotel.hotel_id, "H005")
        self.assertEqual(hotel.available_rooms, 18)
        self.assertEqual(hotel.reservations, ["R003"])

    def test_create_hotel_success(self):
        """
        Verify that create_hotel returns a valid Hotel instance
        when the ID does not already exist.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            hotel = Hotel.create_hotel("H005", "City Express", "Denver", 20)

        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.hotel_id, "H005")

    def test_create_hotel_duplicate_id_returns_none(self):
        """
        [NEGATIVE] Ensure that duplicate hotel IDs return None
        and do not overwrite existing data.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.create_hotel("H001", "Another Hotel", "Boston", 20)

        self.assertIsNone(result)

    def test_delete_hotel_success(self):
        """
        Verify that delete_hotel removes an existing hotel
        and returns True.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.delete_hotel("H003")
            hotels = _load_hotels()

        self.assertTrue(result)
        self.assertNotIn("H003", hotels)

    def test_delete_hotel_nonexistent_returns_false(self):
        """
        [NEGATIVE] Ensure that deleting a non-existent hotel
        returns False.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.delete_hotel("H999")

        self.assertFalse(result)

    def test_modify_hotel_available_rooms_not_negative(self):
        """
        [NEGATIVE] Ensure available_rooms never becomes negative
        after modifying total_rooms.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.modify_hotel("H001", total_rooms=1)
            Hotel.modify_hotel("H001", total_rooms=0)
            hotels = _load_hotels()

        self.assertGreaterEqual(hotels["H001"]["available_rooms"], 0)

    def test_modify_hotel_nonexistent_returns_false(self):
        """
        [NEGATIVE] Ensure modify_hotel returns False
        for unknown hotel IDs.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.modify_hotel("H999", name="Ghost Hotel")

        self.assertFalse(result)

    def test_display_hotel_returns_hotel_object(self):
        """
        Verify that display_hotel returns a Hotel instance
        for a valid ID.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.display_hotel("H001")

        self.assertIsInstance(result, Hotel)
        self.assertEqual(result.hotel_id, "H001")

    def test_display_hotel_nonexistent_returns_none(self):
        """
        [NEGATIVE] Ensure display_hotel returns None
        for invalid IDs.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.display_hotel("H999")

        self.assertIsNone(result)

    def test_reserve_room_success(self):
        """
        Verify that reserve_room decreases availability
        and registers the reservation ID.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.reserve_room("H003", "R001")
            hotels = _load_hotels()

        self.assertTrue(result)
        self.assertEqual(hotels["H003"]["available_rooms"], 1)
        self.assertIn("R001", hotels["H003"]["reservations"])

    def test_reserve_room_hotel_not_found(self):
        """
        [NEGATIVE] Ensure reserve_room returns False
        when the hotel does not exist.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.reserve_room("H999", "R003")

        self.assertFalse(result)

    def test_reserve_room_no_availability(self):
        """
        [NEGATIVE] Ensure reserve_room returns False
        when no rooms are available.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.reserve_room("H003", "R003")
            Hotel.reserve_room("H003", "R004")
            result = Hotel.reserve_room("H003", "R005")

        self.assertFalse(result)

    def test_reserve_room_duplicate_reservation_id(self):
        """
        [NEGATIVE] Ensure duplicate reservation IDs
        are rejected.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.reserve_room("H002", "R001")
            result = Hotel.reserve_room("H002", "R001")

        self.assertFalse(result)

    def test_cancel_reservation_hotel_not_found(self):
        """
        [NEGATIVE] Ensure cancellation fails
        for unknown hotel IDs.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.cancel_room_reservation("H999", "R001")

        self.assertFalse(result)

    def test_cancel_reservation_not_found_in_hotel(self):
        """
        [NEGATIVE] Ensure cancellation fails
        for unknown reservation IDs.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.cancel_room_reservation("H001", "R999")

        self.assertFalse(result)

    def test_cancel_reservation_does_not_exceed_total_rooms(self):
        """
        Ensure that cancelling a reservation never increases
        available_rooms beyond total_rooms.
        """
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.cancel_room_reservation("H001", "R001")
            hotels = _load_hotels()

        self.assertLessEqual(
            hotels["H001"]["available_rooms"],
            hotels["H001"]["total_rooms"]
        )

    def test_load_hotels_with_corrupted_file(self):
        """
        [NEGATIVE] Ensure corrupted JSON files are handled safely.

        The function should return an empty dictionary
        instead of raising an exception.
        """
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("INVALID JSON")

        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = _load_hotels()

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
