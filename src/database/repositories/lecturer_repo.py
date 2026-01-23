from database.repository import BaseRepository
from models.lecturer import Lecturer

class LecturerRepository(BaseRepository):
    def get_all(self, page=None, per_page=None):
        """Get lecturers (optional pagination)"""
        sql = """
            SELECT l.*, u.*, d.dept_name 
            FROM Lecturers l
            JOIN Users u ON l.user_id = u.user_id
            LEFT JOIN Departments d ON l.dept_id = d.dept_id
            ORDER BY l.lecturer_code ASC
        """
        params = ()
        if page is not None and per_page is not None:
            offset = (page - 1) * per_page
            sql += " LIMIT %s OFFSET %s"
            params = (per_page, offset)
            
        results = self.execute_query(sql, params, fetch_all=True)
        return [Lecturer.from_db_row(row) for row in results]

    def get_by_id(self, lecturer_id):
        sql = "SELECT l.*, u.*, d.dept_name FROM Lecturers l JOIN Users u ON l.user_id = u.user_id LEFT JOIN Departments d ON l.dept_id = d.dept_id WHERE l.lecturer_id = %s"
        row = self.execute_query(sql, (lecturer_id,), fetch_one=True)
        return Lecturer.from_db_row(row)

    def add(self, lecturer, password_hash):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            # 1. Insert User
            cursor.execute("INSERT INTO Users (username, password, full_name, email, phone, role, status) VALUES (%s, %s, %s, %s, %s, 'Lecturer', 'ACTIVE')",
                           (lecturer.lecturer_code, password_hash, lecturer.full_name, lecturer.email, lecturer.phone))
            user_id = cursor.lastrowid
            # 2. Insert Lecturer
            cursor.execute("INSERT INTO Lecturers (user_id, lecturer_code, dept_id, degree) VALUES (%s, %s, %s, %s)",
                           (user_id, lecturer.lecturer_code, lecturer.dept_id, lecturer.degree))
            conn.commit()
            return True, "Lecturer created successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def update(self, lecturer):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            cursor.execute("UPDATE Users SET full_name=%s, email=%s, phone=%s WHERE user_id=%s",
                           (lecturer.full_name, lecturer.email, lecturer.phone, lecturer.user_id))
            cursor.execute("UPDATE Lecturers SET dept_id=%s, degree=%s WHERE lecturer_id=%s",
                           (lecturer.dept_id, lecturer.degree, lecturer.lecturer_id))
            conn.commit()
            return True, "Lecturer updated successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, lecturer_id):
        res = self.execute_query("SELECT COUNT(*) as count FROM Course_Classes WHERE lecturer_id=%s", (lecturer_id,), fetch_one=True)
        if res['count'] > 0: return False, "Cannot delete: Lecturer assigned to classes."
        
        lec = self.get_by_id(lecturer_id)
        if not lec: return False, "Lecturer not found"
        
        try:
            self.execute_query("DELETE FROM Users WHERE user_id = %s", (lec.user_id,))
            return True, "Lecturer deleted"
        except Exception as e:
            return False, str(e)

    def get_by_user_id(self, user_id):
        """Retrieve full Lecturer information from User ID"""
        sql = """
            SELECT l.*, u.*, d.dept_name 
            FROM Lecturers l
            JOIN Users u ON l.user_id = u.user_id
            LEFT JOIN Departments d ON l.dept_id = d.dept_id
            WHERE u.user_id = %s
        """
        row = self.execute_query(sql, (user_id,), fetch_one=True)
        return Lecturer.from_db_row(row) if row else None

    def get_schedule_by_lecturer(self, lecturer_id):
        """Get list of classes assigned to lecturer"""
        sql = """
            SELECT cc.*, c.course_name, c.course_code,
                   (SELECT COUNT(*) FROM Grades WHERE class_id = cc.class_id) as enrolled_count
            FROM Course_Classes cc
            JOIN Courses c ON cc.course_id = c.course_id
            WHERE cc.lecturer_id = %s
        """
        # Return list of dicts for easy display in table
        return self.execute_query(sql, (lecturer_id,), fetch_all=True)

    def count_all(self):
        try: # Count users with 'Lecturer' role
            result = self.execute_query("SELECT COUNT(*) as total FROM Users WHERE role = 'Lecturer'", fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            print(f"Error counting lecturers: {e}")
            return 0