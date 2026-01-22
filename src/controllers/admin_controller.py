from database.connection import DatabaseConnection
from utils.security import Security
# Assuming you have validators. If not, you can skip this line and check manually with if/else
from utils.validators import validate_email, validate_phone 

class AdminController:
    """
    Controller handling all business logic for Administrator (Academic Affairs Officer).
    Includes: Semesters, Courses, Classes, Students, Lecturers, Announcements.
    """

    def __init__(self, user_id):
        self.user_id = user_id

    def get_dashboard_stats(self):
        """Lấy số liệu thống kê cho Dashboard"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM Students")
            stats['students'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Lecturers")
            stats['lecturers'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Courses")
            stats['courses'] = cursor.fetchone()[0]
            return stats
        except:
            return {'students': 0, 'lecturers': 0, 'courses': 0}
        finally:
            conn.close()

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

    def get_all_semesters(self):
        """Lấy danh sách tất cả học kỳ"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Semesters ORDER BY start_date DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching semesters: {e}")
            return []
        finally:
            conn.close()

    def update_semester(self, semester_id, name, start_date, end_date, status):
        """Cập nhật thông tin học kỳ"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Nếu status là OPEN, có thể cần logic để đóng các kỳ khác (tùy nghiệp vụ)
            # Ở đây ta update đơn thuần
            sql = """
                UPDATE Semesters 
                SET name=%s, start_date=%s, end_date=%s, status=%s 
                WHERE semester_id=%s
            """
            cursor.execute(sql, (name, start_date, end_date, status, semester_id))
            conn.commit()
            return True, "Semester updated successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_semester(self, semester_id):
        """Xóa học kỳ (Hoặc Archive)"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Kiểm tra ràng buộc khóa ngoại (Lớp học, Điểm số...)
            check_sql = "SELECT COUNT(*) FROM Course_Classes WHERE semester_id = %s"
            cursor.execute(check_sql, (semester_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Cannot delete: Classes exist in this semester."
            
            cursor.execute("DELETE FROM Semesters WHERE semester_id = %s", (semester_id,))
            conn.commit()
            return True, "Semester deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 2. COURSE MANAGEMENT (FR-15 / UC17) [cite: 115-118, 667-681]
    # =========================================================================
    def get_all_courses(self):
        """Lấy danh sách khóa học"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Giả sử bảng Courses đã được cập nhật thêm cột course_type
            # Nếu chưa có, bạn cần ALTER TABLE Courses ADD COLUMN course_type VARCHAR(20) DEFAULT 'Core';
            # Và ALTER TABLE Courses ADD COLUMN prerequisites_str TEXT;
            sql = "SELECT * FROM Courses ORDER BY course_code ASC"
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    def create_course(self, code, name, credits, type_c, desc, prereq):
        """Tạo khóa học mới"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Kiểm tra trùng mã
            cursor.execute("SELECT COUNT(*) FROM Courses WHERE course_code = %s", (code,))
            if cursor.fetchone()[0] > 0:
                return False, f"Course code '{code}' already exists."

            # Insert (Lưu ý: Bạn cần đảm bảo DB có các cột tương ứng)
            sql = """
                INSERT INTO Courses (course_code, course_name, credits, course_type, description, prerequisites_str)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (code, name, credits, type_c, desc, prereq))
            conn.commit()
            return True, "Course created successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def update_course(self, course_id, code, name, credits, type_c, desc, prereq):
        """Cập nhật khóa học"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
                UPDATE Courses 
                SET course_code=%s, course_name=%s, credits=%s, course_type=%s, description=%s, prerequisites_str=%s
                WHERE course_id=%s
            """
            cursor.execute(sql, (code, name, credits, type_c, desc, prereq, course_id))
            conn.commit()
            return True, "Course updated successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_course(self, course_id):
        """Xóa khóa học (Check ràng buộc lớp học)"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Check dependency
            cursor.execute("SELECT COUNT(*) FROM Course_Classes WHERE course_id = %s", (course_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Cannot delete: Active classes exist for this course."
            
            cursor.execute("DELETE FROM Courses WHERE course_id = %s", (course_id,))
            conn.commit()
            return True, "Course deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # =========================================================================
    # 3. CLASS SECTION MANAGEMENT (FR-16 / UC18) [cite: 119-123, 691-703]
    # =========================================================================
    def get_all_classes_details(self):
        """Lấy danh sách lớp kèm tên môn và tên giảng viên"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT cc.class_id, cc.room, cc.schedule, cc.max_capacity,
                       c.course_name, c.course_code, cc.course_id,
                       u.full_name as lecturer_name, cc.lecturer_id,
                       (SELECT COUNT(*) FROM Grades WHERE class_id = cc.class_id) as current_enrolled
                FROM Course_Classes cc
                JOIN Courses c ON cc.course_id = c.course_id
                LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
                LEFT JOIN Users u ON l.user_id = u.user_id
                ORDER BY c.course_name ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    def create_class(self, course_id, semester_name, room, schedule, capacity):
        """Tạo lớp học mới (Lưu ý: Semester ID đang giả lập hoặc cần query từ name)"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            # Giả sử lấy semester_id mới nhất hoặc từ dropdown (để đơn giản ta fix cứng hoặc query)
            # Thực tế: SELECT semester_id FROM Semesters WHERE name = %s
            semester_id = 1 
            
            sql = """
                INSERT INTO Course_Classes (course_id, semester_id, room, schedule, max_capacity)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (course_id, semester_id, room, schedule, capacity))
            conn.commit()
            return True, "Class scheduled successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def update_class(self, class_id, room, schedule, capacity):
        """Cập nhật thông tin cơ bản của lớp"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = "UPDATE Course_Classes SET room=%s, schedule=%s, max_capacity=%s WHERE class_id=%s"
            cursor.execute(sql, (room, schedule, capacity, class_id))
            conn.commit()
            return True, "Class updated."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_class(self, class_id):
        """Xóa lớp học"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Course_Classes WHERE class_id=%s", (class_id,))
            conn.commit()
            return True, "Class deleted."
        except Exception as e:
            return False, "Cannot delete class (active grades/students)."
        finally:
            conn.close()

    def assign_lecturer_to_class(self, class_id, lecturer_id):
        """Gán giảng viên cho lớp"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            
            # TODO: Add logic "Check for schedule conflicts" here as per requirement
            
            sql = "UPDATE Course_Classes SET lecturer_id=%s WHERE class_id=%s"
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

    def get_all_students(self):
        """Lấy danh sách sinh viên hiển thị lên bảng"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Join Students -> Users (lấy tên, email) -> Departments (lấy tên khoa)
            sql = """
                SELECT s.student_id, s.student_code, u.full_name, u.email, 
                       d.dept_name, s.academic_status, s.dept_id, s.major, s.academic_year
                FROM Students s
                JOIN Users u ON s.user_id = u.user_id
                LEFT JOIN Departments d ON s.dept_id = d.dept_id
                ORDER BY s.student_code ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    def update_student(self, student_id, full_name, email, dept_id, status):
        """Cập nhật thông tin sinh viên"""
        conn = DatabaseConnection.get_connection()
        try:
            conn.start_transaction()
            cursor = conn.cursor()
            
            # 1. Get User ID
            cursor.execute("SELECT user_id FROM Students WHERE student_id = %s", (student_id,))
            res = cursor.fetchone()
            if not res: return False, "Student not found"
            user_id = res[0]

            # 2. Update User Info
            cursor.execute("UPDATE Users SET full_name=%s, email=%s WHERE user_id=%s", (full_name, email, user_id))
            
            # 3. Update Student Info
            cursor.execute("UPDATE Students SET dept_id=%s, academic_status=%s WHERE student_id=%s", 
                           (dept_id, status, student_id))
            
            conn.commit()
            return True, "Student updated successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def delete_student(self, student_id):
        """Xóa sinh viên (Soft delete hoặc check ràng buộc)"""
        # (Giữ nguyên hoặc dùng hàm update status -> 'Archived' tùy nghiệp vụ)
        # Ở đây demo xóa cứng kèm check điểm
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Grades WHERE student_id=%s", (student_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Cannot delete: Student has grade records."
            
            cursor.execute("SELECT user_id FROM Students WHERE student_id=%s", (student_id,))
            uid = cursor.fetchone()[0]
            cursor.execute("DELETE FROM Students WHERE student_id=%s", (student_id,))
            cursor.execute("DELETE FROM Users WHERE user_id=%s", (uid,))
            conn.commit()
            return True, "Student deleted."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_student_academic_record(self, student_id):
        """Lấy bảng điểm chi tiết của sinh viên"""
        conn = DatabaseConnection.get_connection()
        data = {"gpa": 0.0, "credits": 0, "status": "Unknown", "grades": []}
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Lấy thông tin cơ bản & GPA (Giả lập GPA tính toán)
            cursor.execute("SELECT academic_status FROM Students WHERE student_id=%s", (student_id,))
            res = cursor.fetchone()
            if res: data['status'] = res['academic_status']

            # 2. Lấy danh sách điểm
            sql = """
                SELECT c.course_name, c.credits, g.midterm, g.final, g.total, g.letter_grade
                FROM Grades g
                JOIN Course_Classes cc ON g.class_id = cc.class_id
                JOIN Courses c ON cc.course_id = c.course_id
                WHERE g.student_id = %s
            """
            cursor.execute(sql, (student_id,))
            grades = cursor.fetchall()
            data['grades'] = grades
            
            # 3. Tính GPA & Credits tạm thời (Logic đơn giản)
            total_points = 0
            total_credits = 0
            for g in grades:
                if g['total'] is not None:
                    # Convert total / 2.5 hoặc mapping letter grade sang thang 4
                    # Demo: total 10 -> 4.0
                    gpa_point = (g['total'] / 10) * 4 
                    total_points += gpa_point * g['credits']
                    total_credits += g['credits']
            
            if total_credits > 0:
                data['gpa'] = round(total_points / total_credits, 2)
                data['credits'] = total_credits
                
            return data
        finally:
            conn.close()

    # =========================================================================
    # 6. LECTURER MANAGEMENT (FR-19 / UC16) [cite: 136-141, 645-657]
    # =========================================================================
    def get_all_lecturers(self):
        """Lấy danh sách giảng viên kèm thông tin khoa"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT l.lecturer_id, l.lecturer_code, u.full_name, u.email, u.phone,
                       d.dept_name, l.degree, l.dept_id, u.status
                FROM Lecturers l
                JOIN Users u ON l.user_id = u.user_id
                LEFT JOIN Departments d ON l.dept_id = d.dept_id
                ORDER BY l.lecturer_code ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    def create_lecturer(self, lecturer_code, full_name, email, phone, dept_id, degree):
        """Tạo tài khoản giảng viên mới (User + Lecturer Profile)"""
        conn = DatabaseConnection.get_connection()
        try:
            conn.start_transaction()
            cursor = conn.cursor()

            # 1. Create User
            hashed_pw = Security.hash_password("123") # Mật khẩu mặc định
            user_sql = """
                INSERT INTO Users (username, password, full_name, email, phone, role, status)
                VALUES (%s, %s, %s, %s, %s, 'Lecturer', 'ACTIVE')
            """
            # Username mặc định là Mã giảng viên
            cursor.execute(user_sql, (lecturer_code, hashed_pw, full_name, email, phone))
            user_id = cursor.lastrowid

            # 2. Create Lecturer Profile
            lec_sql = """
                INSERT INTO Lecturers (user_id, lecturer_code, degree, dept_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(lec_sql, (user_id, lecturer_code, dept_id, degree))

            conn.commit()
            return True, "Lecturer account created successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def update_lecturer(self, lecturer_id, full_name, email, phone, dept_id, degree):
        """Cập nhật thông tin giảng viên"""
        conn = DatabaseConnection.get_connection()
        try:
            conn.start_transaction()
            cursor = conn.cursor()

            # Lấy User ID
            cursor.execute("SELECT user_id FROM Lecturers WHERE lecturer_id=%s", (lecturer_id,))
            res = cursor.fetchone()
            if not res: return False, "Lecturer not found"
            user_id = res[0]

            # Update User
            cursor.execute("UPDATE Users SET full_name=%s, email=%s, phone=%s WHERE user_id=%s", 
                           (full_name, email, phone, user_id))
            
            # Update Lecturer
            cursor.execute("UPDATE Lecturers SET dept_id=%s, degree=%s WHERE lecturer_id=%s", 
                           (dept_id, degree, lecturer_id))

            conn.commit()
            return True, "Lecturer updated successfully."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def delete_lecturer(self, lecturer_id):
        """Xóa giảng viên (có kiểm tra ràng buộc lớp học)"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if assigned to any class
            cursor.execute("SELECT COUNT(*) FROM Course_Classes WHERE lecturer_id=%s", (lecturer_id,))
            if cursor.fetchone()[0] > 0:
                return False, "Cannot delete lecturer assigned to active classes."

            # Perform Delete
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
    # ANNOUNCEMENT MANAGEMENT (SIMPLIFIED)
    # =========================================================================
    def get_all_announcements(self):
        """Lấy danh sách thông báo"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM Announcements ORDER BY created_date DESC"
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    def create_announcement(self, title, content, officer_id):
        """Tạo thông báo mới (Chỉ Tiêu đề & Nội dung)"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = """
                INSERT INTO Announcements (title, content, officer_id, created_date) 
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(sql, (title, content, officer_id))
            conn.commit()
            return True, "Announcement posted successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def update_announcement(self, ann_id, title, content):
        """Cập nhật thông báo"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            sql = "UPDATE Announcements SET title=%s, content=%s WHERE announcement_id=%s"
            cursor.execute(sql, (title, content, ann_id))
            conn.commit()
            return True, "Announcement updated successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_announcement(self, ann_id):
        """Xóa thông báo"""
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Announcements WHERE announcement_id=%s", (ann_id,))
            conn.commit()
            return True, "Announcement deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()