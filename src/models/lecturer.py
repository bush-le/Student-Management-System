from .user import User

class Lecturer(User):
    """
    Lecturer class inheriting from User.
    Maps to 'Lecturers' table.
    """
    def __init__(self, user_data, lecturer_id, lecturer_code, degree, dept_id):
        super().__init__(**user_data)
        
        self.lecturer_id = lecturer_id
        self.lecturer_code = lecturer_code # Lecturer Code (e.g., L102)
        self.degree = degree # Degree (e.g., Master, PhD...)
        self.dept_id = dept_id