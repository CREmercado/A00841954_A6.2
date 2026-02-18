"""
hotel.py - Hotel class for the Reservation System.

Handles hotel creation, deletion, display, modification,
room reservation and cancellation with JSON file persistence.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

from .utils.file_manager import load_json, save_json
from .utils.constants import (
    ERROR_PREFIX,
    WARNING_PREFIX,
    HOTELS_FILE,
)


def _load_hotels():
    """Load hotels from the JSON file."""
    return load_json(HOTELS_FILE, "Hotels")
    

def _save_hotels(hotels):
    """Save hotels dictionary to the JSON file."""
    save_json(HOTELS_FILE, hotels, "Hotels")


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
        print(f"{WARNING_PREFIX} Creating Hotel with ID '{hotel_id}'...")
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
        print(f"{WARNING_PREFIX} Deleting Hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False
        del hotels[hotel_id]
        _save_hotels(hotels)
        return True

    @staticmethod
    def modify_hotel(hotel_id, name=None, location=None, total_rooms=None):
        """Modify hotel."""
        print(f"{WARNING_PREFIX} Modifying Hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False
        if name:
            hotels[hotel_id]["name"] = name
        if location:
            hotels[hotel_id]["location"] = location
        if total_rooms is not None:
            diff = total_rooms - hotels[hotel_id]["total_rooms"]
            hotels[hotel_id]["total_rooms"] = total_rooms
            hotels[hotel_id]["available_rooms"] = max(
                0, hotels[hotel_id]["available_rooms"] + diff
            )
        _save_hotels(hotels)
        return True

    @staticmethod
    def display_hotel(hotel_id):
        """Display hotel."""
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
    def reserve_room(hotel_id, reservation_id):
        """Reserve a hotel room."""
        print(f"{WARNING_PREFIX} Reserving room in Hotel with ID'{hotel_id}' "
              f"for Reservation with ID '{reservation_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False
        hotel = hotels[hotel_id]
        if hotel["available_rooms"] <= 0:
            print(f"{ERROR_PREFIX} No available rooms in Hotel with ID '{hotel_id}'.")
            return False
        if reservation_id in hotel["reservations"]:
            print(f"{ERROR_PREFIX} Reservation '{reservation_id}' already exists "
                  f"in hotel '{hotel_id}'.")
            return False
        hotel["available_rooms"] -= 1
        hotel["reservations"].append(reservation_id)
        _save_hotels(hotels)
        return True
    
    @staticmethod
    def cancel_room_reservation(hotel_id, reservation_id):
        """Cancel hotel room reservation."""
        print(f"{WARNING_PREFIX} Canceling Reservation with ID '{reservation_id}' "
              f"in Hotel with ID '{hotel_id}'...")
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False
        hotel = hotels[hotel_id]
        if reservation_id not in hotel["reservations"]:
            print(f"{ERROR_PREFIX} Reservation with ID '{reservation_id}' not found "
                  f"in Hotel with ID '{hotel_id}'.")
            return False
        hotel["reservations"].remove(reservation_id)
        hotel["available_rooms"] = min(
            hotel["available_rooms"] + 1,
            hotel["total_rooms"]
        )
        _save_hotels(hotels)
        return True