import re
from datetime import datetime

# --- FR-06: Validate Personal Information  ---
def validate_email(email):
    """
    Validate standard email format.
    Valid example: student@test.com
    """
    if not email:
        return False
    # Basic regex for email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """
    Validate phone number: Contains only digits, length 10-11 characters (VN Standard).
    """
    if not phone:
        return False
    pattern = r'^\d{10,11}$'
    return re.match(pattern, phone) is not None

# --- FR-12: Validate Grade Input  ---
def validate_grade_input(score):
    """
    Validate score must be a float between 0.0 and 10.0.
    """
    try:
        val = float(score)
        return 0.0 <= val <= 10.0
    except (ValueError, TypeError):
        return False

# --- Helper for Admin ---
def validate_date_format(date_str):
    """
    Validate date format (YYYY-MM-DD) for student/semester management functions.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False