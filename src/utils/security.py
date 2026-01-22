import bcrypt
import secrets
import string
import re

class Security:
    """
    Utility class handling security, encryption, and sessions.
    UPDATED: Uses bcrypt for secure password hashing.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        NFR-09: Encrypt password before saving to DB.
        Uses BCrypt (Salt is automatically handled).
        """
        # Bcrypt yêu cầu bytes
        pwd_bytes = password.encode('utf-8')
        # Tạo salt và hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        # Trả về chuỗi decode để lưu vào Database (VARCHAR)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """
        Check if the provided password matches the hash in the DB.
        """
        if not stored_hash or not provided_password:
            return False
            
        try:
            # Chuyển đổi về bytes để so sánh
            stored_bytes = stored_hash.encode('utf-8')
            provided_bytes = provided_password.encode('utf-8')
            
            # Bcrypt tự trích xuất salt từ stored_hash để so sánh
            return bcrypt.checkpw(provided_bytes, stored_bytes)
            
        except ValueError as e:
            # Lỗi này xảy ra nếu stored_hash không phải chuẩn Bcrypt
            print(f"⚠️ Bcrypt Error: {e}") # Để xem lỗi chi tiết
            return False
        except Exception as e:
            print(f"System Error: {e}")
            return False

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        FR-03: Check password strength.
        Rules: Min 8 chars, Upper, Lower, Digit, Special char.
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        return all([has_upper, has_lower, has_digit, has_special])

    @staticmethod
    def generate_otp(length=6) -> str:
        """
        FR-04: Generate a 6-digit numeric OTP securely.
        Uses 'secrets' module instead of 'random'.
        """
        return ''.join(secrets.choice(string.digits) for _ in range(length))