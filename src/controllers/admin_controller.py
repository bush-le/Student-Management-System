from database.connection import DatabaseConnection
from utils.security import Security
# Assuming you have validators. If not, you can skip this line and check manually with if/else
from utils.validators import validate_email, validate_phone 

class AdminController:
    """
    Controller handling all business logic for Administrator (Academic Affairs Officer).
    Includes: Semesters, Courses, Classes, Students, Lecturers, Announcements.
    """

    # =========================================================================
    # 1. SEMESTER MANAGEMENT (FR-14 / UC14) [cite: 111-114, 603-605]
    # =========================================================================
    def create_semester(self, name, start_date, end_date):
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Default status is 'OPEN' when created
            sql = "INSERT INTO Semesters (name, start_date, end_date, status) VALUES (%s, %s, %s, 'OPEN')"
            cursor.execute(sql, (name, start_date, end_date))
            conn.commit()
            return True, "Semester created successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def update_semester_status(self, semester_id, status):
        """Open/Close semester. When closing, grade locking logic might be needed (FR-14)"""
        if status not in ['OPEN', 'CLOSED']:
            return False, "Invalid status."
            
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = "UPDATE Semesters SET status = %s WHERE semester_id = %s"
            cursor.execute(sql, (status, semester_id))
            conn.commit()
            return True, f"Semester status updated to {status}."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 2. COURSE MANAGEMENT (FR-15 / UC17) [cite: 115-118, 667-681]
    # =========================================================================
    def create_course(self, code, name, credits, dept_id, description, prerequisite_id=None):
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
                INSERT INTO Courses (course_code, course_name, credits, dept_id, description, prerequisite_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (code, name, credits, dept_id, description, prerequisite_id))
            conn.commit()
            return True, "Course created successfully."
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()

    def delete_course(self, course_id):
        """Note: Need to handle foreign key constraints (Classes, Grades) before deletion"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM Courses WHERE course_id = %s"
            cursor.execute(sql, (course_id,))
            conn.commit()
            return True, "Course deleted successfully."
        except Exception as e:
            return False, "Cannot delete course. It may be assigned to classes."
        finally:
            conn.close()

    # =========================================================================
    # 3. CLASS SECTION MANAGEMENT (FR-16 / UC18) [cite: 119-123, 691-703]
    # =========================================================================
    def create_class(self, course_id, semester_id, room, schedule, capacity):
        """Create a new class section for a semester"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Can add room/schedule conflict check logic here (FR-16 check logic)
            sql = """
                INSERT INTO Course_Classes (course_id, semester_id, room, schedule, max_capacity)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (course_id, semester_id, room, schedule, capacity))
            conn.commit()
            return True, "Class created successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 4. LECTURER ASSIGNMENT (FR-17 / UC19) [cite: 124-128, 712-724]
    # =========================================================================
    def assign_lecturer(self, class_id, lecturer_id):
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            
            # (Optional) Check for lecturer schedule conflict before assignment [cite: 127]
            # check_schedule_conflict(lecturer_id, new_schedule) -> This logic is complex, implement later.

            sql = "UPDATE Course_Classes SET lecturer_id = %s WHERE class_id = %s"
            cursor.execute(sql, (lecturer_id, class_id))
            conn.commit()
            return True, "Lecturer assigned successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 5. STUDENT MANAGEMENT (FR-18 / UC15) [cite: 129-135, 624-635]
    # =========================================================================
    def create_student(self, username, password, full_name, email, phone, student_code, dept_id, major, year):
        """
        Create new User -> Get User ID -> Create new Student.
        Use Transaction to ensure integrity.
        """
        conn = DatabaseConnection.get_connection()
        try:
            conn.start_transaction()
            cursor = conn.cursor()

            # 1. Create User
            hashed_pw = Security.hash_password(password)
            user_sql = """
                INSERT INTO Users (username, password, full_name, email, phone, role, status)
                VALUES (%s, %s, %s, %s, %s, 'Student', 'ACTIVE')
            """
            cursor.execute(user_sql, (username, hashed_pw, full_name, email, phone))
            user_id = cursor.lastrowid

            # 2. Create Student Profile
            student_sql = """
                INSERT INTO Students (user_id, student_code, dept_id, major, academic_year, academic_status)
                VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
            """
            cursor.execute(student_sql, (user_id, student_code, dept_id, major, year))

            conn.commit()
            return True, "Student account created."
        except Exception as e:
            conn.rollback()
            return False, f"Failed to create student: {str(e)}"
        finally:
            conn.close()

    def update_student_status(self, student_id, new_status):
        """Update status: Active, On Leave, Dropped, Graduated [cite: 133]"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = "UPDATE Students SET academic_status = %s WHERE student_id = %s"
            cursor.execute(sql, (new_status, student_id))
            conn.commit()
            return True, "Student status updated."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 6. LECTURER MANAGEMENT (FR-19 / UC16) [cite: 136-141, 645-657]
    # =========================================================================
    def create_lecturer(self, username, password, full_name, email, phone, lecturer_code, degree, dept_id):
        """Similar to create_student, uses Transaction"""
        conn = DatabaseConnection.get_connection()
        try:
            conn.start_transaction()
            cursor = conn.cursor()

            # 1. Create User
            hashed_pw = Security.hash_password(password)
            user_sql = """
                INSERT INTO Users (username, password, full_name, email, phone, role, status)
                VALUES (%s, %s, %s, %s, %s, 'Lecturer', 'ACTIVE')
            """
            cursor.execute(user_sql, (username, hashed_pw, full_name, email, phone))
            user_id = cursor.lastrowid

            # 2. Create Lecturer Profile
            lecturer_sql = """
                INSERT INTO Lecturers (user_id, lecturer_code, degree, dept_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(lecturer_sql, (user_id, lecturer_code, degree, dept_id))

            conn.commit()
            return True, "Lecturer account created."
        except Exception as e:
            conn.rollback()
            return False, f"Failed: {str(e)}"
        finally:
            conn.close()

    def delete_lecturer(self, lecturer_id):
        """
        FR-19: Prevent deleting lecturers currently assigned to classes.
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            
            # 1. Check constraints
            check_sql = "SELECT COUNT(*) FROM Course_Classes WHERE lecturer_id = %s"
            cursor.execute(check_sql, (lecturer_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                return False, "Cannot delete lecturer assigned to active classes."

            # 2. Delete (In reality, should use Soft Delete or set status=LOCKED)
            # Here deleting Lecturer profile, parent User kept or deleted depending on policy
            # Assuming deleting User as well:
            # Get user_id first
            cursor.execute("SELECT user_id FROM Lecturers WHERE lecturer_id=%s", (lecturer_id,))
            user_id = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM Lecturers WHERE lecturer_id = %s", (lecturer_id,))
            cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
            
            conn.commit()
            return True, "Lecturer deleted."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 7. ANNOUNCEMENT MANAGEMENT (FR-20 / UC20) [cite: 142-146, 734-745]
    # =========================================================================
    def create_announcement(self, title, content, officer_id):
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO Announcements (title, content, officer_id, created_date) VALUES (%s, %s, %s, NOW())"
            cursor.execute(sql, (title, content, officer_id))
            conn.commit()
            return True, "Announcement posted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_all_announcements(self):
        """Get list of announcements for management"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM Announcements ORDER BY created_date DESC"
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()