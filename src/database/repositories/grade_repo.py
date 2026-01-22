from database.repository import BaseRepository
from models.academic.grade import Grade

class GradeRepository(BaseRepository):
    def get_by_student(self, student_id):
        """Lấy bảng điểm của 1 sinh viên (kèm thông tin môn học)"""
        sql = """
            SELECT g.*, c.course_name, c.credits
            FROM Grades g
            JOIN Course_Classes cc ON g.class_id = cc.class_id
            JOIN Courses c ON cc.course_id = c.course_id
            WHERE g.student_id = %s
        """
        results = self.execute_query(sql, (student_id,), fetch_all=True)
        return [Grade.from_db_row(r) for r in results]

    def get_by_class(self, class_id):
        """Lấy bảng điểm của 1 lớp (cho Giảng viên nhập điểm)"""
        sql = """
            SELECT g.*, s.student_code, u.full_name 
            FROM Grades g
            JOIN Students s ON g.student_id = s.student_id
            JOIN Users u ON s.user_id = u.user_id
            WHERE g.class_id = %s
            ORDER BY s.student_code ASC
        """
        # Lưu ý: Model Grade hiện tại chưa có field student_name/code. 
        # Bạn có thể mở rộng Model Grade hoặc trả về dict nếu chỉ để hiển thị UI
        # Ở đây ta trả về list dict cho đơn giản với UI nhập điểm
        return self.execute_query(sql, (class_id,), fetch_all=True)

    def update_scores(self, grade_obj):
        """Cập nhật điểm số"""
        # Kiểm tra khóa điểm
        check = self.execute_query("SELECT is_locked FROM Grades WHERE grade_id=%s", (grade_obj.grade_id,), fetch_one=True)
        if check and check['is_locked']:
            return False, "Grades are locked."

        # Tự động tính toán lại total và letter trước khi lưu
        grade_obj.calculate_total()

        sql = """
            UPDATE Grades 
            SET attendance_score=%s, midterm=%s, final=%s, total=%s, letter_grade=%s
            WHERE grade_id=%s
        """
        try:
            self.execute_query(sql, (
                grade_obj.attendance_score, 
                grade_obj.midterm, 
                grade_obj.final, 
                grade_obj.total, 
                grade_obj.letter_grade, 
                grade_obj.grade_id
            ))
            return True, "Saved"
        except Exception as e: return False, str(e)

    def lock_grades(self, class_id):
        """Khóa điểm toàn bộ lớp"""
        try:
            self.execute_query("UPDATE Grades SET is_locked=1 WHERE class_id=%s", (class_id,))
            return True, "Grades locked"
        except Exception as e: return False, str(e)
        
    def get_id_by_enrollment(self, student_id, class_id):
        """Lấy grade_id dựa trên sinh viên và lớp học"""
        sql = "SELECT grade_id FROM Grades WHERE student_id = %s AND class_id = %s"
        res = self.execute_query(sql, (student_id, class_id), fetch_one=True)
        return res['grade_id'] if res else None

    # Các method bắt buộc của BaseRepo (nếu không dùng thì để pass hoặc raise)
    def get_all(self): pass

    def get_by_id(self, grade_id):
        sql = "SELECT * FROM Grades WHERE grade_id = %s"
        row = self.execute_query(sql, (grade_id,), fetch_one=True)
        return Grade.from_db_row(row) if row else None

    def add(self, entity): pass 
    def update(self, entity): pass
    def delete(self, id): pass