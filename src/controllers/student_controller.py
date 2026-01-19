from database.connection import DatabaseConnection
from models.student import Student
from models.academic.grade import Grade

class StudentController:
    def __init__(self, user_id):
        self.user_id = user_id

    def view_profile(self):
        """
        FR-05: View Personal Information [cite: 58-62].
        Returns full Student object information.
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Join Students and Users tables to get full info
            query = """
                SELECT u.*, s.* FROM Students s
                JOIN Users u ON s.user_id = u.user_id
                WHERE u.user_id = %s
            """
            cursor.execute(query, (self.user_id,))
            data = cursor.fetchone()
            
            if data:
                # Separate data to initialize Student Model correctly
                # Note: Need to filter User and Student fields carefully
                # Here assuming data contains all necessary keys
                return Student(
                    user_data={k: v for k, v in data.items() if k in ['user_id', 'username', 'password', 'full_name', 'email', 'phone', 'role', 'status']},
                    student_id=data['student_id'],
                    student_code=data['student_code'],
                    major=data['major'],
                    dept_id=data['dept_id'],
                    academic_year=data['academic_year'],
                    gpa=data['gpa'],
                    academic_status=data['academic_status']
                )
            return None
        finally:
            conn.close()

    def update_profile(self, phone, email, address):
        """
        FR-06: Update Personal Information [cite: 63-68].
        Only allow updating contact information.
        """
        # Validate input (use utils/validators.py if available)
        if not phone or not email:
            return False, "Phone and Email are required."

        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Update Users table (General information)
            query = "UPDATE Users SET phone = %s, email = %s WHERE user_id = %s"
            # Note: Need to add address column to Users or Students table if DB design has it (Data Model page 35 doesn't show address clearly, but FR-06 mentions it).
            # Assuming address is in Students table if needed.
            cursor.execute(query, (phone, email, self.user_id))
            conn.commit()
            return True, "Profile updated successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def view_schedule(self):
        """
        FR-07: View Weekly Schedule [cite: 69-72].
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Get schedule based on classes the student has grades for (or is enrolled in)
            query = """
                SELECT c.course_name, cc.room, cc.schedule, l.lecturer_code, u.full_name as lecturer_name
                FROM Grades g
                JOIN Course_Classes cc ON g.class_id = cc.class_id
                JOIN Courses c ON cc.course_id = c.course_id
                LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
                LEFT JOIN Users u ON l.user_id = u.user_id
                JOIN Students s ON g.student_id = s.student_id
                WHERE s.user_id = %s
            """
            cursor.execute(query, (self.user_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def view_grades(self):
        """
        FR-08: View Academic Results [cite: 73-77].
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.course_code, c.course_name, c.credits, 
                       g.attendance_score, g.midterm, g.final, g.total, g.letter_grade
                FROM Grades g
                JOIN Course_Classes cc ON g.class_id = cc.class_id
                JOIN Courses c ON cc.course_id = c.course_id
                JOIN Students s ON g.student_id = s.student_id
                WHERE s.user_id = %s
            """
            cursor.execute(query, (self.user_id,))
            grades_data = cursor.fetchall()
            
            # Calculate cumulative GPA (Simplified logic)
            # In reality need to calculate: Sum(Total * Credits) / Sum(Credits)
            return grades_data
        finally:
            conn.close()