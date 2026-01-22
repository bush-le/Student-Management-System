from datetime import datetime, timedelta
from database.repositories.user_repo import UserRepository
from utils.security import Security
from utils.email_service import EmailService

class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()

    def login(self, email, password):
        """
        Xử lý đăng nhập với logic khóa tài khoản (Lockout Mechanism)
        """
        # 1. Tìm user qua Repository
        user = self.user_repo.get_by_email(email)
        
        if not user:
            return None, "Invalid username or password."

        # 2. Kiểm tra trạng thái khóa (LOCKED)
        if user.status == 'LOCKED':
            if user.lockout_time:
                # [cite_start]Logic: Kiểm tra hết hạn khóa (30 phút) [cite: 29-35]
                lockout_duration = timedelta(minutes=30)
                if datetime.now() > user.lockout_time + lockout_duration:
                    # Hết hạn khóa -> Mở khóa
                    self.user_repo.update_login_stats(user.user_id, 0, 'ACTIVE', None)
                    user.status = 'ACTIVE' # Cập nhật object tạm
                else:
                    # Vẫn còn khóa -> Tính thời gian còn lại
                    remaining = (user.lockout_time + lockout_duration) - datetime.now()
                    minutes_left = round(remaining.total_seconds() / 60)
                    return None, f"Account locked. Try again in {minutes_left} minutes."
            else:
                return None, "Account is locked administratively."

        # 3. Kiểm tra mật khẩu
        if Security.verify_password(password, user.password):
            # Thành công: Reset số lần sai về 0 nếu cần
            if user.failed_login_attempts > 0:
                self.user_repo.update_login_stats(user.user_id, 0, 'ACTIVE', None)
            return user, "Login successful."
        
        else:
            # Thất bại: Tăng số lần sai
            new_attempts = user.failed_login_attempts + 1
            max_attempts = 5
            
            if new_attempts >= max_attempts:
                # Quá 5 lần -> Khóa tài khoản
                self.user_repo.update_login_stats(user.user_id, new_attempts, 'LOCKED', datetime.now())
                msg = "Account locked due to multiple failed attempts (30 mins)."
            else:
                # Chưa quá 5 lần -> Cập nhật số lần sai
                self.user_repo.update_login_stats(user.user_id, new_attempts, user.status, user.lockout_time)
                msg = "Invalid username or password."
            
            return None, msg

    def change_password(self, user_id, old_pass, new_pass):
        """Đổi mật khẩu"""
        # Validate input
        if not Security.validate_password_strength(new_pass):
            return False, "Password weak: min 8 chars, uppercase, number, special char."

        # Lấy user để check pass cũ
        user = self.user_repo.get_by_id(user_id)
        if not user or not Security.verify_password(old_pass, user.password):
            return False, "Incorrect current password."

        # Update pass mới
        hashed_new = Security.hash_password(new_pass)
        self.user_repo.update_password(user_id, hashed_new)
        return True, "Password changed successfully."

    def request_password_reset(self, email):
        """Gửi OTP quên mật khẩu"""
        user = self.user_repo.get_by_email(email)
        if not user:
            # Fake success để tránh lộ email (Security Best Practice)
            return False, "User ID or Email not found."

        # Tạo OTP
        otp = Security.generate_otp()
        hashed_otp = Security.hash_password(otp) # Hash OTP trước khi lưu xuống DB
        expiry = datetime.now() + timedelta(minutes=15)

        # Lưu xuống DB qua Repo
        self.user_repo.save_reset_token(email, hashed_otp, expiry)

        # Gửi email
        if EmailService.send_recovery_email(email, otp):
            return True, "Recovery code sent successfully."
        return False, "Failed to send email."

    def reset_password(self, email, otp, new_password):
        """Reset mật khẩu bằng OTP"""
        user = self.user_repo.get_by_email(email)
        
        # Validate các điều kiện
        if not user or not user.reset_token:
            return False, "Invalid request."
        
        if datetime.now() > user.reset_token_expiry:
            return False, "Code expired."
            
        if not Security.verify_password(otp, user.reset_token): # Verify OTP đã hash
            return False, "Invalid recovery code."

        if not Security.validate_password_strength(new_password):
            return False, "Password weak."

        # Thực hiện đổi pass và xóa token
        hashed_pw = Security.hash_password(new_password)
        self.user_repo.update_password(user.user_id, hashed_pw)
        self.user_repo.clear_reset_token(email)
        
        return True, "Password reset successfully."