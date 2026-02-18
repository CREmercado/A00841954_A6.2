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

    def test_init_sets_attributes(self):
        """Hotel initializes with correct attributes."""
        hotel = Hotel("H001", "Grand Plaza", "New York", 50)
        self.assertEqual(hotel.hotel_id, "H001")
        self.assertEqual(hotel.name, "Grand Plaza")
        self.assertEqual(hotel.city, "New York")
        self.assertEqual(hotel.total_rooms, 50)
        self.assertEqual(hotel.available_rooms, 50)
        self.assertEqual(hotel.reservations, [])

    def test_to_dict_values_match(self):
        """to_dict values match the hotel attributes."""
        hotel = Hotel("H001", "Grand Plaza", "New York", 50)
        data = hotel.to_dict()
        self.assertEqual(data["hotel_id"], "H001")
        self.assertEqual(data["name"], "Grand Plaza")
        self.assertEqual(data["city"], "New York")
        self.assertEqual(data["total_rooms"], 50)
        self.assertEqual(data["available_rooms"], 50)
        self.assertEqual(data["reservations"], [])

    def test_from_dict_creates_hotel(self):
        """from_dict correctly reconstructs a Hotel object."""
        data = {
            "hotel_id": "H001",
            "name": "Grand Plaza",
            "city": "New York",
            "total_rooms": 50,
            "available_rooms": 48,
            "reservations": ["R001", "R002"],
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.hotel_id, "H001")
        self.assertEqual(hotel.available_rooms, 48)
        self.assertEqual(hotel.reservations, ["R001", "R002"])
        
    def test_create_hotel_success(self):
        """create_hotel returns a Hotel object on success."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            hotel = Hotel.create_hotel("H001", "Grand Plaza", "New York", 50)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.hotel_id, "H001")
    
    def test_create_hotel_duplicate_id_returns_none(self):
        """[NEGATIVE] create_hotel returns None if hotel ID already exists."""
        with patch("src.hotel.HOTELS_FILE", self.temp_file):
            Hotel.create_hotel("H001", "Grand Plaza", "New York", 50)
            result = Hotel.create_hotel("H001", "Another Hotel", "Boston", 20)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
