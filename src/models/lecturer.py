from .user import User

class Lecturer(User):
    def __init__(self, user_data, lecturer_id, lecturer_code, dept_id, degree, dept_name=None):
        super().__init__(**user_data)
        self.lecturer_id = lecturer_id
        self.lecturer_code = lecturer_code
        self.dept_id = dept_id
        self.degree = degree
        self.dept_name = dept_name

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        user_keys = ['user_id', 'username', 'password', 'full_name', 'email', 'phone', 'role', 'status']
        user_data = {k: row.get(k) for k in user_keys if k in row}
        
        return cls(
            user_data=user_data,
            lecturer_id=row.get('lecturer_id'),
            lecturer_code=row.get('lecturer_code'),
            dept_id=row.get('dept_id'),
            degree=row.get('degree'),
            dept_name=row.get('dept_name')
        )