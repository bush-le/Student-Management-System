import sys
import os
import json
import bcrypt
import time
from google.genai import Client
from dotenv import load_dotenv

# Add the src directory to sys.path to fix ModuleNotFoundError
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(current_dir), 'src'))

# Import các repository từ dự án của bạn
from database.repositories.student_repo import StudentRepository
from database.repositories.course_repo import CourseRepository
from database.repositories.lecturer_repo import LecturerRepository
from database.repositories.class_repo import ClassRepository

class UnifiedDataSeeder:
    def __init__(self):
        # 1. Load cấu hình bảo mật
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Không tìm thấy GEMINI_API_KEY trong file .env!")
        
        self.client = Client(api_key=api_key)

        # 2. Khởi tạo các Repository
        self.student_repo = StudentRepository()
        self.course_repo = CourseRepository()
        self.lec_repo = LecturerRepository()
        self.class_repo = ClassRepository()

        # 3. Hash mật khẩu dùng chung cho dữ liệu mẫu (Test123!)
        self.password_hash = bcrypt.hashpw("Test123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def ask_gemini(self, prompt):
        """Hàm helper gọi Gemini và xử lý JSON"""
        try:
            full_prompt = f"{prompt}. Trả về MẢNG JSON nguyên bản, không dùng Markdown (```json), không giải thích văn bản."
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=full_prompt
            )
            text = response.text
            clean_json = text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"⚠️ Lỗi xử lý Gemini: {e}")
            return []

    # --- CÁC PHƯƠNG THỨC SEED DỮ LIỆU ---

    def seed_semesters(self):
        """Tạo học kỳ mặc định"""
        print("📅 Đang tạo học kỳ...")
        sql = "INSERT INTO Semesters (name, start_date, end_date, status) VALUES (%s, %s, %s, %s)"
        self.course_repo.execute_query(sql, ("Học kỳ 1 - 2025-2026", "2025-09-01", "2026-01-15", "OPEN"))
        print("✅ Đã tạo học kỳ.")

    def seed_courses(self, n=10):
        print(f"📚 Đang sinh {n} môn học IT...")
        prompt = f"Tạo {n} môn học CNTT. Gồm: course_code (ITxxx), course_name, credits (2-4), description."
        data = self.ask_gemini(prompt)
        added = 0
        for c in data:
            try:
                # Check if course already exists
                existing = self.course_repo.execute_query(
                    "SELECT course_id FROM Courses WHERE course_code = %s",
                    (c['course_code'],),
                    fetch_one=True
                )
                if not existing:
                    self.course_repo.execute_query(
                        "INSERT INTO Courses (course_code, course_name, credits, description) VALUES (%s, %s, %s, %s)",
                        (c['course_code'], c['course_name'], c['credits'], c['description'])
                    )
                    added += 1
            except Exception as e:
                print(f"⚠️ Lỗi thêm course {c.get('course_code')}: {e}")
        print(f"✅ Đã xong Courses (thêm {added}/{len(data)} môn học mới).")

    def seed_lecturers(self, n=5):
        print(f"👨‍🏫 Đang sinh {n} giảng viên...")
        prompt = f"Tạo {n} giảng viên VN. Gồm: full_name, email (@uth.edu.vn), phone, lecturer_code (GVxxx), degree (MSc hoặc PhD)."
        data = self.ask_gemini(prompt)
        added = 0
        for l in data:
            try:
                # Check if lecturer already exists (by username or email)
                existing = self.lec_repo.execute_query(
                    "SELECT user_id FROM Users WHERE username = %s OR email = %s",
                    (l['lecturer_code'], l['email']),
                    fetch_one=True
                )
                if not existing:
                    time.sleep(0.05)  # Small delay to avoid "Unread result found"
                    user_id = self.lec_repo.execute_query(
                        "INSERT INTO Users (username, email, password, full_name, role) VALUES (%s, %s, %s, %s, 'Lecturer')",
                        (l['lecturer_code'], l['email'], self.password_hash, l['full_name'])
                    )
                    time.sleep(0.05)
                    self.lec_repo.execute_query(
                        "INSERT INTO Lecturers (user_id, lecturer_code, degree) VALUES (%s, %s, %s)",
                        (user_id, l['lecturer_code'], l['degree'])
                    )
                    added += 1
            except Exception as e:
                print(f"⚠️ Lỗi thêm lecturer {l.get('lecturer_code')}: {e}")
        print(f"✅ Đã xong Lecturers (thêm {added}/{len(data)} giảng viên mới).")

    def seed_students(self, n=15):
        print(f"👨‍🎓 Đang sinh {n} sinh viên...")
        prompt = f"Tạo {n} sinh viên VN. Gồm: full_name, email (@student.uth.edu.vn), phone, student_code."
        data = self.ask_gemini(prompt)
        added = 0
        for s in data:
            try:
                # Check if student already exists (by username or email)
                existing = self.student_repo.execute_query(
                    "SELECT user_id FROM Users WHERE username = %s OR email = %s",
                    (s['student_code'], s['email']),
                    fetch_one=True
                )
                if not existing:
                    time.sleep(0.05)  # Small delay to avoid "Unread result found"
                    user_id = self.student_repo.execute_query(
                        "INSERT INTO Users (username, email, password, full_name, role) VALUES (%s, %s, %s, %s, 'Student')",
                        (s['student_code'], s['email'], self.password_hash, s['full_name'])
                    )
                    time.sleep(0.05)
                    self.student_repo.execute_query(
                        "INSERT INTO Students (user_id, student_code) VALUES (%s, %s)",
                        (user_id, s['student_code'])
                    )
                    added += 1
            except Exception as e:
                print(f"⚠️ Lỗi thêm student {s.get('student_code')}: {e}")
        print(f"✅ Đã xong Students (thêm {added}/{len(data)} sinh viên mới).")

    def seed_classes(self, n=8):
        print(f"🏫 Đang thiết lập {n} lớp học...")
        # Lấy context từ DB để Gemini không tạo dữ liệu rác
        courses = self.class_repo.execute_query("SELECT course_id, course_name FROM Courses", fetch_all=True)
        lecturers = self.class_repo.execute_query("SELECT lecturer_id FROM Lecturers", fetch_all=True)
        semester = self.class_repo.execute_query("SELECT semester_id FROM Semesters LIMIT 1", fetch_one=True)

        if not courses or not lecturers or not semester:
            print("⚠️ Không có dữ liệu courses, lecturers hoặc semester")
            return

        prompt = f"""Dựa trên {len(courses)} courses và {len(lecturers)} lecturers.
        Tạo {n} lớp học cho học kỳ {semester['semester_id']}. 
        Gồm: course_idx (0-{len(courses)-1}), lecturer_idx (0-{len(lecturers)-1}), room (Phòng A/B/C.xxx), schedule (Thứ + Giờ), max_capacity (40-60)."""
        
        data = self.ask_gemini(prompt)
        for cl in data:
            try:
                course_idx = int(cl.get('course_idx', 0))
                lecturer_idx = int(cl.get('lecturer_idx', 0))
                
                # Validate indices
                if course_idx >= len(courses) or lecturer_idx >= len(lecturers):
                    continue
                    
                course_id = courses[course_idx]['course_id']
                lecturer_id = lecturers[lecturer_idx]['lecturer_id']
                
                self.class_repo.execute_query(
                    """INSERT INTO Course_Classes (course_id, lecturer_id, semester_id, room, schedule, max_capacity) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (course_id, lecturer_id, semester['semester_id'], cl['room'], cl['schedule'], cl['max_capacity'])
                )
            except Exception as e:
                print(f"⚠️ Lỗi tạo lớp: {e}")
        print("✅ Đã xong Classes.")

    def run_all(self):
        """Thực hiện theo đúng thứ tự ràng buộc khóa ngoại"""
        print("🚀 BẮT ĐẦU QUY TRÌNH SEED DỮ LIỆU TỔNG HỢP...")
        try:
            self.seed_semesters()
            self.seed_courses(30)
            self.seed_lecturers(100)
            self.seed_students(100)
            self.seed_classes(40)

            print("🎉 THÀNH CÔNG! Database của bạn đã đầy đủ dữ liệu thực tế.")
        except Exception as e:
            print(f"❌ Quy trình thất bại: {e}")

if __name__ == "__main__":
    seeder = UnifiedDataSeeder()
    seeder.run_all()