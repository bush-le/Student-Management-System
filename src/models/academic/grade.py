class Grade:
    def __init__(self, grade_id, student_id, class_id, attendance_score, midterm, final, total, letter_grade, is_locked=False):
        self.grade_id = grade_id
        self.student_id = student_id
        self.class_id = class_id
        self.attendance_score = attendance_score
        self.midterm = midterm
        self.final = final
        self.total = total
        self.letter_grade = letter_grade
        self.is_locked = bool(is_locked)

        # Fields mở rộng (khi join)
        self.course_name = None
        self.credits = 0

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        obj = cls(
            grade_id=row.get('grade_id'),
            student_id=row.get('student_id'),
            class_id=row.get('class_id'),
            attendance_score=row.get('attendance_score'),
            midterm=row.get('midterm'),
            final=row.get('final'),
            total=row.get('total'),
            letter_grade=row.get('letter_grade'),
            is_locked=row.get('is_locked', 0)
        )
        # Map thêm thông tin môn học nếu có
        obj.course_name = row.get('course_name')
        obj.credits = row.get('credits', 0)
        return obj

    def calculate_total(self):
        """Tính toán điểm tổng kết dựa trên trọng số"""
        # Giả sử: Chuyên cần 10%, Giữa kỳ 30%, Cuối kỳ 60%
        # Bạn có thể thay đổi tỷ lệ này tùy quy định
        att = self.attendance_score or 0
        mid = self.midterm or 0
        fin = self.final or 0
        
        self.total = round((att * 0.1) + (mid * 0.3) + (fin * 0.6), 2)
        self.letter_grade = self._convert_to_letter(self.total)
        return self.total

    def _convert_to_letter(self, score):
        if score >= 8.5: return "A"
        elif score >= 7.0: return "B"
        elif score >= 5.5: return "C"
        elif score >= 4.0: return "D"
        else: return "F"