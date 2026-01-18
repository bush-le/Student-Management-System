import hashlib

class Security:
    """
    Security utility class for the Authentication Module
    (FR-01, FR-03, FR-04).

    This class provides cryptographic functions such as password hashing
    and verification, which are required for secure authentication.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password using SHA-256.

        Used in:
        - UC03: Change Password (FR-03)
        - UC04: Reset Password (FR-04)

        :param password: Plain-text password
        :return: SHA-256 hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify whether a plain-text password matches the stored hashed password.

        Used in:
        - UC01: Login (FR-01)
        - UC03: Change Password (FR-03)

        :param plain_password: Password entered by user
        :param hashed_password: Password stored in database
        :return: True if passwords match, otherwise False
        """
        return Security.hash_password(plain_password) == hashed_password
