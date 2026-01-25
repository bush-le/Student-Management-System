from datetime import datetime, timedelta
from database.repositories.user_repo import UserRepository
from utils.security import Security
from utils.email_service import EmailService
from utils.validators import Validators

class AuthController:
    def __init__(self):
        # Lazy load UserRepository
        self._user_repo = None

    @property
    def user_repo(self):
        if self._user_repo is None: self._user_repo = UserRepository()
        return self._user_repo

    def login(self, email, password):
        """Handles login with account lockout logic"""
        """Handles login with account lockout logic""" # Handles login with account lockout logic
        # 1. Find user via Repository
        user = self.user_repo.get_by_email(email)
        
        if not user:
            return None, "Invalid username or password."

        # 2. Check lock status (LOCKED)
        if user.status == 'LOCKED':
            if user.lockout_time:
                lockout_duration = timedelta(minutes=30)
                if datetime.now() > user.lockout_time + lockout_duration:
                    # Lockout expired -> Unlock
                    self.user_repo.update_login_stats(user.user_id, 0, 'ACTIVE', None)
                    user.status = 'ACTIVE'
                    user.failed_login_attempts = 0 # Reset
                else: # Still locked
                    # Still locked
                    remaining = (user.lockout_time + lockout_duration) - datetime.now()
                    minutes_left = round(remaining.total_seconds() / 60)
                    return None, f"Account locked. Try again in {minutes_left} minutes."
            else:
                return None, "Account is locked administratively."

        # 3. Check password (PARAMETER ORDER CORRECTED)
        # Correct standard: verify_password(HASH_IN_DB, ENTERED_PASSWORD)
        if Security.verify_password(user.password, password):
            # Success
            if user.failed_login_attempts > 0:
                self.user_repo.update_login_stats(user.user_id, 0, 'ACTIVE', None)
            return user, "Login successful."
        
        else:
            # Failed
            new_attempts = user.failed_login_attempts + 1 # Failure
            if new_attempts >= 5:
                self.user_repo.update_login_stats(user.user_id, new_attempts, 'LOCKED', datetime.now())
                msg = "Account locked due to multiple failed attempts (30 mins)."
            else:
                self.user_repo.update_login_stats(user.user_id, new_attempts, user.status, user.lockout_time)
                remaining = 5 - new_attempts
                msg = f"Invalid username or password. Remaining attempts: {remaining}"
            
            return None, msg

    def change_password(self, user_id, old_pass, new_pass): # Changes password
        """Changes password"""
        if not Security.validate_password_strength(new_pass):
            return False, "Password weak: min 8 chars, uppercase, number, special char."

        user = self.user_repo.get_by_id(user_id)
        
        # PARAMETER ORDER CORRECTED: verify_password(HASH, PLAIN)
        if not user or not Security.verify_password(user.password, old_pass):
            return False, "Incorrect current password."

        hashed_new = Security.hash_password(new_pass)
        self.user_repo.update_password(user_id, hashed_new)
        return True, "Password changed successfully."
    
    def request_password_reset(self, email): # Sends OTP for password reset
        """Sends OTP for password reset"""
        if not Validators.is_valid_email(email):
            return False, "Invalid email format."

        user = self.user_repo.get_by_email(email)
        if not user:
            return False, "User ID or Email not found."

        otp = Security.generate_otp()
        hashed_otp = Security.hash_password(otp)
        expiry = datetime.now() + timedelta(minutes=15)

        self.user_repo.save_reset_token(email, hashed_otp, expiry)

        if EmailService.send_recovery_email(email, otp):
            return True, "Recovery code sent successfully."
        return False, "Failed to send email."
    
    def reset_password(self, email, otp, new_password): # Resets password using OTP
        """Resets password using OTP""" # Resets password using OTP
        user = self.user_repo.get_by_email(email)
        
        if not user or not user.reset_token:
            return False, "Invalid request."
        
        if datetime.now() > user.reset_token_expiry:
            return False, "The recovery OTP has expired. Please request a new one."
            
        # PARAMETER ORDER CORRECTED: verify_password(HASH_TOKEN, OTP_INPUT)
        if not Security.verify_password(user.reset_token, otp): 
            return False, "Invalid recovery code."

        if not Security.validate_password_strength(new_password):
            return False, "Password weak."

        hashed_pw = Security.hash_password(new_password)
        self.user_repo.update_password(user.user_id, hashed_pw)
        self.user_repo.clear_reset_token(email)
        
        return True, "Password reset successfully."