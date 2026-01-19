from .user import User

class Student(User):
    """
    Student class inheriting from User.
    Maps to 'Students' table and has a 1-to-1 relationship with 'Users'.
    """
    def __init__(self, user_data, student_id, student_code, major, dept_id, academic_year, gpa=0.0, academic_status="ACTIVE"):
        # Unpack user_data (dict) into the parent constructor
        super().__init__(**user_data)
        
        self.student_id = student_id
        self.student_code = student_code  # Student Code (e.g., S001)
        self.major = major
        self.dept_id = dept_id
        self.academic_year = academic_year
        self.gpa = float(gpa) if gpa else 0.0
        self.academic_status = academic_status # ENUM: ACTIVE, ON_LEAVE, DROPPED, GRADUATED

    def to_dict(self):
        """Helper to convert object to dict for UI display"""
        return {
            "id": self.student_id,
            "code": self.student_code,
            "name": self.full_name,
            "email": self.email,
            "gpa": self.gpa,
            "status": self.academic_status
        }