from .user import User

class Student(User):
    def __init__(self, user_data, student_id, student_code, major, dept_id, academic_year, gpa=0.0, academic_status="ACTIVE", dept_name=None):
        # Gọi init của lớp cha User
        # user_data là dict chứa: user_id, username, full_name, email...
        super().__init__(**user_data)
        
        self.student_id = student_id
        self.student_code = student_code
        self.major = major
        self.dept_id = dept_id
        self.academic_year = academic_year
        self.gpa = float(gpa) if gpa else 0.0
        self.academic_status = academic_status
        
        # Field mở rộng (không có trong bảng Students nhưng có khi join)
        self.dept_name = dept_name

    @classmethod
    def from_db_row(cls, row):
        """
        Factory method: Tạo đối tượng Student từ dòng dữ liệu DB (Dictionary).
        """
        if not row:
            return None
        
        # Tách dữ liệu thuộc về User (dựa trên tên cột trong bảng Users)
        user_keys = ['user_id', 'username', 'password', 'full_name', 'email', 'phone', 'role', 'status', 'address', 'dob']
        # Lọc lấy các key có tồn tại trong row
        user_data = {k: row.get(k) for k in user_keys if k in row}
        
        return cls(
            user_data=user_data,
            student_id=row.get('student_id'),
            student_code=row.get('student_code'),
            major=row.get('major'),
            dept_id=row.get('dept_id'),
            academic_year=row.get('academic_year'),
            gpa=row.get('gpa'),
            academic_status=row.get('academic_status'),
            dept_name=row.get('dept_name') # Lấy từ bảng Departments khi join
        )