from database.repositories.student_repo import StudentRepository
from database.repositories.class_repo import ClassRepository
from database.repositories.grade_repo import GradeRepository

class StudentController:
    def __init__(self, user_id):
        self.user_id = user_id
        
        # Khởi tạo Repositories
        self.student_repo = StudentRepository()
        self.class_repo = ClassRepository()
        self.grade_repo = GradeRepository()
        
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

        # Cập nhật dữ liệu vào Object hiện tại
        self.current_student.email = email
        self.current_student.phone = phone
        self.current_student.address = address # Đảm bảo Model User/Student có field address

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

        # Sử dụng lại GradeRepo đã viết (trả về List[Grade Object])
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