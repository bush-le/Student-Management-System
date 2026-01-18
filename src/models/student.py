from models.user import User

class Student(User):
    """
    Class representing a Student, inheriting from User.
    Maps to the 'Students' table in the database.
    """
    def __init__(self, user_id, username, password, fullname, email, phone, status,
                 student_id, student_code, major, dept_id, academic_year, gpa, academic_status):
        
        # Initialize parent User class attributes 
        super().__init__(user_id, username, password, fullname, email, phone, 'Student', status)
        
        # Specific Student attributes 
        self.student_id = student_id # Primary Key: integer
        self.student_code = student_code # varchar(20) 
        self.major = major # varchar(100) 
        self.dept_id = dept_id # Foreign Key to Departments 
        self.academic_year = academic_year # varchar(10) 
        self.gpa = gpa # decimal(3,2) 
        self.academic_status = academic_status # Enum: ACTIVE, ON LEAVE, etc.
