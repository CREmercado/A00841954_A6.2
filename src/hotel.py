"""
hotel.py - Hotel class for the Reservation System.

Handles hotel creation, deletion, display, modification,
room reservation and cancellation with JSON file persistence.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import json
import os

from .constants import ERROR_PREFIX, SUCCESS_PREFIX, WARNING_PREFIX, HOTELS_FILE

def _load_hotels():
    """Load hotels from the JSON file."""
    if not os.path.exists(HOTELS_FILE):
        return {}
    try:
        with open(HOTELS_FILE, "r", encoding="utf-8") as file:
            print(f"{WARNING_PREFIX} Hotels file is being loaded. Ensure it is not corrupted.")
            return json.load(file)
    except (json.JSONDecodeError, IOError) as error:
        print(f"{ERROR_PREFIX} Could not load hotels file: {error}")
        return {}
    
def _save_hotels(hotels):
    """Save hotels dictionary to the JSON file."""
    os.makedirs(os.path.dirname(HOTELS_FILE), exist_ok=True)
    try:
        with open(HOTELS_FILE, "w", encoding="utf-8") as file:
            json.dump(hotels, file, indent=4)
            print(f"{SUCCESS_PREFIX} Hotels saved successfully.")
    except IOError as error:
        print(f"{ERROR_PREFIX} Could not save hotels file: {error}")

class Hotel:

    def __init__(self, hotel_id, name, city, total_rooms):
        """Initialize a Hotel."""
        self.hotel_id = hotel_id
        self.name = name
        self.city = city
        self.total_rooms = total_rooms
        self.available_rooms = total_rooms
        self.reservations = []
    
    def to_dict(self):
        """Hotel to a dictionary."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "city": self.city,
            "total_rooms": self.total_rooms,
            "available_rooms": self.available_rooms,
            "reservations": self.reservations,
        }

    @staticmethod
    def from_dict(data):
        """Hotel from a dictionary."""
        hotel = Hotel(
            hotel_id=data["hotel_id"],
            name=data["name"],
            city=data["city"],
            total_rooms=data["total_rooms"],
        )
        hotel.available_rooms = data.get("available_rooms", data["total_rooms"])
        hotel.reservations = data.get("reservations", [])
        return hotel

    @staticmethod
    def create_hotel(hotel_id, name, city, total_rooms):
        """Create hotel."""
        print(f"{WARNING_PREFIX} Creating hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' already exists.")
            return None
        hotel = Hotel(hotel_id, name, city, total_rooms)
        hotels[hotel_id] = hotel.to_dict()
        _save_hotels(hotels)
        return hotel
    
    @staticmethod
    def delete_hotel(hotel_id):
        """Delete hotel."""
        print(f"{WARNING_PREFIX} Deleting hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False
        del hotels[hotel_id]
        _save_hotels(hotels)
        return True

    @staticmethod
    def display_hotel(hotel_id):
        """Display hotel."""
        print(f"{WARNING_PREFIX} Displaying hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return None
        data = hotels[hotel_id]
        print("Hotel Information: ")
        print(f"  - ID            : {data['hotel_id']}")
        print(f"  - Name          : {data['name']}")
        print(f"  - City          : {data['city']}")
        print(f"  - Rooms         : {data['total_rooms']} total, "
              f"{data['available_rooms']} available")
        print(f"  - Reservations  : {data['reservations']}")
        return Hotel.from_dict(data)

    @staticmethod
    def modify_hotel(hotel_id, name=None, city=None, total_rooms=None):
        """Modify hotel."""
        print(f"{WARNING_PREFIX} Modifying hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False
        if name:
            hotels[hotel_id]["name"] = name
        if city:
            hotels[hotel_id]["city"] = city
        if total_rooms is not None:
            diff = total_rooms - hotels[hotel_id]["total_rooms"]
            hotels[hotel_id]["total_rooms"] = total_rooms
            hotels[hotel_id]["available_rooms"] = max(
                0, hotels[hotel_id]["available_rooms"] + diff
            )
        _save_hotels(hotels)
        return True