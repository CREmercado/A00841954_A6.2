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