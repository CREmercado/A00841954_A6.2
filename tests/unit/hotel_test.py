"""
hotel_test.py - Unit tests for the Hotel class.

Tests cover creation, deletion, display, modification,
room reservation and cancellation, including negative cases.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from src.hotel import Hotel, _load_hotels, _save_hotels


class TestHotel(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "hotels.json")
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.create_hotel("H001", "Grand Plaza", "New York", 50)
            Hotel.create_hotel("H002", "Pacific Ocean View", "Los Angeles", 30)
            Hotel.create_hotel("H003", "Mision", "San Diego", 2)
            Hotel.reserve_room("H001", "R001")
            Hotel.reserve_room("H002", "R002")

    def test_init_sets_attributes(self):
        """Hotel initializes with correct attributes."""
        hotel = Hotel("H004", "City Express", "Denver", 20)
        self.assertEqual(hotel.hotel_id, "H004")
        self.assertEqual(hotel.name, "City Express")
        self.assertEqual(hotel.city, "Denver")
        self.assertEqual(hotel.total_rooms, 20)
        self.assertEqual(hotel.available_rooms, 20)
        self.assertEqual(hotel.reservations, [])

    def test_to_dict_values_match(self):
        """to_dict values match the hotel attributes."""
        hotel = Hotel("H004", "City Express", "Denver", 20)
        data = hotel.to_dict()
        self.assertEqual(data["hotel_id"], "H004")
        self.assertEqual(data["name"], "City Express")
        self.assertEqual(data["city"], "Denver")
        self.assertEqual(data["total_rooms"], 20)
        self.assertEqual(data["available_rooms"], 20)
        self.assertEqual(data["reservations"], [])

    def test_from_dict_creates_hotel(self):
        """from_dict correctly reconstructs a Hotel object."""
        data = {
            "hotel_id": "H004",
            "name": "City Express",
            "city": "Denver",
            "total_rooms": 20,
            "available_rooms": 18,
            "reservations": ["R003"],
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.hotel_id, "H004")
        self.assertEqual(hotel.available_rooms, 18)
        self.assertEqual(hotel.reservations, ["R003"])
        
    def test_create_hotel_success(self):
        """create_hotel returns a Hotel object on success."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            hotel = Hotel.create_hotel("H004", "City Express", "Denver", 20)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.hotel_id, "H004")
    
    def test_create_hotel_duplicate_id_returns_none(self):
        """[NEGATIVE] create_hotel returns None if hotel ID already exists."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.create_hotel("H001", "Another Hotel", "Boston", 20)
        self.assertIsNone(result)

    def test_delete_hotel_success(self):
        """delete_hotel returns True and removes hotel from file."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.delete_hotel("H003")
            hotels = _load_hotels()
        self.assertTrue(result)
        self.assertNotIn("H003", hotels)
    
    def test_delete_hotel_nonexistent_returns_false(self):
        """[NEGATIVE] delete_hotel returns False for a non-existent hotel ID."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.delete_hotel("H999")
        self.assertFalse(result)

    def test_modify_hotel_available_rooms_not_negative(self):
        """[NEGATIVE] modify_hotel clamps available_rooms to 0 if reduction exceeds current."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.modify_hotel("H001", total_rooms=1)
            Hotel.modify_hotel("H001", total_rooms=0)
            hotels = _load_hotels()
        self.assertGreaterEqual(hotels["H001"]["available_rooms"], 0)

    def test_modify_hotel_nonexistent_returns_false(self):
        """[NEGATIVE] modify_hotel returns False for a non-existent hotel ID."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.modify_hotel("H999", name="Ghost Hotel")
        self.assertFalse(result)

    def test_display_hotel_nonexistent_returns_none(self):
        """[NEGATIVE] display_hotel returns None for a non-existent hotel ID."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.display_hotel("H999")
        self.assertIsNone(result)
    
    def test_reserve_room_hotel_not_found(self):
        """[NEGATIVE] reserve_room returns False when hotel ID does not exist."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.reserve_room("H999", "R003")
        self.assertFalse(result)

    def test_reserve_room_no_availability(self):
        """[NEGATIVE] reserve_room returns False when no rooms are available."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.reserve_room("H003", "R003")
            Hotel.reserve_room("H003", "R004")
            result = Hotel.reserve_room("H001", "R005")
        self.assertFalse(result)

    def test_cancel_reservation_hotel_not_found(self):
        """[NEGATIVE] cancel_room_reservation returns False for unknown hotel."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.cancel_room_reservation("H999", "R001")
        self.assertFalse(result)

    def test_cancel_reservation_not_found_in_hotel(self):
        """[NEGATIVE] cancel_room_reservation returns False for unknown reservation."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            result = Hotel.cancel_room_reservation("H001", "R999")
        self.assertFalse(result)

    def test_cancel_reservation_does_not_exceed_total_rooms(self):
        """cancel_room_reservation does not allow available_rooms > total_rooms."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.cancel_room_reservation("H001", "R001")
            hotels = _load_hotels()
        self.assertLessEqual(
            hotels["H001"]["available_rooms"],
            hotels["H001"]["total_rooms"]
        )


if __name__ == '__main__':
    unittest.main()
