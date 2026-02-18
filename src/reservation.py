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
    
    def __init__(self):
        pass

    @staticmethod
    def create_reservation():
        pass

    @staticmethod
    def cancel_reservation():
        pass

    @staticmethod
    def display_reservation():
        pass