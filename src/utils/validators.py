import re

class Validator:
    """
    Input validation utility for the Authentication Module
    (FR-01, FR-03, FR-04).

    This class provides reusable validation methods to ensure
    that user input follows required formats and security rules
    before business logic is executed.
    """

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email format.

        Used in:
        - UC01: Login (FR-01)
        - UC04: Reset / Forgot Password (FR-04)

        :param email: Email address provided by user
        :return: True if email format is valid, otherwise False
        """
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_password(password: str) -> bool:
        """
        Validate password strength according to security rules.

        Password rules (FR-03):
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Used in:
        - UC03: Change Password (FR-03)
        - UC04: Reset Password (FR-04)

        :param password: Plain-text password
        :return: True if password meets all rules, otherwise False
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*]", password):
            return False
        return True
