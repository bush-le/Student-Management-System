from database.repository import BaseRepository
from models.user import User

class UserRepository(BaseRepository):
    def get_by_email(self, email):
        """Lấy user theo email để check login"""
        # Cần lấy đủ các trường nhạy cảm như password, failed_attempts để xử lý logic
        sql = "SELECT * FROM Users WHERE email = %s"
        row = self.execute_query(sql, (email,), fetch_one=True)
        if not row: return None
        return User(**row)

    def update_login_stats(self, user_id, failed_attempts, status, lockout_time=None):
        """Cập nhật trạng thái đăng nhập (khóa, mở khóa, reset số lần sai)"""
        sql = """
            UPDATE Users 
            SET failed_login_attempts = %s, status = %s, lockout_time = %s 
            WHERE user_id = %s
        """
        return self.execute_query(sql, (failed_attempts, status, lockout_time, user_id))

    def update_password(self, user_id, new_password_hash):
        """Đổi mật khẩu"""
        sql = "UPDATE Users SET password = %s WHERE user_id = %s"
        return self.execute_query(sql, (new_password_hash, user_id))

    def save_reset_token(self, email, hashed_token, expiry_time):
        """Lưu OTP và thời gian hết hạn"""
        sql = "UPDATE Users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s"
        return self.execute_query(sql, (hashed_token, expiry_time, email))

    def clear_reset_token(self, email):
        """Xóa token sau khi reset thành công"""
        sql = "UPDATE Users SET reset_token = NULL, reset_token_expiry = NULL WHERE email = %s"
        return self.execute_query(sql, (email,))

    # Các hàm abstract bắt buộc
    def get_all(self): pass
    def get_by_id(self, id): 
        row = self.execute_query("SELECT * FROM Users WHERE user_id=%s", (id,), fetch_one=True)
        return User(**row) if row else None
    def add(self, entity): pass
    def update(self, entity): pass
    def delete(self, id): pass