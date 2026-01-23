from database.repositories.student_repo import StudentRepository
from database.repositories.lecturer_repo import LecturerRepository
from database.repositories.course_repo import CourseRepository
from database.repositories.semester_repo import SemesterRepository
from database.repositories.class_repo import ClassRepository
from database.repositories.announcement_repo import AnnouncementRepository
from database.repositories.department_repo import DepartmentRepository
from database.repositories.grade_repo import GradeRepository

from models.student import Student
from models.lecturer import Lecturer
from models.academic.course import Course
from models.academic.semester import Semester
from models.academic.course_class import CourseClass
from models.academic.announcement import Announcement

from utils.security import Security
from utils.validators import Validators

class AdminController:
    def __init__(self, user_id):
        self.user_id = user_id
        # Khởi tạo tất cả Repositories
        self.student_repo = StudentRepository()
        self.lecturer_repo = LecturerRepository()
        self.course_repo = CourseRepository()
        self.semester_repo = SemesterRepository()
        self.class_repo = ClassRepository()
        self.ann_repo = AnnouncementRepository()
        self.dept_repo = DepartmentRepository()
        self.grade_repo = GradeRepository()

    # =========================================================================
    # 1. STUDENT MANAGEMENT
    # =========================================================================
    def get_all_students(self, page=1, per_page=15):
        return self.student_repo.get_all(page=page, per_page=per_page)

    def get_total_students(self):
        return self.student_repo.count_all()

    def create_student(self, full_name, email, phone, student_code, dept_id, major, year):
        if not Validators.is_valid_email(email):
            return False, "Invalid email format"
        
        if not Validators.is_valid_phone(phone):
            return False, "Invalid phone number format"

        hashed_pw = Security.hash_password("123")
        new_student = Student(
            user_data={"user_id": None, "username": student_code, "full_name": full_name, "email": email, "phone": phone, "role": "Student", "status": "ACTIVE"},
            student_id=None, student_code=student_code, major=major, dept_id=dept_id, academic_year=year
        )
        return self.student_repo.add(new_student, hashed_pw)

    def update_student(self, student_id, full_name, email, dept_id, status):
        if not Validators.is_valid_email(email):
            return False, "Invalid email format"
            
        student = self.student_repo.get_by_id(student_id)
        if not student: return False, "Not found"
        student.full_name = full_name
        student.email = email
        student.dept_id = dept_id
        student.academic_status = status
        return self.student_repo.update(student)

    def delete_student(self, student_id):
        return self.student_repo.delete(student_id)

    def import_students_csv(self, file_path):
        import csv
        students = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Validate row data here if needed
                    students.append({
                        'code': row['StudentCode'],
                        'name': row['FullName'],
                        'email': row['Email'],
                        'major': row.get('Major', 'N/A')
                    })
            
            if not students: return False, "Empty CSV file"
            
            return self.student_repo.bulk_add(students)
        except Exception as e:
            return False, f"CSV Error: {str(e)}"

    # =========================================================================
    # 2. LECTURER MANAGEMENT
    # =========================================================================
    def get_all_lecturers(self, page=1, per_page=15):
        return self.lecturer_repo.get_all(page=page, per_page=per_page)

    def get_total_lecturers(self):
        return self.lecturer_repo.count_all()

    def create_lecturer(self, lecturer_code, full_name, email, phone, dept_id, degree):
        if not Validators.is_valid_email(email):
            return False, "Invalid email format"
        
        if not Validators.is_valid_phone(phone):
            return False, "Invalid phone number format"

        hashed_pw = Security.hash_password("123")
        new_lec = Lecturer(
            user_data={"user_id": None, "username": lecturer_code, "full_name": full_name, "email": email, "phone": phone, "role": "Lecturer", "status": "ACTIVE"},
            lecturer_id=None, lecturer_code=lecturer_code, dept_id=dept_id, degree=degree
        )
        return self.lecturer_repo.add(new_lec, hashed_pw)

    def update_lecturer(self, lecturer_id, full_name, email, phone, dept_id, degree):
        if not Validators.is_valid_email(email):
            return False, "Invalid email format"
        
        if not Validators.is_valid_phone(phone):
            return False, "Invalid phone number format"

        lec = self.lecturer_repo.get_by_id(lecturer_id)
        if not lec: return False, "Not found"
        lec.full_name = full_name
        lec.email = email
        lec.phone = phone
        lec.dept_id = dept_id
        lec.degree = degree
        return self.lecturer_repo.update(lec)

    def delete_lecturer(self, lecturer_id):
        return self.lecturer_repo.delete(lecturer_id)

    # =========================================================================
    # 3. COURSE MANAGEMENT
    # =========================================================================
    def get_all_courses(self, page=1, per_page=15):
        return self.course_repo.get_all(page=page, per_page=per_page)

    def get_total_courses(self):
        return self.course_repo.count_all()

    def create_course(self, code, name, credits, type_c, desc, prereq):
        new_course = Course(None, code, name, credits, type_c, desc, prereq)
        return self.course_repo.add(new_course)

    def update_course(self, course_id, code, name, credits, type_c, desc, prereq):
        # Lưu ý: để tối ưu có thể thêm get_by_id cho course_repo, 
        # nhưng ở đây ta tạo object mới với ID cũ để update trực tiếp cho nhanh
        updated_course = Course(course_id, code, name, credits, type_c, desc, prereq)
        return self.course_repo.update(updated_course)

    def delete_course(self, course_id):
        return self.course_repo.delete(course_id)

    # =========================================================================
    # 4. SEMESTER MANAGEMENT
    # =========================================================================
    def get_all_semesters(self):
        return self.semester_repo.get_all()

    def create_semester(self, name, start, end):
        # Mặc định tạo là OPEN
        return self.semester_repo.add(Semester(None, name, start, end, "OPEN"))

    def update_semester(self, sem_id, name, start, end, status):
        return self.semester_repo.update(Semester(sem_id, name, start, end, status))

    def delete_semester(self, sem_id):
        return self.semester_repo.delete(sem_id)

    # =========================================================================
    # 5. CLASS MANAGEMENT
    # =========================================================================
    def get_all_classes_details(self, page=1, per_page=15):
        return self.class_repo.get_all_details(page=page, per_page=per_page)

    def get_total_classes(self):
        return self.class_repo.count_all()

    def create_class(self, course_id, semester_name, room, schedule, capacity):
        # Giả lập semester_id = 1 (Trong thực tế cần query semester_repo.get_by_name)
        semester_id = 1 
        new_cls = CourseClass(None, course_id, semester_id, room, schedule, capacity)
        return self.class_repo.add(new_cls)

    def update_class(self, class_id, room, schedule, capacity):
        # Tạo dummy object chỉ chứa thông tin cần update
        # class_repo.update cần chỉnh để chỉ update các trường này, hoặc truyền đủ param
        # Ở repo trên tôi đã viết update nhận object đầy đủ, nhưng chỉ dùng 3 trường này.
        dummy_cls = CourseClass(class_id, None, None, room, schedule, capacity)
        return self.class_repo.update(dummy_cls)

    def assign_lecturer_to_class(self, class_id, lecturer_id):
        return self.class_repo.assign_lecturer(class_id, lecturer_id)

    def delete_class(self, class_id):
        return self.class_repo.delete(class_id)

    # =========================================================================
    # 6. ANNOUNCEMENT MANAGEMENT
    # =========================================================================
    def get_all_announcements(self):
        return self.ann_repo.get_all()

    def create_announcement(self, title, content, officer_id):
        return self.ann_repo.add(Announcement(None, title, content, None, officer_id))

    def update_announcement(self, ann_id, title, content):
        return self.ann_repo.update(Announcement(ann_id, title, content, None, None))

    def delete_announcement(self, ann_id):
        return self.ann_repo.delete(ann_id)

    # =========================================================================
    # HELPERS (Cho Dropdown)
    # =========================================================================
    def get_all_departments(self):
        """Lấy danh sách khoa để hiển thị lên ComboBox"""
        return self.dept_repo.get_all()

    def get_dashboard_stats(self):
        """Lấy số liệu thống kê tổng quan cho Dashboard từ DB thật."""
        try:
            stats = {
                'students': self.student_repo.count_all(),
                'lecturers': self.lecturer_repo.count_all(),
                'courses': self.course_repo.count_all(),
                'classes': self.class_repo.count_all()
            }
            return stats
        except Exception as e:
            print(f"Lỗi khi lấy thống kê Dashboard: {e}")
            # Trả về 0 nếu có lỗi DB để tránh crash UI
            return {'students': 0, 'lecturers': 0, 'courses': 0, 'classes': 0}

    # =========================================================================
    # VIEW ACADEMIC RECORD (Cập nhật dùng GradeRepo)
    # =========================================================================
    def get_student_academic_record(self, student_id):
        """
        Lấy bảng điểm chi tiết của sinh viên.
        Trả về dictionary tổng hợp để View dễ hiển thị (GPA, Credits, List Grades).
        """
        # 1. Lấy thông tin Grades từ Repo
        grades = self.grade_repo.get_by_student(student_id)
        
        # 2. Lấy thông tin Student status (tái sử dụng StudentRepo)
        student = self.student_repo.get_by_id(student_id)
        status = student.academic_status if student else "Unknown"

        # 3. Tính GPA & Credits
        total_points = 0
        total_credits = 0
        
        # Helper: Map Letter Grade sang thang điểm 4 (đơn giản)
        point_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}

        for g in grades:
            # Chỉ tính các môn đã có điểm tổng kết và không phải F (nếu tính tích lũy)
            if g.letter_grade:
                p = point_map.get(g.letter_grade, 0.0)
                total_points += p * g.credits
                total_credits += g.credits
        
        gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

        return {
            "gpa": gpa,
            "credits": total_credits,
            "status": status,
            "grades": grades # List các object Grade
        }