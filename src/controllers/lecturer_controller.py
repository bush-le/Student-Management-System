from database.connection import DatabaseConnection
from models.academic.grade import Grade

class LecturerController:
    def __init__(self, user_id):
        self.user_id = user_id
        # Helper: Get lecturer_id from logged-in user_id
        self.lecturer_id = self._fetch_lecturer_id()

    def _fetch_lecturer_id(self):
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT lecturer_id FROM Lecturers WHERE user_id = %s", (self.user_id,))
            res = cursor.fetchone()
            return res[0] if res else None
        finally:
            conn.close()

    def get_teaching_schedule(self):
        """FR-10: View Assigned Schedule [cite: 86-90]"""
        if not self.lecturer_id: return []
        
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT cc.class_id, c.course_name, cc.schedule, cc.room, cc.max_capacity,
                       (SELECT COUNT(*) FROM Grades g WHERE g.class_id = cc.class_id) as enrolled_count
                FROM Course_Classes cc
                JOIN Courses c ON cc.course_id = c.course_id
                WHERE cc.lecturer_id = %s
            """
            cursor.execute(query, (self.lecturer_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_class_student_list(self, class_id):
        """FR-11: View Student List [cite: 91-94]"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT s.student_id, s.student_code, u.full_name, 
                       g.attendance_score, g.midterm, g.final, g.total, g.grade_id, g.is_locked
                FROM Grades g
                JOIN Students s ON g.student_id = s.student_id
                JOIN Users u ON s.user_id = u.user_id
                WHERE g.class_id = %s
                ORDER BY s.student_code ASC
            """
            cursor.execute(query, (class_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def input_grade(self, student_id, class_id, attendance, midterm, final):
        """
        FR-12 & FR-13: Enter/Update Grades [cite: 95-107].
        Use Grade Model for calculations.
        """
        # 1. Calculate total score and letter grade
        grade_obj = Grade(None, student_id, class_id, attendance, midterm, final)
        total = grade_obj.calculate_total()
        letter = grade_obj.letter_grade

        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            
            # 2. Check grade lock status (FR-12) [cite: 102]
            check_sql = "SELECT is_locked FROM Grades WHERE student_id = %s AND class_id = %s"
            cursor.execute(check_sql, (student_id, class_id))
            row = cursor.fetchone()
            
            if row and row[0] == 1: # True
                return False, "This grade record is locked and cannot be edited."

            # 3. Update database
            update_sql = """
                UPDATE Grades 
                SET attendance_score=%s, midterm=%s, final=%s, total=%s, letter_grade=%s, updated_at=NOW()
                WHERE student_id=%s AND class_id=%s
            """
            cursor.execute(update_sql, (attendance, midterm, final, total, letter, student_id, class_id))
            conn.commit()
            return True, "Grade saved successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()