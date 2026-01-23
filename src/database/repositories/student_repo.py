from database.repository import BaseRepository
from models.student import Student
from utils.cache import cache_result

class StudentRepository(BaseRepository):
    def get_all(self, page=1, per_page=50):
        """
        Server-side pagination that also returns the total count of items
        using SQL_CALC_FOUND_ROWS to avoid a separate COUNT(*) query.
        Returns a tuple: (list_of_students, total_count)
        """
        offset = (page - 1) * per_page
        sql = """
            SELECT SQL_CALC_FOUND_ROWS s.*, u.*, d.dept_name 
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
            LEFT JOIN Departments d ON s.dept_id = d.dept_id
            ORDER BY s.student_code ASC
            LIMIT %s OFFSET %s
        """
        total_count_sql = "SELECT FOUND_ROWS() as total"

        conn = None
        try:
            # Manually manage connection to ensure FOUND_ROWS() works on the same connection
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Execute the main query to get the page data
            cursor.execute(sql, (per_page, offset))
            results = cursor.fetchall()
            students = [Student.from_db_row(row) for row in results]

            # Execute the second query to get the total count
            cursor.execute(total_count_sql)
            total_count = cursor.fetchone()['total']

            # Return both data and total count
            return students, total_count
        except Exception as e:
            print(f"Error fetching paginated students: {e}")
            return [], 0 # Return empty result on error
        finally:
            if conn:
                conn.close() # This returns the connection to the pool
    
    def get_all_for_admin(self, page=1, per_page=50):
        """Optimized method for admin panel with pagination"""
        return self.get_all(page, per_page)

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
            user_sql = """ # 1. Insert User
                INSERT INTO Users (username, password, full_name, email, phone, role, status)
                VALUES (%s, %s, %s, %s, %s, 'Student', 'ACTIVE')
            """
            cursor.execute(user_sql, (
                student_obj.student_code, 
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
        conn = self.db.get_connection() # Get database connection
        cursor = conn.cursor()
        try:
            conn.start_transaction()

            # 1. Update User info (Added phone)
            user_sql = "UPDATE Users SET full_name=%s, email=%s, phone=%s WHERE user_id=%s"
            cursor.execute(user_sql, (student_obj.full_name, student_obj.email, student_obj.phone, student_obj.user_id))
            
            # 2. Update Student info (Added major, academic_year)
            stu_sql = "UPDATE Students SET dept_id=%s, academic_status=%s, major=%s, academic_year=%s WHERE student_id=%s"
            cursor.execute(stu_sql, (student_obj.dept_id, student_obj.academic_status, student_obj.major, student_obj.academic_year, student_obj.student_id))
            
            conn.commit()
            return True, "Student updated successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def delete(self, student_id):
        # Check grade constraints
        check_sql = "SELECT COUNT(*) as count FROM Grades WHERE student_id=%s"
        res = self.execute_query(check_sql, (student_id,), fetch_one=True)
        if res['count'] > 0:
            return False, "Cannot delete: Student has grade records."

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
        """Retrieve Student information based on User ID (Used after Login)"""
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
        """Only update contact information (FR-06)"""
        # Added dob to update
        sql = "UPDATE Users SET email=%s, phone=%s, address=%s, dob=%s WHERE user_id=%s"
        try:
            self.execute_query(sql, (student_obj.email, student_obj.phone, student_obj.address, student_obj.dob, student_obj.user_id))
            return True, "Profile updated successfully."
        except Exception as e:
            return False, str(e)

    def bulk_add(self, students_list, default_dept_id=1, default_year=2024):
        """
        students_list: List of dictionaries [{'code': 'S001', 'name': 'A', ...}]
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            count = 0
            for s in students_list: # Iterate through student data
                from utils.security import Security
                hashed_pw = Security.hash_password(s['code']) 
                
                cursor.execute(
                    "INSERT INTO Users (username, password, full_name, email, role, status) VALUES (%s, %s, %s, %s, 'Student', 'ACTIVE')",
                    (s['code'], hashed_pw, s['name'], s['email'])
                )
                user_id = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO Students (user_id, student_code, dept_id, major, academic_year, academic_status) VALUES (%s, %s, %s, %s, %s, 'ACTIVE')",
                    (user_id, s['code'], default_dept_id, s.get('major', 'General'), default_year)
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
