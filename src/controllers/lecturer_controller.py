from database.repositories.lecturer_repo import LecturerRepository
from database.repositories.class_repo import ClassRepository
from database.repositories.grade_repo import GradeRepository
from models.academic.grade import Grade
from utils.validators import Validators

class LecturerController:
    def __init__(self, user_id):
        self.user_id = user_id
        
        # Khởi tạo Repositories
        self.lecturer_repo = LecturerRepository()
        self.class_repo = ClassRepository()
        self.grade_repo = GradeRepository()
        
        # Load thông tin giảng viên ngay khi khởi tạo
        self.current_lecturer = self.lecturer_repo.get_by_user_id(user_id)

    def get_teaching_schedule(self):
        """
        FR-10: View Assigned Schedule
        """
        if not self.current_lecturer:
            return []
            
        return self.class_repo.get_schedule_by_lecturer(self.current_lecturer.lecturer_id)

    def get_class_student_list(self, class_id):
        """
        FR-11: View Student List
        """
        # Tái sử dụng hàm đã có trong GradeRepo
        return self.grade_repo.get_by_class(class_id)

    def input_grade(self, student_id, class_id, attendance, midterm, final):
        """
        FR-12 & FR-13: Enter/Update Grades
        """
        # Validate inputs
        if not (Validators.is_valid_grade(attendance) and Validators.is_valid_grade(midterm) and Validators.is_valid_grade(final)):
             return False, "Grades must be between 0.0 and 10.0"

        # 1. Tìm grade_id tương ứng
        grade_id = self.grade_repo.get_id_by_enrollment(student_id, class_id)
        
        if not grade_id:
            return False, "Enrollment record not found."

        # 2. Tạo object Grade chứa dữ liệu mới
        # Lưu ý: Không cần tính total/letter ở đây, GradeRepo.update_scores sẽ tự gọi model để tính
        grade_obj = Grade(
            grade_id=grade_id,
            student_id=student_id,
            class_id=class_id,
            attendance_score=attendance,
            midterm=midterm,
            final=final,
            total=0,       # Sẽ được tính lại trong Repo
            letter_grade="" # Sẽ được tính lại trong Repo
        )

        # 3. Gọi Repo cập nhật
        # Repo sẽ tự kiểm tra is_locked và trả về lỗi nếu lớp đã khóa điểm
        return self.grade_repo.update_scores(grade_obj)