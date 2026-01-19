from enum import Enum
from datetime import datetime

class UserRole(Enum):
    STUDENT = "Student"
    LECTURER = "Lecturer"
    ADMIN = "Admin"

class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"

class User:
    """
    User class representing the 'Users' table in the Data Model [cite: 840-843].
    Contains common attributes for all accounts.
    """
    def __init__(self, user_id, username, password, full_name, email, phone, role, status="ACTIVE", failed_login_attempts=0, lockout_time=None):
        self.user_id = user_id
        self.username = username
        self.password = password  # Note: Should store hash, not plain text (NFR-09)
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.role = role
        self.status = status
        self.failed_login_attempts = failed_login_attempts
        self.lockout_time = lockout_time

    def is_locked(self):
        """Check if the account is currently locked (FR-01)"""
        return self.status == UserStatus.LOCKED.value