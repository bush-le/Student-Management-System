from database.repository import BaseRepository
from models.academic.course_class import CourseClass

class ClassRepository(BaseRepository):
    def get_all_details(self):
        sql = """
            SELECT cc.*, c.course_name, c.course_code, u.full_name as lecturer_name,
                   (SELECT COUNT(*) FROM Grades WHERE class_id = cc.class_id) as current_enrolled
            FROM Course_Classes cc
            JOIN Courses c ON cc.course_id = c.course_id
            LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
            LEFT JOIN Users u ON l.user_id = u.user_id
            ORDER BY c.course_name ASC
        """
        return [CourseClass.from_db_row(row) for row in self.execute_query(sql, fetch_all=True)]

    def get_all(self):
        return self.get_all_details()

    def get_by_id(self, class_id):
        sql = """
            SELECT cc.*, c.course_name, c.course_code, u.full_name as lecturer_name,
                   (SELECT COUNT(*) FROM Grades WHERE class_id = cc.class_id) as current_enrolled
            FROM Course_Classes cc
            JOIN Courses c ON cc.course_id = c.course_id
            LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
            LEFT JOIN Users u ON l.user_id = u.user_id
            WHERE cc.class_id = %s
        """
        row = self.execute_query(sql, (class_id,), fetch_one=True)
        return CourseClass.from_db_row(row) if row else None

    def add(self, cls_obj):
        try:
            self.execute_query("INSERT INTO Course_Classes (course_id, semester_id, room, schedule, max_capacity) VALUES (%s, %s, %s, %s, %s)",
                               (cls_obj.course_id, cls_obj.semester_id, cls_obj.room, cls_obj.schedule, cls_obj.max_capacity))
            return True, "Class scheduled"
        except Exception as e: return False, str(e)

    def update(self, cls_obj):
        try:
            self.execute_query("UPDATE Course_Classes SET room=%s, schedule=%s, max_capacity=%s WHERE class_id=%s",
                               (cls_obj.room, cls_obj.schedule, cls_obj.max_capacity, cls_obj.class_id))
            return True, "Class updated"
        except Exception as e: return False, str(e)
        
    def assign_lecturer(self, class_id, lecturer_id):
        try:
            self.execute_query("UPDATE Course_Classes SET lecturer_id=%s WHERE class_id=%s", (lecturer_id, class_id))
            return True, "Lecturer assigned"
        except Exception as e: return False, str(e)

    def delete(self, class_id):
        try:
            self.execute_query("DELETE FROM Course_Classes WHERE class_id=%s", (class_id,))
            return True, "Class deleted"
        except Exception as e: return False, "Cannot delete (Active grades)"

    def get_schedule_by_student(self, student_id):
        """Lấy lịch học của sinh viên dựa trên các lớp đã đăng ký (có trong bảng Grades)"""
        sql = """
            SELECT cc.schedule, cc.room, c.course_name, c.course_code, 
                   u.full_name as lecturer_name, l.lecturer_code
            FROM Grades g
            JOIN Course_Classes cc ON g.class_id = cc.class_id
            JOIN Courses c ON cc.course_id = c.course_id
            LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
            LEFT JOIN Users u ON l.user_id = u.user_id
            WHERE g.student_id = %s
        """
        # Trả về danh sách dictionary (vì đây là dữ liệu tổng hợp để hiển thị, chưa cần map sang Model phức tạp)
        return self.execute_query(sql, (student_id,), fetch_all=True)

    def count_all(self):
        try:
            result = self.execute_query("SELECT COUNT(*) as total FROM Classes", fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            print(f"Error counting classes: {e}")
            return 0