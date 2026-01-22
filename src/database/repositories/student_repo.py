from database.repository import BaseRepository
from models.student import Student

class StudentRepository(BaseRepository):
    def get_all(self):
        # Join bảng để lấy đầy đủ thông tin: User info + Student info + Dept Name
        sql = """
            SELECT s.*, u.*, d.dept_name 
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
            LEFT JOIN Departments d ON s.dept_id = d.dept_id
            ORDER BY s.student_code ASC
        """
        results = self.execute_query(sql, fetch_all=True)
        # Convert list of dicts -> list of Student objects
        return [Student.from_db_row(row) for row in results]

    def get_by_id(self, student_id):
        sql = """
            SELECT s.*, u.*, d.dept_name 
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
            LEFT JOIN Departments d ON s.dept_id = d.dept_id
            WHERE s.student_id = %s
        """
        row = self.execute_query(sql, (student_id,), fetch_one=True)
        return Student.from_db_row(row)

    def add(self, student_obj, password_hash):
        """
        Transaction: Insert User -> Lấy ID -> Insert Student
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            
            # 1. Insert User
            user_sql = """
                INSERT INTO Users (username, password, full_name, email, phone, role, status)
                VALUES (%s, %s, %s, %s, %s, 'Student', 'ACTIVE')
            """
            cursor.execute(user_sql, (
                student_obj.student_code, # Username mặc định là mã SV
                password_hash, 
                student_obj.full_name, 
                student_obj.email, 
                student_obj.phone
            ))
            user_id = cursor.lastrowid

            # 2. Insert Student
            student_sql = """
                INSERT INTO Students (user_id, student_code, dept_id, major, academic_year, academic_status)
                VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
            """
            cursor.execute(student_sql, (
                user_id, 
                student_obj.student_code, 
                student_obj.dept_id, 
                student_obj.major, 
                student_obj.academic_year
            ))
            
            conn.commit()
            return True, "Student created successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def update(self, student_obj):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()

            # 1. Update User info
            user_sql = "UPDATE Users SET full_name=%s, email=%s WHERE user_id=%s"
            cursor.execute(user_sql, (student_obj.full_name, student_obj.email, student_obj.user_id))
            
            # 2. Update Student info
            stu_sql = "UPDATE Students SET dept_id=%s, academic_status=%s WHERE student_id=%s"
            cursor.execute(stu_sql, (student_obj.dept_id, student_obj.academic_status, student_obj.student_id))
            
            conn.commit()
            return True, "Student updated successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def delete(self, student_id):
        # Kiểm tra ràng buộc điểm số
        check_sql = "SELECT COUNT(*) as count FROM Grades WHERE student_id=%s"
        res = self.execute_query(check_sql, (student_id,), fetch_one=True)
        if res['count'] > 0:
            return False, "Cannot delete: Student has grade records."

        # Lấy thông tin student để xóa User (Cascade sẽ xóa Student)
        student = self.get_by_id(student_id)
        if not student: 
            return False, "Student not found"

        sql = "DELETE FROM Users WHERE user_id = %s"
        try:
            self.execute_query(sql, (student.user_id,))
            return True, "Student deleted successfully"
        except Exception as e:
            return False, str(e)

    def get_by_user_id(self, user_id):
        """Lấy thông tin Student dựa trên User ID (Dùng khi Login xong)"""
        sql = """
            SELECT s.*, u.*, d.dept_name 
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
            LEFT JOIN Departments d ON s.dept_id = d.dept_id
            WHERE u.user_id = %s
        """
        row = self.execute_query(sql, (user_id,), fetch_one=True)
        return Student.from_db_row(row) if row else None
    
    def update_contact_info(self, student_obj):
        """Chỉ cập nhật thông tin liên lạc (FR-06)"""
        sql = "UPDATE Users SET email=%s, phone=%s, address=%s WHERE user_id=%s"
        try:
            self.execute_query(sql, (student_obj.email, student_obj.phone, student_obj.address, student_obj.user_id))
            return True, "Profile updated successfully."
        except Exception as e:
            return False, str(e)

    def bulk_add(self, students_list):
        """
        students_list: List of dictionaries [{'code': 'S001', 'name': 'A', ...}]
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            count = 0
            for s in students_list:
                # 1. Tạo User
                # Password mặc định là ID sinh viên
                from utils.security import Security
                hashed_pw = Security.hash_password(s['code']) 
                
                cursor.execute(
                    "INSERT INTO Users (username, password, full_name, email, role, status) VALUES (%s, %s, %s, %s, 'Student', 'ACTIVE')",
                    (s['code'], hashed_pw, s['name'], s['email'])
                )
                user_id = cursor.lastrowid
                
                # 2. Tạo Student
                # Giả định dept_id = 1 mặc định nếu CSV không có
                cursor.execute(
                    "INSERT INTO Students (user_id, student_code, dept_id, major, academic_year, academic_status) VALUES (%s, %s, %s, %s, %s, 'ACTIVE')",
                    (user_id, s['code'], 1, s.get('major', 'General'), 2024)
                )
                count += 1
            
            conn.commit()
            return True, f"Successfully imported {count} students."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def count_all(self):
        try:
            result = self.execute_query("SELECT COUNT(*) as total FROM Students", fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            print(f"Error counting students: {e}")
            return 0