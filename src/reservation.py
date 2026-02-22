"""
reservation.py - Reservation class for the Reservation System.

Handles reservation creation and cancellation linking
customers and hotels, with JSON file persistence.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

from datetime import date

import src.hotel as hotel_module
import src.customer as customer_module
from .utils.file_manager import load_json, save_json
from .utils.constants import (
    ERROR_PREFIX,
    WARNING_PREFIX,
    RESERVATIONS_FILE,
    ACTIVE_STATUS,
    CANCELED_STATUS,
)


def _load_reservations():
    """
    Load and return the reservations dictionary from the JSON file.

    This helper centralizes persistence access, keeping file
    management separated from business logic.

    Returns:
        dict: Dictionary containing all reservation records.
    """
    return load_json(RESERVATIONS_FILE, "Reservations")


def _save_reservations(reservations):
    """
    Persist the reservations dictionary to the JSON file.

    Args:
        reservations (dict): Dictionary containing all reservations.
    """
    save_json(RESERVATIONS_FILE, reservations, "Reservations")


class Reservation:
    """
    Represents a hotel room reservation.

    This class encapsulates reservation data and provides static
    methods to manage reservation lifecycle operations, including
    creation, cancellation, display, and JSON persistence.
    """

    def __init__(self, reservation_id, customer_id, hotel_id, dates):
        """
        Initialize a Reservation instance.

        Args:
            reservation_id (str): Unique identifier of the reservation.
            customer_id (str): Identifier of the associated customer.
            hotel_id (str): Identifier of the associated hotel.
            dates (dict): Dictionary containing:
                - "check_in" (str): Check-in date.
                - "check_out" (str): Check-out date.
        """
        # Store reservation identity and associations
        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.hotel_id = hotel_id

        # Store grouped date information
        self.dates = dates

        # Default status is ACTIVE upon creation
        self.status = ACTIVE_STATUS

    def to_dict(self):
        """
        Convert the Reservation instance into a serializable dictionary.

        This method prepares the object for JSON persistence.

        Returns:
            dict: Dictionary representation of the reservation.
        """
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "check_in": self.dates["check_in"],
            "check_out": self.dates["check_out"],
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Reservation instance from a dictionary.

        This method reconstructs a Reservation object from
        persisted JSON data.

        Args:
            data (dict): Dictionary containing reservation data.

        Returns:
            Reservation: Reconstructed Reservation object.
        """
        # Instantiate Reservation with grouped dates
        res = Reservation(
            reservation_id=data["reservation_id"],
            customer_id=data["customer_id"],
            hotel_id=data["hotel_id"],
            dates={
                "check_in": data["check_in"],
                "check_out": data["check_out"],
            },
        )

        # Restore status (default to ACTIVE if not present)
        res.status = data.get("status", ACTIVE_STATUS)
        return res

    @staticmethod
    def create_reservation(reservation_id, customer_id, hotel_id,
                           check_in=None, check_out=None):
        """
        Create and persist a new reservation.

        Validates:
            - Reservation uniqueness
            - Customer existence
            - Hotel room availability

        If check-in or check-out dates are not provided,
        the current date is used as default.

        Returns:
            Reservation | None: Created Reservation object if successful,
            otherwise None if validation fails.
        """
        print(f"{WARNING_PREFIX} Attempting to create Reservation with "
              f"ID '{reservation_id}' for Customer with ID '{customer_id}' "
              f"at Hotel with ID '{hotel_id}'...")

        # Load existing reservations from persistence layer
        reservations = _load_reservations()

        # Ensure reservation IDs remain unique
        if reservation_id in reservations:
            print(f"{ERROR_PREFIX} Reservation with ID '{reservation_id}' "
                  "already exists.")
            return None

        # Validate customer existence via public interface
        if not customer_module.Customer.exists(customer_id):
            print(f"{ERROR_PREFIX} Customer with ID '{customer_id}' "
                  "not found.")
            return None

        # Attempt to reserve a room in the specified hotel
        if not hotel_module.Hotel.reserve_room(hotel_id, reservation_id):
            return None

        # Apply default dates if not provided
        if check_in is None:
            check_in = str(date.today())
        if check_out is None:
            check_out = str(date.today())

        # Instantiate domain object
        reservation = Reservation(
            reservation_id,
            customer_id,
            hotel_id,
            {
                "check_in": check_in,
                "check_out": check_out,
            },
        )

        # Store serialized reservation
        reservations[reservation_id] = reservation.to_dict()

        # Persist updated state
        _save_reservations(reservations)

        return reservation

    @staticmethod
    def cancel_reservation(reservation_id):
        """
        Cancel an existing reservation.

        Updates the reservation status to CANCELED and
        notifies the associated hotel to release the room.

        Returns:
            bool: True if cancellation was successful,
            False if reservation was not found or already canceled.
        """
        print(f"{WARNING_PREFIX} Attempting to cancel Reservation with "
              f"ID '{reservation_id}'...")

        # Load persisted reservations
        reservations = _load_reservations()

        # Validate existence
        if reservation_id not in reservations:
            print(f"{ERROR_PREFIX} Reservation with ID '{reservation_id}' "
                  "not found.")
            return False

        reservation = reservations[reservation_id]

        # Prevent duplicate cancellation
        if reservation["status"] == CANCELED_STATUS:
            print(f"{ERROR_PREFIX} Reservation with ID '{reservation_id}' "
                  "is already "
                  f"{CANCELED_STATUS}.")
            return False

        # Notify hotel module to release reserved room
        hotel_module.Hotel.cancel_room_reservation(
            reservation["hotel_id"], reservation_id
        )

        # Update reservation status
        reservations[reservation_id]["status"] = CANCELED_STATUS

        # Persist changes
        _save_reservations(reservations)

        return True

    @staticmethod
    def display_reservation(reservation_id):
        """
        Display reservation information and return
        the corresponding Reservation object.

        Returns:
            Reservation | None: Reservation instance if found,
            otherwise None.
        """
        # Load persisted reservations
        reservations = _load_reservations()

        # Validate existence
        if reservation_id not in reservations:
            print(f"{ERROR_PREFIX} Reservation '{reservation_id}' not found.")
            return None

        # Retrieve raw reservation data
        data = reservations[reservation_id]

        # Present formatted output to user interface
        print("Reservation Information: ")
        print(f"  - ID          : {data['reservation_id']}")
        print(f"  - Customer ID : {data['customer_id']}")
        print(f"  - Hotel ID    : {data['hotel_id']}")
        print(f"  - Check-in    : {data['check_in']}")
        print(f"  - Check-out   : {data['check_out']}")
        print(f"  - Status      : {data['status']}")

        # Reconstruct domain object before returning
        return Reservation.from_dict(data)
