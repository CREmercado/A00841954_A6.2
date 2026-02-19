"""
reservation_test.py - Unit tests for the Reservation class.

Tests cover creation, cancellation and display of reservations,
including negative cases and cross-entity validation.

Author: A00841954 Christian Erick Mercado Flores
Date: February 2026
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from src.hotel import Hotel, _load_hotels
from src.customer import Customer, _load_customers
from src.reservation import (
    Reservation,
    _load_reservations,
    _save_reservations,
)
from src.utils.constants import ACTIVE_STATUS, CANCELED_STATUS


class TestReservation(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
