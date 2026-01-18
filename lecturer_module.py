from datetime import datetime
from typing import List, Dict, Optional

# ==========================================
# 1. BASE CLASS: USER (Common Module 1.1)
# ==========================================
class User:
    """
    Lớp cha đại diện cho người dùng hệ thống.
    Đáp ứng Module 1.1: Common Module (Authentication & Security)
    """
    def __init__(self, user_id: str, full_name: str, email: str, password: str):
        self._user_id = user_id        # Encapsulation: Protected attribute
        self._full_name = full_name
        self._email = email
        self.__password = password     # Encapsulation: Private attribute

    def login(self, email: str, password: str) -> bool:
        """
        FR-01: User Login
        Kiểm tra thông tin đăng nhập.
        """
        if self._email == email and self.__password == password:
            print(f"[System] Đăng nhập thành công. Chào mừng {self._full_name}.")
            return True
        print("[System] Lỗi: Sai email hoặc mật khẩu.")
        return False

    def change_password(self, old_pass: str, new_pass: str) -> bool:
        """
        FR-03: Change Password
        Thay đổi mật khẩu với điều kiện bảo mật.
        """
        if self.__password != old_pass:
            print("[System] Lỗi: Mật khẩu cũ không đúng.")
            return False
        
        # Kiểm tra độ mạnh mật khẩu (giả lập quy tắc FR-03)
        if len(new_pass) < 8:
            print("[System] Lỗi: Mật khẩu mới phải có ít nhất 8 ký tự.")
            return False
            
        self.__password = new_pass
        print(f"[System] Đổi mật khẩu thành công cho user {self._user_id}.")
        return True

    def get_user_id(self) -> str:
        return self._user_id

    def get_full_name(self) -> str:
        return self._full_name


# ==========================================
# 2. HELPER CLASSES (Mô phỏng dữ liệu)
# ==========================================
class Student:
    """Đại diện cho sinh viên trong danh sách lớp (UC11)"""
    def __init__(self, student_id: str, full_name: str, email: str):
        self.student_id = student_id
        self.full_name = full_name
        self.email = email
        self.grades: Dict[str, float] = {} # Lưu điểm: {'midterm': 8.0, 'final': 9.0}

class Classroom:
    """Đại diện cho lớp học phần (UC10, UC16)"""
    def __init__(self, class_code: str, course_name: str, room: str, days: str, time: str):
        self.class_code = class_code
        self.course_name = course_name
        self.room = room
        self.days = days
        self.time = time
        self.students: List[Student] = []
        self.is_finalized = False  # Trạng thái chốt điểm

    def add_student(self, student: Student):
        self.students.append(student)


