class Grade:
    def __init__(self, grade_id, student_id, class_id, attendance_score, midterm, final, total=0, letter_grade="", **kwargs):
        self.grade_id = grade_id
        self.student_id = student_id
        self.class_id = class_id
        self.attendance_score = float(attendance_score or 0)
        self.midterm = float(midterm or 0)
        self.final = float(final or 0)
        self.total = total
        self.letter_grade = letter_grade
        
        # Hỗ trợ các thuộc tính mở rộng từ câu lệnh JOIN (ví dụ: course_name, credits)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_db_row(cls, row):
        if not row:
            return None
        
        # Tách các trường chuẩn của Grade
        init_args = {
            'grade_id': row.get('grade_id'),
            'student_id': row.get('student_id'),
            'class_id': row.get('class_id'),
            'attendance_score': row.get('attendance_score'),
            'midterm': row.get('midterm'),
            'final': row.get('final'),
            'total': row.get('total'),
            'letter_grade': row.get('letter_grade')
        }
        
        # Các trường còn lại (như course_name) sẽ được truyền vào kwargs
        kwargs = {k: v for k, v in row.items() if k not in init_args}
        
        return cls(**init_args, **kwargs)

    def calculate_total(self):
        """Tính điểm tổng kết theo trọng số: 10% CC, 40% GK, 50% CK"""
        self.total = (self.attendance_score * 0.1) + (self.midterm * 0.4) + (self.final * 0.5)
        self.total = round(self.total, 1) # Làm tròn 1 chữ số
        
        # Mapping Letter Grade
        if self.total >= 8.5: self.letter_grade = 'A'
        elif self.total >= 7.0: self.letter_grade = 'B'
        elif self.total >= 5.5: self.letter_grade = 'C'
        elif self.total >= 4.0: self.letter_grade = 'D'
        else: self.letter_grade = 'F'