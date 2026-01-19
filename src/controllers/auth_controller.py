from database.connection import DatabaseConnection
from models.user import User, UserRole, UserStatus
from utils.security import Security

class AuthController:
    def login(self, email, password):
        """
        FR-01: User Login [cite: 29-35].
        Validate email, password, account status, and role.
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Find user by email
            query = "SELECT * FROM Users WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()

            if not user_data:
                return None, "Email not found."

            # 2. Check lock status (FR-01)
            if user_data['status'] == 'LOCKED':
                return None, "Account is locked due to too many failed attempts."

            # 3. Verify password (NFR-09)
            if Security.verify_password(user_data['password'], password):
                # Reset failed login attempts
                cursor.execute("UPDATE Users SET failed_login_attempts = 0 WHERE user_id = %s", (user_data['user_id'],))
                conn.commit()
                
                # Return basic User object with success message
                current_user = User(**user_data)
                return current_user, "Login successful."
            else:
                # Increment failed login attempts
                cursor.execute("UPDATE Users SET failed_login_attempts = failed_login_attempts + 1 WHERE user_id = %s", (user_data['user_id'],))
                conn.commit()
                return None, "Invalid password."

        except Exception as e:
            return None, f"System Error: {str(e)}"
        finally:
            if conn.is_connected():
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