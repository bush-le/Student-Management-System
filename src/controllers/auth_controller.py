from database.connection import DatabaseConnection
from models.user import User, UserRole, UserStatus
from utils.security import Security
from utils.email_service import EmailService
from datetime import datetime, timedelta

class AuthController:
    def login(self, email, password):
        """
        FR-01: User Login [cite: 29-35].
        Validate email, password, account status. Returns (user_object, message).
        """
        conn = DatabaseConnection.get_connection()
        if not conn:
            return None, "System Error: Could not connect to the database."
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Find user by email
            query = "SELECT * FROM Users WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
 
            # AF1: If user not found, return a generic error to prevent email enumeration.
            if not user_data:
                return None, "Invalid username or password."
 
            user = User(**user_data)
 
            # AF2: Check lock status (FR-01)
            if user.status == 'LOCKED':
                # Check if the lockout is temporary and has expired
                if user.lockout_time:
                    lockout_duration = timedelta(minutes=30)
                    if datetime.now() > user.lockout_time + lockout_duration:
                        # Lockout expired, so unlock the account and proceed
                        cursor.execute("UPDATE Users SET status = 'ACTIVE', failed_login_attempts = 0, lockout_time = NULL WHERE user_id = %s", (user.user_id,))
                        conn.commit()
                        user.status = 'ACTIVE' # Update local object
                    else:
                        # Lockout is still active, calculate remaining time
                        remaining_time = (user.lockout_time + lockout_duration) - datetime.now()
                        minutes_left = round(remaining_time.total_seconds() / 60)
                        return None, f"Account locked. Please try again in {minutes_left} minutes."
                else:
                    # Account was likely locked by an admin (no lockout time)
                    return None, "Account is locked. Please contact an administrator."
 
            # 3. Verify password (NFR-09) [cite: 159]
            if Security.verify_password(user.password, password):
                # Reset failed login attempts if there were any
                if user.failed_login_attempts > 0:
                    cursor.execute("UPDATE Users SET failed_login_attempts = 0, lockout_time = NULL WHERE user_id = %s", (user.user_id,))
                    conn.commit()
                
                return user, "Login successful."
            else:
                # Increment failed login attempts and check for lockout
                new_attempts = user.failed_login_attempts + 1
                max_attempts = 5 # This should ideally be in a config file
                
                if new_attempts >= max_attempts:
                    # AF2.1, AF2.2: Lock account and set lockout time
                    cursor.execute("UPDATE Users SET failed_login_attempts = %s, status = 'LOCKED', lockout_time = NOW() WHERE user_id = %s", (new_attempts, user.user_id))
                    user.status = 'LOCKED'
                    msg = "Account locked due to multiple failed attempts. Please try again after 30 minutes."
                else:
                    cursor.execute("UPDATE Users SET failed_login_attempts = %s WHERE user_id = %s", (new_attempts, user.user_id))
                    msg = "Invalid username or password."
                
                conn.commit()
                user.failed_login_attempts = new_attempts
                return user, msg
        except Exception as e:
            return None, f"System Error: {str(e)}"
        finally:
            if conn and conn.is_connected():
                # cursor might not be defined if get_connection fails
                if 'cursor' in locals() and cursor:
                    cursor.close()
                conn.close()

    def change_password(self, user_id, old_pass, new_pass):
        """
        FR-03: Change Password [cite: 40-46].
        """
        if not Security.validate_password_strength(new_pass):
            return False, "Password must be at least 8 characters, include uppercase, number, special char."

        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Get current password
            cursor.execute("SELECT password FROM Users WHERE user_id = %s", (user_id,))
            record = cursor.fetchone()

            if not record or not Security.verify_password(record['password'], old_pass):
                return False, "Incorrect current password."

            # Hash new password and update
            hashed_new_pass = Security.hash_password(new_pass)
            cursor.execute("UPDATE Users SET password = %s WHERE user_id = %s", (hashed_new_pass, user_id))
            conn.commit()
            return True, "Password changed successfully."
        finally:
            conn.close()

    def request_password_reset(self, email):
        """
        UC04 - Step 2-5: Verify email, generate OTP, and send it.
        """
        with DatabaseConnection.get_cursor() as cursor:
            # Step 3: Verify user exists
            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                # AF1.2: User not found
                return False, "User ID or Email not found. Please check your information."

            # Step 4: Generate OTP and expiry
            otp = Security.generate_otp()
            hashed_otp = Security.hash_password(otp)
            expiry_time = datetime.now() + timedelta(minutes=15)

            # Store hashed OTP and expiry in DB
            cursor.execute(
                "UPDATE Users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s",
                (hashed_otp, expiry_time, email)
            )

            # Step 5: Send email
            email_sent = EmailService.send_recovery_email(email, otp)
            if not email_sent:
                return False, "Failed to send recovery email. Please try again later."

            return True, "Recovery code sent successfully."

    def reset_password(self, email, otp, new_password):
        """
        UC04 - Step 6-7: Verify OTP and reset the password.
        """
        with DatabaseConnection.get_cursor() as cursor:
            # Find user and check token validity
            cursor.execute("SELECT reset_token, reset_token_expiry FROM Users WHERE email = %s", (email,))
            record = cursor.fetchone()

            if not record or not record['reset_token']:
                return False, "Invalid request. Please start over."

            # AF2: Check if token is expired
            if datetime.now() > record['reset_token_expiry']:
                return False, "The recovery code has expired. Please request a new one."

            # Verify OTP
            if not Security.verify_password(record['reset_token'], otp):
                return False, "Invalid recovery code."

            # Step 6: Validate new password strength
            if not Security.validate_password_strength(new_password):
                return False, "Password must be at least 8 characters and contain uppercase, number, and special char."

            # Step 7: Update password and clear token
            hashed_password = Security.hash_password(new_password)
            cursor.execute("UPDATE Users SET password = %s, reset_token = NULL, reset_token_expiry = NULL WHERE email = %s", (hashed_password, email))
            return True, "Password has been reset successfully."