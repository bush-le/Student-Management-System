import re
from datetime import datetime

class Validators:
    """
    Helper class for validating input data across the application.
    """

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        FR-06: Validate standard email format.
        """
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        FR-06: Validate phone number (VN Standard: 10-11 digits, starts with 0).
        """
        if not phone:
            return False
        pattern = r'^0\d{9,10}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def is_valid_grade(score) -> bool:
        """
        FR-12: Validate score must be a float between 0.0 and 10.0.
        """
        try:
            val = float(score)
            return 0.0 <= val <= 10.0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """
        Validate date format (YYYY-MM-DD).
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False