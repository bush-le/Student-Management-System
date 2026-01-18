class User:
    """
    User domain model used across the Authentication Module
    (FR-01 to FR-04).

    This class represents a system user and stores authentication-related
    attributes such as credentials, role, account status, and login attempts.
    """

    def __init__(
        self,
        user_id,
        email,
        password,
        role,
        status,
        failed_attempts=0
    ):
        """
        Initialize a User object.

        :param user_id: Unique identifier of the user
        :param email: Registered email address
        :param password: Hashed password
        :param role: User role (Student, Lecturer, Administrator)
        :param status: Account status (ACTIVE / LOCKED)
        :param failed_attempts: Number of failed login attempts (FR-01)
        """
        self.user_id = user_id
        self.email = email
        self.password = password
        self.role = role
        self.status = status
        self.failed_attempts = failed_attempts

    def is_active(self) -> bool:
        """
        Check whether the user account is active.

        Used in:
        - UC01: Login (FR-01)

        :return: True if account status is ACTIVE
        """
        return self.status == "ACTIVE"