# ==========================================
# 3. MAIN CLASS: LECTURER (Module 1.3)
# ==========================================
class Lecturer(User):
    """
    Lớp Giảng viên, kế thừa từ User.
    Thực hiện các chức năng trong Mục 1.3 và Use Cases UC10-UC13.
    """
    def __init__(self, user_id: str, full_name: str, email: str, password: str, department: str):
        super().__init__(user_id, full_name, email, password)
        self._department = department
        self._assigned_classes: List[Classroom] = [] # Danh sách lớp được phân công

    # ---------------------------------------------------------
    # Use Case 10 (UC10) & FR-10: View Assigned Schedule
    # ---------------------------------------------------------
    def view_assigned_schedule(self):
        """
        FR-10: Hiển thị lịch giảng dạy.
        Chi tiết: Tên lớp, Mã học phần, Phòng, Ngày dạy, Ca dạy, Số lượng SV.
        """
        print(f"\n--- LỊCH GIẢNG DẠY CỦA GV: {self._full_name} ---")
        if not self._assigned_classes:
            print("[Info] Không có lớp học nào được phân công trong học kỳ này.")
            return

        print(f"{'Mã Lớp':<15} {'Môn Học':<25} {'Phòng':<10} {'Thời Gian':<20} {'Sĩ Số':<10}")
        print("-" * 80)
        for classroom in self._assigned_classes:
            print(f"{classroom.class_code:<15} {classroom.course_name:<25} "
                  f"{classroom.room:<10} {classroom.days} {classroom.time:<10} "
                  f"{len(classroom.students):<10}")
        print("-" * 80)

    # ---------------------------------------------------------
    # Use Case 11 (UC11) & FR-11: View Student List
    # ---------------------------------------------------------
    def view_student_list(self, class_code: str):
        """
        FR-11: Xem danh sách sinh viên của một lớp cụ thể.
        Chi tiết: Hiển thị ID, Tên, Liên hệ, Tóm tắt điểm.
        """
        selected_class = self.__find_class(class_code)
        if not selected_class:
            print(f"[Error] Không tìm thấy lớp có mã {class_code} trong lịch phân công.")
            return

        print(f"\n--- DANH SÁCH SINH VIÊN LỚP {class_code} ---")
        if not selected_class.students:
            print("[Info] Lớp này chưa có sinh viên đăng ký.")
            return

        print(f"{'MSSV':<10} {'Họ Tên':<25} {'Email':<25} {'Điểm TK'}")
        for std in selected_class.students:
            # Tính điểm tổng kết giả định để hiển thị
            gpa = self.__calculate_gpa(std.grades)
            gpa_display = f"{gpa:.2f}" if gpa is not None else "N/A"
            print(f"{std.student_id:<10} {std.full_name:<25} {std.email:<25} {gpa_display}")

    # ---------------------------------------------------------
    # Use Case 12 (UC12) & FR-12: Enter Grades
    # ---------------------------------------------------------
    def enter_grades(self, class_code: str, student_id: str, component: str, score: float):
        """
        FR-12: Nhập điểm cho sinh viên.
        - Validate điểm (0-10).
        - Lưu điểm vào hệ thống.
        - Thông báo cho sinh viên (Simulated).
        """
        # 1. Tìm lớp
        selected_class = self.__find_class(class_code)
        if not selected_class:
            print(f"[Error] Giảng viên không dạy lớp {class_code}.")
            return

        # 2. Kiểm tra trạng thái chốt điểm (Lock grades)
        if selected_class.is_finalized:
            print(f"[Error] Lớp {class_code} đã chốt điểm. Không thể nhập thêm.")
            return

        # 3. Tìm sinh viên
        student = next((s for s in selected_class.students if s.student_id == student_id), None)
        if not student:
            print(f"[Error] Sinh viên {student_id} không có trong lớp {class_code}.")
            return

        # 4. Validate điểm (0-10 scale)
        if not (0 <= score <= 10):
            print("[Error] Điểm phải nằm trong khoảng từ 0 đến 10.")
            return

        # 5. Lưu điểm
        student.grades[component] = score
        print(f"[Success] Đã nhập điểm '{component}' = {score} cho SV {student.full_name}.")
        
        # 6. Gửi thông báo (FR-12: Notify affected students)
        self.__send_notification(student.email, f"Điểm {component} mới: {score}")

    # ---------------------------------------------------------
    # Use Case 13 (UC13) & FR-13: Update Grades
    # ---------------------------------------------------------
    def update_grades(self, class_code: str, student_id: str, component: str, new_score: float):
        """
        FR-13: Cập nhật điểm số.
        - Ghi log audit (Simulated).
        - Thông báo cho sinh viên.
        """
        print(f"\n[System Log] Giảng viên {self._user_id} yêu cầu sửa điểm...")
        # Tái sử dụng logic nhập điểm vì bản chất giống nhau, 
        # nhưng trong thực tế sẽ cần kiểm tra thêm "thời hạn sửa điểm" (limited period)
        self.enter_grades(class_code, student_id, component, new_score)
        print("[Audit] Hành động sửa điểm đã được ghi lại vào nhật ký hệ thống.")

    def finalize_class_grades(self, class_code: str):
        """
        FR-12: Save and lock the grades.
        Chốt điểm để ngăn chặn thay đổi sau này.
        """
        selected_class = self.__find_class(class_code)
        if selected_class:
            selected_class.is_finalized = True
            print(f"[Info] Điểm lớp {class_code} đã được CHỐT. Không thể chỉnh sửa.")

    # ---------------------------------------------------------
    # Helper Methods (Private)
    # ---------------------------------------------------------
    def assign_class(self, classroom: Classroom):
        """Hỗ trợ thêm lớp vào lịch giảng dạy (Thường do Admin thực hiện - FR-17)"""
        self._assigned_classes.append(classroom)

    def __find_class(self, class_code: str) -> Optional[Classroom]:
        """Tìm lớp trong danh sách phân công"""
        for cls in self._assigned_classes:
            if cls.class_code == class_code:
                return cls
        return None

    def __calculate_gpa(self, grades: Dict[str, float]) -> Optional[float]:
        """
        FR-12: Automatically calculate weighted averages.
        Giả sử tỉ lệ: Midterm 30%, Final 70%
        """
        if 'midterm' in grades and 'final' in grades:
            return grades['midterm'] * 0.3 + grades['final'] * 0.7
        return None

    def __send_notification(self, email: str, message: str):
        """FR-12/13: Hệ thống thông báo qua App"""
        print(f"   >>> [Notification sent to {email}]: {message}")


# ==========================================
# 4. DEMO / DRIVER CODE
# ==========================================
if __name__ == "__main__":
    # 1. Khởi tạo Giảng viên
    lecturer = Lecturer("L001", "Trần Thị Mỹ Tiên", "tien.tran@uth.edu.vn", "password123", "CNTT")
    
    # 2. Khởi tạo Dữ liệu giả lập (Lớp học và Sinh viên)
    se_class = Classroom("SE101", "Công nghệ phần mềm", "C302", "Thứ 2", "07:00-11:30")
    sv1 = Student("SV001", "Nguyễn Văn A", "a.nguyen@st.uth.edu.vn")
    sv2 = Student("SV002", "Lê Thị B", "b.le@st.uth.edu.vn")
    
    se_class.add_student(sv1)
    se_class.add_student(sv2)

    # Admin phân công lớp cho giảng viên
    lecturer.assign_class(se_class)

    # ==========================================
    # TEST SCENARIOS (Dựa trên Use Cases)
    # ==========================================
    
    # UC01: Đăng nhập
    lecturer.login("tien.tran@uth.edu.vn", "password123")

    # UC10 / FR-10: Xem lịch giảng dạy
    lecturer.view_assigned_schedule()

    # UC11 / FR-11: Xem danh sách sinh viên lớp SE101
    lecturer.view_student_list("SE101")

    # UC12 / FR-12: Nhập điểm (Midterm, Final)
    print("\n--- NHẬP ĐIỂM ---")
    lecturer.enter_grades("SE101", "SV001", "midterm", 8.0)
    lecturer.enter_grades("SE101", "SV001", "final", 9.0)
    
    # Nhập điểm lỗi (ngoài range)
    lecturer.enter_grades("SE101", "SV002", "midterm", 11.0) 

    # Xem lại danh sách để thấy điểm tổng kết tự động tính (FR-12)
    lecturer.view_student_list("SE101")

    # UC13 / FR-13: Sửa điểm
    print("\n--- SỬA ĐIỂM ---")
    lecturer.update_grades("SE101", "SV001", "midterm", 8.5)

    # FR-12: Chốt điểm (Lock)
    lecturer.finalize_class_grades("SE101")

    # Thử sửa điểm sau khi đã khóa (Mong đợi lỗi)
    lecturer.update_grades("SE101", "SV001", "final", 10.0)