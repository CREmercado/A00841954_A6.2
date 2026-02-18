"""
reservation.py - Reservation class for the Reservation System.

Handles reservation creation and cancellation linking
customers and hotels, with JSON file persistence.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import json
import os
from datetime import date

import src.hotel as hotel_module
import src.customer as customer_module
from .utils.constants import (
    ERROR_PREFIX,
    SUCCESS_PREFIX,
    WARNING_PREFIX,
    RESERVATIONS_FILE,
    ACTIVE_STATUS
)


def _load_reservations():
    """Load reservations from the JSON file."""
    if not os.path.exists(RESERVATIONS_FILE):
        return {}
    try:
        with open(RESERVATIONS_FILE, "r", encoding="utf-8") as file:
            print(f"{WARNING_PREFIX} Reservations file is being loaded...")
            return json.load(file)
    except (json.JSONDecodeError, IOError) as error:
        print(f"{ERROR_PREFIX} Could not load reservations file: {error}")
        return {}


def _save_reservations(reservations):
    """Save reservations dictionary to the JSON file."""
    os.makedirs(os.path.dirname(RESERVATIONS_FILE), exist_ok=True)
    try:
        with open(RESERVATIONS_FILE, "w", encoding="utf-8") as file:
            json.dump(reservations, file, indent=4)
            print(f"{SUCCESS_PREFIX} Reservations saved successfully.")
    except IOError as error:
        print(f"{ERROR_PREFIX} Could not save reservations file: {error}")


class Reservation:
    
    def __init__(self, reservation_id, customer_id, hotel_id, check_in, check_out):
        """Initialize a Reservation."""
        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.hotel_id = hotel_id
        self.check_in = check_in
        self.check_out = check_out
        self.status = ACTIVE_STATUS
    
    def to_dict(self):
        """Reservation to a dictionary."""
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "status": self.status,
        }
    
    @staticmethod
    def from_dict(data):
        """Reservation from a dictionary."""
        res = Reservation(
            reservation_id=data["reservation_id"],
            customer_id=data["customer_id"],
            hotel_id=data["hotel_id"],
            check_in=data["check_in"],
            check_out=data["check_out"],
        )
        res.status = data.get("status", ACTIVE_STATUS)
        return res

    @staticmethod
    def create_reservation():
        pass

    @staticmethod
    def cancel_reservation():
        pass

    @staticmethod
    def display_reservation():
        pass