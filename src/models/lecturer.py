import csv
import os
from typing import List, Dict, Optional
from src.models.user import User  # Import class cha từ module

# (Giả định đường dẫn tương đối từ thư mục chạy main.py)
DATA_PATH = {
    "schedule": "data/schedule.csv",
    "students": "data/students_template.csv",  # Dùng file template nhóm đã tạo
    "grades": "data/grades.csv"
}


class Lecturer(User):
    """
    Class Lecturer (Giảng viên) - Kế thừa từ User.
    Được thiết kế dựa trên 'Requirement Specification - Group01', Mục 1.3.
    """

    def __init__(self, user_id: str, full_name: str, email: str = "", phone: str = ""):
        # Gọi constructor của User (theo Project Structure.md)
        super().__init__(user_id, full_name, role="Lecturer", email=email)
        self.phone = phone

    # =========================================================================
    # FR-10: VIEW ASSIGNED SCHEDULE (XEM LỊCH GIẢNG DẠY)
    # =========================================================================
    def get_assigned_schedule(self) -> List[Dict]:
        """
        Lấy danh sách các lớp học phần được phân công cho giảng viên này.

        Returns:
            List[Dict]: Danh sách các lớp (Mã lớp, Phòng, Thời gian...).
        """
        schedule_list = []
        path = DATA_PATH["schedule"]

        if not os.path.exists(path):
            return []  # Trả về rỗng nếu chưa có dữ liệu

        try:
            with open(path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Logic: Chỉ lấy dòng nào có lecturer_id trùng với ID của object này
                    if row.get("lecturer_id") == self.user_id:
                        schedule_list.append({
                            "class_id": row.get("class_id"),
                            "course_name": row.get("course_name"),
                            "room": row.get("room"),
                            "time": row.get("time")
                        })
        except Exception as e:
            print(f"[ERROR] Lỗi đọc lịch giảng dạy: {e}")

        return schedule_list

    # =========================================================================
    # FR-11: VIEW STUDENT LIST (XEM DANH SÁCH SINH VIÊN)
    # =========================================================================
    def get_student_list(self, class_id: str) -> List[Dict]:
        """
        Lấy danh sách sinh viên của một lớp cụ thể.

        Args:
            class_id (str): Mã lớp học phần cần xem.

        Returns:
            List[Dict]: Danh sách sinh viên (MSSV, Họ tên, Email).
        """
        # Bước 1: (Tùy chọn) Kiểm tra xem GV có dạy lớp này không để bảo mật
        # if not self._is_assigned_to_class(class_id): return []

        students = []
        path = DATA_PATH["students"]

        if not os.path.exists(path):
            return []

        try:
            with open(path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Logic: Lọc sinh viên theo class_id
                    if row.get("class_id") == class_id:
                        students.append({
                            "student_id": row.get("student_id"),
                            "full_name": row.get("full_name"),
                            "email": row.get("email")
                        })
        except Exception as e:
            print(f"[ERROR] Lỗi đọc danh sách sinh viên: {e}")

        return students

    # =========================================================================
    # FR-12: ENTER/UPDATE GRADES (NHẬP ĐIỂM)
    # =========================================================================
    def update_student_grade(self, class_id: str, student_id: str, grade_type: str, score: float) -> bool:
        """
        Cập nhật điểm cho sinh viên.

        Args:
            class_id (str): Mã lớp.
            student_id (str): Mã sinh viên.
            grade_type (str): Loại điểm ('attendance', 'midterm', 'final').
            score (float): Điểm số (0.0 - 10.0).

        Returns:
            bool: True nếu thành công, False nếu thất bại.
        """
        # 1. Validate dữ liệu đầu vào (Clean Code Principle: Fail Fast)
        if not (0 <= score <= 10):
            print(f"[VALIDATION ERROR] Điểm {score} không hợp lệ (0-10).")
            return False

        valid_types = ['attendance', 'midterm', 'final']
        if grade_type not in valid_types:
            print(f"[VALIDATION ERROR] Loại điểm '{grade_type}' không đúng quy định.")
            return False

        # 2. Xử lý lưu trữ (Logic đọc - sửa - ghi đè file CSV)
        path = DATA_PATH["grades"]
        grades_data = []
        is_updated = False

        # Đảm bảo file tồn tại
        if not os.path.exists(path):
            # Nếu chưa có file, tạo header trước (Việc này thường do Admin làm, nhưng code phòng hờ)
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['student_id', 'class_id', 'attendance', 'midterm', 'final'])
                writer.writeheader()

        # Đọc dữ liệu cũ
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                grades_data = list(reader)
        except Exception:
            grades_data = []

        # Tìm và cập nhật
        for row in grades_data:
            if row['student_id'] == student_id and row['class_id'] == class_id:
                row[grade_type] = str(score)
                is_updated = True
                break

        # Nếu chưa có dòng dữ liệu cho SV này -> Tạo mới
        if not is_updated:
            new_record = {
                'student_id': student_id,
                'class_id': class_id,
                'attendance': '', 'midterm': '', 'final': ''
            }
            new_record[grade_type] = str(score)
            grades_data.append(new_record)

        # Ghi lại toàn bộ file
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['student_id', 'class_id', 'attendance', 'midterm', 'final'])
                writer.writeheader()
                writer.writerows(grades_data)
            return True
        except Exception as e:
            print(f"[ERROR] Lỗi khi lưu điểm: {e}")
            return False

    def __str__(self):
        return f"Lecturer: {self.full_name} ({self.user_id})"