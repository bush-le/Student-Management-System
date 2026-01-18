class EmailService:
    """
    Email service utility for the Authentication Module
    (FR-04 - Forgot / Reset Password).

    This class simulates communication with an external Email System
    to send password recovery instructions.
    """

    @staticmethod
    def send_reset_password(email: str, token: str):
        """
        Send a password reset email containing a time-limited reset token.

        Used in:
        - UC04: Reset / Forgot Password (FR-04)

        Note:
        This is a mock implementation for academic purposes.

        :param email: Recipient email address
        :param token: Password reset token (valid for 15 minutes)
        """
        print(f"[EMAIL SYSTEM] Sending password reset email to {email}")
        print(f"[EMAIL SYSTEM] Reset token: {token}")
