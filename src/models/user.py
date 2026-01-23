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
    def __init__(self, user_id, username, password, full_name, email, phone, role, status="ACTIVE", failed_login_attempts=0, lockout_time=None, address=None, dob=None, reset_token=None, reset_token_expiry=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.role = role
        self.status = status
        self.failed_login_attempts = failed_login_attempts 
        self.lockout_time = lockout_time
        
        self.address = address
        self.dob = dob

        self.reset_token = reset_token
        self.reset_token_expiry = reset_token_expiry

    def is_locked(self):
        return self.status == UserStatus.LOCKED.value