from database.repository import BaseRepository
from models.user import User

class UserRepository(BaseRepository):
    def get_by_email(self, email):
        """Get user by email for login check"""
        # Need to retrieve sensitive fields like password, failed_attempts for logic processing
        sql = "SELECT * FROM Users WHERE email = %s"
        row = self.execute_query(sql, (email,), fetch_one=True)
        if not row: return None
        return User(**row)

    def update_login_stats(self, user_id, failed_attempts, status, lockout_time=None):
        """Update login status (lock, unlock, reset failed attempts)"""
        sql = """
            UPDATE Users 
            SET failed_login_attempts = %s, status = %s, lockout_time = %s 
            WHERE user_id = %s
        """
        return self.execute_query(sql, (failed_attempts, status, lockout_time, user_id))
    
    def update_password(self, user_id, new_password_hash):
        """Change password"""
        sql = "UPDATE Users SET password = %s WHERE user_id = %s"
        return self.execute_query(sql, (new_password_hash, user_id))

    def save_reset_token(self, email, hashed_token, expiry_time):
        """Save OTP and expiration time"""
        sql = "UPDATE Users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s"
        return self.execute_query(sql, (hashed_token, expiry_time, email))

    def clear_reset_token(self, email):
        """clear token affter reset"""
        sql = "UPDATE Users SET reset_token = NULL, reset_token_expiry = NULL WHERE email = %s"
        return self.execute_query(sql, (email,))

    def get_all(self): pass
    def get_by_id(self, id): 
        row = self.execute_query("SELECT * FROM Users WHERE user_id=%s", (id,), fetch_one=True)
        return User(**row) if row else None
    def add(self, entity): pass
    def update(self, entity): pass
    def delete(self, id): pass