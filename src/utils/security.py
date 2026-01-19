import hashlib
import re
import uuid

class Security:
    """
    Utility class handling security, encryption, and sessions.
    """

    @staticmethod
    def hash_password(password):
        """
        NFR-09: Encrypt password before saving to DB.
        Uses SHA-256 (Can be upgraded to bcrypt if additional libraries are installed).
        """
        # In reality, 'salt' should be added; here using basic SHA256 for the project
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(stored_hash, provided_password):
        """
        Check if the provided password matches the hash in the DB.
        """
        return stored_hash == hashlib.sha256(provided_password.encode()).hexdigest()

    @staticmethod
    def validate_password_strength(password):
        """
        FR-03: Check password strength [cite: 43-45].
        Rules:
        - Minimum 8 characters.
        - Contains uppercase, lowercase, digit, and special character.
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        # Special character: not alphanumeric
        has_special = any(not c.isalnum() for c in password)

        return all([has_upper, has_lower, has_digit, has_special])

    @staticmethod
    def generate_reset_token():
        """
        FR-04: Generate random token for Forgot Password function [cite: 52].
        """
        return str(uuid.uuid4())