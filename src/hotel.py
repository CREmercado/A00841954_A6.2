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
    """
    Load and return the hotels dictionary from the JSON file.

    Centralizes persistence logic to keep business logic separated
    from storage concerns.
    """
    return load_json(HOTELS_FILE, "Hotels")


def _save_hotels(hotels):
    """
    Persist the given hotels dictionary to the JSON file.

    Args:
        hotels (dict): Dictionary containing all hotel records.
    """
    save_json(HOTELS_FILE, hotels, "Hotels")


class Hotel:
    """
    Represents a hotel in the reservation system.

    Encapsulates hotel state and provides static methods
    to manage persistence operations.
    """

    def __init__(self, hotel_id, name, city, total_rooms):
        """
        Initialize a Hotel instance.

        Args:
            hotel_id (str): Unique identifier of the hotel.
            name (str): Name of the hotel.
            city (str): City where the hotel is located.
            total_rooms (int): Total number of rooms available.
        """
        # Core hotel identity attributes
        self.hotel_id = hotel_id
        self.name = name
        self.city = city

        # Capacity management attributes
        self.total_rooms = total_rooms
        self.available_rooms = total_rooms

        # List of active reservation IDs
        self.reservations = []

    def to_dict(self):
        """
        Convert the Hotel instance into a serializable dictionary.

        Returns:
            dict: Dictionary representation suitable for JSON storage.
        """
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
        """
        Reconstruct a Hotel instance from persisted dictionary data.

        Ensures backward compatibility by safely retrieving optional fields.

        Args:
            data (dict): Dictionary containing hotel data.

        Returns:
            Hotel: A reconstructed Hotel object.
        """
        hotel = Hotel(
            hotel_id=data["hotel_id"],
            name=data["name"],
            city=data["city"],
            total_rooms=data["total_rooms"],
        )

        # Preserve stored availability or default to total rooms
        hotel.available_rooms = data.get(
            "available_rooms",
            data["total_rooms"]
        )

        # Preserve stored reservations or initialize empty list
        hotel.reservations = data.get("reservations", [])

        return hotel

    @staticmethod
    def create_hotel(hotel_id, name, city, total_rooms):
        """
        Create and persist a new hotel if the ID does not already exist.

        Returns:
            Hotel | None: The created Hotel object if successful,
            otherwise None if the ID already exists.
        """
        print(f"{WARNING_PREFIX} Creating Hotel with ID '{hotel_id}'...")

        # Load current state from persistence layer
        hotels = _load_hotels()

        # Ensure uniqueness of hotel ID
        if hotel_id in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' already exists.")
            return None

        # Instantiate hotel domain object
        hotel = Hotel(hotel_id, name, city, total_rooms)

        # Store serialized representation
        hotels[hotel_id] = hotel.to_dict()

        # Persist updated state
        _save_hotels(hotels)

        return hotel

    @staticmethod
    def delete_hotel(hotel_id):
        """
        Delete a hotel by ID.

        Returns:
            bool: True if deletion was successful,
            False if the hotel was not found.
        """
        print(f"{WARNING_PREFIX} Deleting Hotel with ID '{hotel_id}'...")

        # Load persisted hotels
        hotels = _load_hotels()

        # Validate existence before deletion
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False

        # Remove hotel entry
        del hotels[hotel_id]

        # Persist changes
        _save_hotels(hotels)

        return True

    @staticmethod
    def modify_hotel(hotel_id, name=None, location=None, total_rooms=None):
        """
        Modify hotel attributes.

        Supports partial updates. If total_rooms changes,
        availability is adjusted accordingly.

        Returns:
            bool: True if modification was successful,
            False if the hotel was not found.
        """
        print(f"{WARNING_PREFIX} Modifying Hotel with ID '{hotel_id}'...")

        # Load current state
        hotels = _load_hotels()

        # Validate existence of hotel
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False

        # Update only provided attributes
        if name:
            hotels[hotel_id]["name"] = name

        if location:
            hotels[hotel_id]["location"] = location

        # Handle capacity adjustment if total_rooms changes
        if total_rooms is not None:
            # Calculate difference to maintain correct availability
            diff = total_rooms - hotels[hotel_id]["total_rooms"]

            hotels[hotel_id]["total_rooms"] = total_rooms

            # Ensure available rooms never drop below zero
            hotels[hotel_id]["available_rooms"] = max(
                0,
                hotels[hotel_id]["available_rooms"] + diff
            )

        # Persist updated state
        _save_hotels(hotels)

        return True

    @staticmethod
    def display_hotel(hotel_id):
        """
        Display hotel information and return corresponding object.

        Returns:
            Hotel | None: Hotel instance if found, otherwise None.
        """
        # Load persisted hotels
        hotels = _load_hotels()

        # Validate hotel existence
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return None

        data = hotels[hotel_id]

        # Present formatted information
        print("Hotel Information: ")
        print(f"  - ID            : {data['hotel_id']}")
        print(f"  - Name          : {data['name']}")
        print(f"  - City          : {data['city']}")
        print(f"  - Rooms         : {data['total_rooms']} total, "
              f"{data['available_rooms']} available")
        print(f"  - Reservations  : {data['reservations']}")

        # Reconstruct domain object before returning
        return Hotel.from_dict(data)

    @staticmethod
    def reserve_room(hotel_id, reservation_id):
        """
        Reserve a room in the specified hotel.

        Ensures:
            - Hotel exists
            - Rooms are available
            - Reservation ID is unique within the hotel

        Returns:
            bool: True if reservation was successful, otherwise False.
        """
        print(f"{WARNING_PREFIX} Reserving room in Hotel with ID'{hotel_id}' "
              f"for Reservation with ID '{reservation_id}'...")

        # Load current hotel state
        hotels = _load_hotels()

        # Validate hotel existence
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False

        hotel = hotels[hotel_id]

        # Check room availability
        if hotel["available_rooms"] <= 0:
            print(f"{ERROR_PREFIX} No available rooms in Hotel with "
                  f"ID '{hotel_id}'.")
            return False

        # Ensure reservation ID is not duplicated
        if reservation_id in hotel["reservations"]:
            print(f"{ERROR_PREFIX} Reservation '{reservation_id}' "
                  "already exists "
                  f"in hotel '{hotel_id}'.")
            return False

        # Decrease availability and register reservation
        hotel["available_rooms"] -= 1
        hotel["reservations"].append(reservation_id)

        # Persist changes
        _save_hotels(hotels)

        return True

    @staticmethod
    def cancel_room_reservation(hotel_id, reservation_id):
        """
        Cancel an existing room reservation.

        Ensures availability does not exceed total capacity.

        Returns:
            bool: True if cancellation was successful, otherwise False.
        """
        print(f"{WARNING_PREFIX} Canceling Reservation with "
              f"ID '{reservation_id}' in Hotel with ID '{hotel_id}'...")

        # Load current state
        hotels = _load_hotels()

        # Validate hotel existence
        if hotel_id not in hotels:
            print(f"{ERROR_PREFIX} Hotel with ID '{hotel_id}' not found.")
            return False

        hotel = hotels[hotel_id]

        # Validate reservation existence
        if reservation_id not in hotel["reservations"]:
            print(f"{ERROR_PREFIX} Reservation with ID '{reservation_id}' "
                  f"not found in Hotel with ID '{hotel_id}'.")
            return False

        # Remove reservation and increase availability safely
        hotel["reservations"].remove(reservation_id)

        hotel["available_rooms"] = min(
            hotel["available_rooms"] + 1,
            hotel["total_rooms"]
        )

        # Persist updated state
        _save_hotels(hotels)

        return True
