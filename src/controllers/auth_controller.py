import time
import uuid
from models.user import User
from utils.security import Security
from utils.validators import Validator
from utils.email_service import EmailService


class AuthController:
    """
    Controller handling business logic for the Authentication Module
    (FR-01 to FR-04).

    Covered functionalities:
    - UC01: Login (FR-01)
    - UC02: Logout (FR-02)
    - UC03: Change Password (FR-03)
    - UC04: Reset / Forgot Password (FR-04)

    This class acts as a bridge between the View layer and the User Repository.
    Due to the fixed project structure, both Controller and Service
    responsibilities are handled within this class.
    """

    # ================= SYSTEM CONSTANTS =================
    MAX_FAILED_ATTEMPTS = 5
    RESET_TOKEN_EXPIRE_TIME = 900  # 15 minutes (FR-04)

    # In-memory storage (acceptable for academic project scope)
    _sessions = {}      # {user_id: role}
    _reset_tokens = {}  # {token: (user_id, created_timestamp)}

    def __init__(self, user_repository):
        """
        Initialize AuthController with a UserRepository.

        :param user_repository: Object responsible for database operations
        """
        self.user_repository = user_repository

    # ====================================================
    # ================= UC01: LOGIN ======================
    # ====================================================
    def login(self, email: str, password: str):
        """
        UC01 - Login (FR-01)

        Authenticate a user using email and password.

        Business rules:
        - Validate input data
        - Verify user existence and account status
        - Limit failed login attempts to 5
        - Lock account after exceeding failed attempts
        - Create user session upon successful login
        """
        # Step 1: Validate required input
        if not email or not password:
            return False, "Email and password are required"

        if not Validator.is_valid_email(email):
            return False, "Invalid email format"

        # Step 2: Retrieve user from database
        user = self._get_user_by_email(email)
        if not user:
            return False, "User not found"

        # Step 3: Check account status
        if not user.is_active():
            return False, "Account is locked or inactive"

        # Step 4: Verify password
        if not self._verify_password(user, password):
            return self._handle_failed_login(user)

        # Step 5: Handle successful login
        self._handle_successful_login(user)
        return True, user.role

    # ====================================================
    # ================= UC02: LOGOUT =====================
    # ====================================================
    def logout(self, user_id: int):
        """
        UC02 - Logout (FR-02)

        Terminate the active session of a logged-in user.
        """
        if user_id not in self._sessions:
            return False, "User not logged in"

        self._sessions.pop(user_id)
        return True, "Logout successful"

    # ====================================================
    # =============== UC03: CHANGE PASSWORD ===============
    # ====================================================
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
        confirm_password: str
    ):
        """
        UC03 - Change Password (FR-03)
        
        Allow an authenticated user to change their password.
        
        Business rules:
        - Verify current password
        - Validate new password strength
        - Require password confirmation
        - Update password securely
        """
        # Step 1: Validate required fields
        if not all([old_password, new_password, confirm_password]):
            return False, "All fields are required"

        # Step 2: Confirm password match
        if new_password != confirm_password:
            return False, "New password and confirmation do not match"

        # Step 3: Validate password strength
        if not Validator.is_valid_password(new_password):
            return False, "New password does not meet security requirements"

        # Step 4: Retrieve user and verify current password
        user = self._get_user_by_id(user_id)
        if not user:
            return False, "User not found"

        if not Security.verify_password(old_password, user.password):
            return False, "Current password is incorrect"

        # Step 5: Update password securely
        self._update_user_password(user.user_id, new_password)
        return True, "Password changed successfully"

    # ====================================================
    # ============ UC04: RESET PASSWORD ===================
    # ====================================================
    def request_password_reset(self, email: str):
        """
        UC04 - Reset Password (FR-04) - Step 1
        
        Generate a time-limited reset token and send it via email.
        """

        if not Validator.is_valid_email(email):
            return False, "Invalid email format"

        user = self._get_user_by_email(email)
        if not user:
            return False, "Email not found"

        # Generate reset token and store timestamp
        token = self._generate_reset_token(user.user_id)

        # Send reset email (mocked)
        EmailService.send_reset_password(user.email, token)
        return True, "Password reset email sent"

    def reset_password(
        self,
        token: str,
        new_password: str,
        confirm_password: str
    ):
        """
        UC04 - Reset Password (FR-04) - Step 2

        Verify reset token and update user password.
        """

        # Step 1: Validate reset token
        user_id = self._validate_reset_token(token)
        if not user_id:
            return False, "Invalid or expired reset token"

        # Step 2: Validate new password
        if new_password != confirm_password:
            return False, "Passwords do not match"

        if not Validator.is_valid_password(new_password):
            return False, "Password does not meet security requirements"

        # Step 3: Update password
        self._update_user_password(user_id, new_password)

        # Step 4: Clean up used token
        self._reset_tokens.pop(token)
        return True, "Password reset successfully"

    # ====================================================
    # =============== INTERNAL HELPER METHODS =============
    # ====================================================

    def _get_user_by_email(self, email: str):
        """
        Retrieve user object by email.
        """
        data = self.user_repository.get_user_by_email(email)
        return User(*data) if data else None

    def _get_user_by_id(self, user_id: int):
        """
        Retrieve user object by user ID.
        """
        data = self.user_repository.get_user_by_id(user_id)
        return User(*data) if data else None

    def _verify_password(self, user: User, password: str) -> bool:
        """
        Verify input password against stored hashed password.
        """
        return Security.verify_password(password, user.password)

    def _handle_failed_login(self, user: User):
        """
        Handle failed login attempts according to FR-01.
        Lock the account if the maximum number of attempts is exceeded.
        """
        self.user_repository.increase_failed_attempts(user.user_id)

        # Lock account if failed attempts exceed limit
        if user.failed_attempts + 1 >= self.MAX_FAILED_ATTEMPTS:
            self.user_repository.lock_account(user.user_id)
            return False, "Account locked due to multiple failed login attempts"

        remaining = self.MAX_FAILED_ATTEMPTS - (user.failed_attempts + 1)
        return False, f"Incorrect password. {remaining} attempts remaining."

    def _handle_successful_login(self, user: User):
        """
        Reset failed attempts counter and create session.
        """
        self.user_repository.reset_failed_attempts(user.user_id)
        self._sessions[user.user_id] = user.role

    def _generate_reset_token(self, user_id: int) -> str:
        """
        Generate and store a time-limited password reset token.
        """
        token = str(uuid.uuid4())
        self._reset_tokens[token] = (user_id, time.time())
        return token

    def _validate_reset_token(self, token: str):
        """
        Validate reset token existence and expiration.
        """
        if token not in self._reset_tokens:
            return None

        user_id, created_time = self._reset_tokens[token]
        if time.time() - created_time > self.RESET_TOKEN_EXPIRE_TIME:
            self._reset_tokens.pop(token)
            return None

        return user_id

    def _update_user_password(self, user_id: int, new_password: str):
        """
        Hash and update user password in database.
        """
        hashed_password = Security.hash_password(new_password)
        self.user_repository.update_password(user_id, hashed_password)
