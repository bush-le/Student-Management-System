import re

def validate_email(email):
    """
    FR-06: Validate email format.
    Uses standard Regular Expression.
    """
    if not email:
        return False
    
    # Structure: name@domain.extension
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_phone(phone):
    """
    FR-06: Validate phone number length and format.
    Ensure it contains only digits and has a length of 10-11 characters (Vietnam standard).
    """
    if not phone:
        return False
    
    # Check for digits only and appropriate length
    phone_regex = r'^\d{10,11}$'
    return re.match(phone_regex, phone) is not None

def validate_password_strength(password):
    """
    FR-03: Check password strength.
    Requirements: At least 8 characters, including uppercase, lowercase, digit, and special character.
    """
    if len(password) < 8:
        return False
        
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    return all([has_upper, has_lower, has_digit, has_special])

def validate_grade_input(score):
    """
    FR-12: Validate score range from 0 to 10 [cite: 98, 577-580].
    """
    try:
        val = float(score)
        return 0 <= val <= 10
    except (ValueError, TypeError):
        return False