from .user import User

class Student(User):
    def __init__(self, user_data, student_id, student_code, major, dept_id, academic_year, gpa=0.0, academic_status="ACTIVE", dept_name=None):
        # Call parent User class init
        # user_data is a dict containing: user_id, username, full_name, email...
        super().__init__(**user_data)
        
        self.student_id = student_id
        self.student_code = student_code
        self.major = major
        self.dept_id = dept_id
        self.academic_year = academic_year
        self.gpa = float(gpa) if gpa else 0.0
        self.academic_status = academic_status
        # Extended field (not in Students table but available when joined)
        self.dept_name = dept_name

    @classmethod
    def from_db_row(cls, row):
        """Factory method: Creates a Student object from a DB data row (Dictionary)."""
        if not row:
            return None
        
        # Separate User data (based on column names in Users table)
        user_keys = ['user_id', 'username', 'password', 'full_name', 'email', 'phone', 'role', 'status', 'address', 'dob']
        # Filter keys existing in row
        user_data = {k: row.get(k) for k in user_keys if k in row}
        # Create Student object
        return cls(
            user_data=user_data,
            student_id=row.get('student_id'),
            student_code=row.get('student_code'),
            major=row.get('major'),
            dept_id=row.get('dept_id'),
            academic_year=row.get('academic_year'),
            gpa=row.get('gpa'),
            academic_status=row.get('academic_status'),
            dept_name=row.get('dept_name') # Retrieved from Departments table when joined
        )