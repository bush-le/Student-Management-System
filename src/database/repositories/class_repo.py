from database.repository import BaseRepository
from models.academic.course_class import CourseClass

class ClassRepository(BaseRepository):
    def get_all_details(self, page=None, per_page=None, search_query=None):
        sql = """
            SELECT SQL_CALC_FOUND_ROWS cc.*, c.course_name, c.course_code, u.full_name as lecturer_name,
                   (SELECT COUNT(*) FROM Grades WHERE class_id = cc.class_id) as current_enrolled
            FROM Course_Classes cc
            JOIN Courses c ON cc.course_id = c.course_id
            LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
            LEFT JOIN Users u ON l.user_id = u.user_id
        """
        params = []
        if search_query:
            sql += " WHERE (c.course_name LIKE %s OR c.course_code LIKE %s OR u.full_name LIKE %s) "
            term = f"%{search_query}%"
            params.extend([term, term, term])
            
        sql += " ORDER BY c.course_name ASC"

        if page is not None and per_page is not None:
            offset = (page - 1) * per_page
            sql += " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            cursor.execute("SELECT FOUND_ROWS() as total")
            total = cursor.fetchone()['total']
            return [CourseClass.from_db_row(row) for row in rows], total
        finally:
            conn.close()

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

    def get_schedule_by_lecturer(self, lecturer_id):
        """Retrieves lecturer's teaching schedule"""
        sql = """
            SELECT cc.*, c.course_name, c.course_code, s.name as semester_name, s.status as semester_status, s.end_date as semester_end_date,
                   (SELECT COUNT(*) FROM Grades WHERE class_id = cc.class_id) as enrolled_count
            FROM Course_Classes cc
            JOIN Courses c ON cc.course_id = c.course_id
            JOIN Semesters s ON cc.semester_id = s.semester_id
            WHERE cc.lecturer_id = %s
            ORDER BY cc.schedule # Order by schedule
        """
        return self.execute_query(sql, (lecturer_id,), fetch_all=True)

    def get_schedule_by_student(self, student_id):
        """Retrieves student's schedule based on registered classes (in Grades table)"""
        sql = """
            SELECT cc.schedule, cc.room, c.course_name, c.course_code, 
                   u.full_name as lecturer_name, l.lecturer_code
            FROM Grades g
            JOIN Course_Classes cc ON g.class_id = cc.class_id
            JOIN Courses c ON cc.course_id = c.course_id
            LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
            LEFT JOIN Users u ON l.user_id = u.user_id
            WHERE g.student_id = %s
        """ # SQL query to get student's schedule
        # Returns a list of dictionaries (as this is aggregated data for display, no need to map to complex Models yet)
        return self.execute_query(sql, (student_id,), fetch_all=True)

    def count_all(self):
        try:
            result = self.execute_query("SELECT COUNT(*) as total FROM Course_Classes", fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            print(f"Error counting classes: {e}")
            return 0