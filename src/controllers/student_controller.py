from database.repositories.student_repo import StudentRepository
from database.repositories.class_repo import ClassRepository
from database.repositories.grade_repo import GradeRepository
from database.repositories.announcement_repo import AnnouncementRepository
from utils.validators import Validators
from datetime import datetime

class StudentController:
    def __init__(self, user_id):
        self.user_id = user_id
        
        # Khởi tạo Repositories
        self.student_repo = StudentRepository()
        self.class_repo = ClassRepository()
        self.grade_repo = GradeRepository()
        self.ann_repo = AnnouncementRepository()
        
        # Load thông tin sinh viên ngay khi khởi tạo
        # Giúp các hàm sau không cần query lại ID
        self.current_student = self.student_repo.get_by_user_id(user_id)

    def view_profile(self):
        """
        FR-05: View Personal Information
        Returns: Student Object
        """
        return self.current_student

    def update_contact_info(self, email, phone, address):
        """
        FR-06: Update Personal Information
        """
        if not self.current_student:
            return False, "Student profile not found."

        if not Validators.is_valid_email(email):
            return False, "Invalid email format."
            
        if not Validators.is_valid_phone(phone):
            return False, "Invalid phone number format."

        # Cập nhật dữ liệu vào Object hiện tại
        self.current_student.email = email
        self.current_student.phone = phone
        
        # Lưu ý: Model Student cần có thuộc tính address
        if hasattr(self.current_student, 'address'):
            self.current_student.address = address

        # Gọi Repo để lưu xuống DB
        return self.student_repo.update_contact_info(self.current_student)

    def view_schedule(self):
        """
        FR-07: View Weekly Schedule
        """
        if not self.current_student: return []
        
        return self.class_repo.get_schedule_by_student(self.current_student.student_id)

    def view_grades(self):
        """
        FR-08: View Academic Results
        """
        if not self.current_student: return []

        if not self.current_student: return {'transcript': [], 'cumulative_gpa': 0.0}
        grades = self.grade_repo.get_by_student(self.current_student.student_id)
        
        # Tính toán GPA tích lũy (Optional - Logic nghiệp vụ)
        total_points = 0
        total_credits = 0
        point_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}

        for g in grades:
            if g.letter_grade:
                # Giả sử trong model Grade đã join lấy credits
                cred = getattr(g, 'credits', 3) # Mặc định 3 nếu không lấy được
                total_points += point_map.get(g.letter_grade, 0) * cred
                total_credits += cred
        
        gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
        
        # Trả về dict chứa cả list điểm và GPA tổng
        return {
            "transcript": grades,
            "cumulative_gpa": gpa
        }

    # --- CÁC HÀM BỔ SUNG CHO DASHBOARD ---

    def get_upcoming_class(self):
        """Lấy lớp học sắp tới cho Student Dashboard"""
        schedule = self.view_schedule()
        if not schedule: return None
        # Logic đơn giản: trả về lớp đầu tiên
        return schedule[0]

    def get_academic_stats(self):
        """Lấy thống kê GPA/Credits cho Dashboard"""
        data = self.view_grades()
        # Tính lại total credits
        grades = data['transcript']
        credits_earned = sum(getattr(g, 'credits', 3) for g in grades if g.letter_grade and g.letter_grade != 'F')
        
        return {
            'gpa': data['cumulative_gpa'],
            'credits': credits_earned,
            'semester': 'N/A' # Placeholder
        }

    def get_recent_grades(self, limit=3):
        """Lấy 3 điểm mới nhất"""
        data = self.view_grades()
        transcript = data['transcript']
        # Giả sử transcript đã sort hoặc lấy 3 cái cuối
        return transcript[:limit]

    def get_latest_announcements(self, limit=3):
        return self.ann_repo.get_recent(limit)
    
    def get_student_profile(self):
        """Lấy full profile bao gồm lớp, khoa"""
        # Cần repo hỗ trợ join, tạm thời trả về object hiện tại dạng dict
        if not self.current_student: return {}
        return {
            'full_name': self.current_student.full_name,
            'email': self.current_student.email,
            'phone': self.current_student.phone,
            'student_code': self.current_student.student_code,
            'dept_name': 'Information Technology', # Placeholder
            'class_name': 'SE_K24', # Placeholder
            'dob': '2004-01-01',
            'address': getattr(self.current_student, 'address', '')
        }
    
    def update_student_profile(self, user_id, email, phone, address, dob):
        """Update Profile từ View"""
        return self.update_contact_info(email, phone, address)