import sys
import os

# Add the src directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(current_dir), 'src'))

from database.repositories.student_repo import StudentRepository
from database.repositories.lecturer_repo import LecturerRepository
from database.repositories.course_repo import CourseRepository
from database.repositories.class_repo import ClassRepository

class DatabaseCleaner:
    def __init__(self):
        self.student_repo = StudentRepository()
        self.lecturer_repo = LecturerRepository()
        self.course_repo = CourseRepository()
        self.class_repo = ClassRepository()
        
        # Users to keep
        self.keep_usernames = ['student_test', 'lecturer_test', 'admin_test', 'test_forgetpassword']

    def get_keep_user_ids(self):
        """Get user_ids of test users to keep"""
        placeholders = ','.join(['%s'] * len(self.keep_usernames))
        sql = f"SELECT user_id FROM Users WHERE username IN ({placeholders})"
        result = self.course_repo.execute_query(sql, tuple(self.keep_usernames), fetch_all=True)
        return [row['user_id'] for row in result]

    def get_ids(self, query, params=()):
        """Helper to get list of IDs from query"""
        res = self.course_repo.execute_query(query, params, fetch_all=True)
        if not res: return []
        key = list(res[0].keys())[0]
        return [r[key] for r in res]

    def delete_not_in(self, table, col, ids):
        """Delete rows where col NOT IN ids"""
        if not ids:
            self.course_repo.execute_query(f"DELETE FROM {table}")
        else:
            placeholders = ','.join(['%s'] * len(ids))
            self.course_repo.execute_query(f"DELETE FROM {table} WHERE {col} NOT IN ({placeholders})", tuple(ids))

    def cleanup(self):
        """Giữ lại test users và một lượng nhỏ dữ liệu demo (~10 records mỗi loại)"""
        print("🗑️ Bắt đầu thu gọn database (giữ lại demo data)...")
        try:
            # 1. Lấy ID của các Test Users gốc
            test_user_ids = self.get_keep_user_ids()
            if not test_user_ids:
                print("⚠️ Không tìm thấy test users.")
                return
            print(f"✅ Tìm thấy {len(test_user_ids)} test users gốc.")

            # 2. Xác định Lecturers & Students tương ứng với Test Users
            test_lec_ids = self.get_ids(f"SELECT lecturer_id FROM Lecturers WHERE user_id IN ({','.join(['%s']*len(test_user_ids))})", tuple(test_user_ids))
            test_stu_ids = self.get_ids(f"SELECT student_id FROM Students WHERE user_id IN ({','.join(['%s']*len(test_user_ids))})", tuple(test_user_ids))

            # 3. Chọn thêm Lecturers để giữ lại (Test + ~8 Random)
            if test_lec_ids:
                exclude = ','.join(map(str, test_lec_ids))
                random_lecs = self.get_ids(f"SELECT lecturer_id FROM Lecturers WHERE lecturer_id NOT IN ({exclude}) ORDER BY RAND() LIMIT 8")
                keep_lec_ids = test_lec_ids + random_lecs
            else:
                keep_lec_ids = self.get_ids("SELECT lecturer_id FROM Lecturers ORDER BY RAND() LIMIT 10")

            # 4. Chọn Classes để giữ lại (Ưu tiên lớp của Lecturer được giữ)
            if keep_lec_ids:
                l_in = ','.join(map(str, keep_lec_ids))
                # Giữ khoảng 15 lớp bất kỳ thuộc về các giảng viên này
                keep_class_ids = self.get_ids(f"SELECT class_id FROM Course_Classes WHERE lecturer_id IN ({l_in}) ORDER BY RAND() LIMIT 15")
            else:
                keep_class_ids = []

            # 5. Suy ra Courses & Semesters cần giữ từ Classes đã chọn
            if keep_class_ids:
                c_in = ','.join(map(str, keep_class_ids))
                keep_course_ids = self.get_ids(f"SELECT DISTINCT course_id FROM Course_Classes WHERE class_id IN ({c_in})")
                keep_sem_ids = self.get_ids(f"SELECT DISTINCT semester_id FROM Course_Classes WHERE class_id IN ({c_in})")
            else:
                keep_course_ids = []
                keep_sem_ids = []

            # 6. Chọn Students để giữ lại (Test + Students có trong lớp đã chọn + Random)
            students_in_classes = []
            if keep_class_ids:
                c_in = ','.join(map(str, keep_class_ids))
                students_in_classes = self.get_ids(f"SELECT DISTINCT student_id FROM Grades WHERE class_id IN ({c_in}) ORDER BY RAND() LIMIT 15")
            
            keep_stu_ids = list(set(test_stu_ids + students_in_classes))
            
            # Nếu ít quá thì lấy thêm random cho đủ 10-15
            if len(keep_stu_ids) < 12:
                needed = 12 - len(keep_stu_ids)
                exclude = ','.join(map(str, keep_stu_ids)) if keep_stu_ids else "0"
                random_stus = self.get_ids(f"SELECT student_id FROM Students WHERE student_id NOT IN ({exclude}) ORDER BY RAND() LIMIT {needed}")
                keep_stu_ids.extend(random_stus)

            # 7. Xác định Users cần giữ (Test Users + Users của Lecturers/Students được giữ)
            keep_user_ids = set(test_user_ids)
            if keep_lec_ids:
                l_in = ','.join(map(str, keep_lec_ids))
                keep_user_ids.update(self.get_ids(f"SELECT user_id FROM Lecturers WHERE lecturer_id IN ({l_in})"))
            if keep_stu_ids:
                s_in = ','.join(map(str, keep_stu_ids))
                keep_user_ids.update(self.get_ids(f"SELECT user_id FROM Students WHERE student_id IN ({s_in})"))
            keep_user_ids = list(keep_user_ids)

            print(f"📊 Kế hoạch giữ lại: {len(keep_user_ids)} Users, {len(keep_stu_ids)} Students, {len(keep_lec_ids)} Lecturers, {len(keep_class_ids)} Classes.")

            # 8. THỰC HIỆN XÓA (Thứ tự quan trọng)
            # Xóa Grades không thuộc về student/class được giữ
            if keep_stu_ids and keep_class_ids:
                s_in = ','.join(map(str, keep_stu_ids))
                c_in = ','.join(map(str, keep_class_ids))
                self.course_repo.execute_query(f"DELETE FROM Grades WHERE student_id NOT IN ({s_in}) OR class_id NOT IN ({c_in})")
            else:
                self.course_repo.execute_query("DELETE FROM Grades")
            print("✅ Đã dọn dẹp Grades.")
            
            self.delete_not_in("Course_Classes", "class_id", keep_class_ids)
            self.delete_not_in("Students", "student_id", keep_stu_ids)
            self.delete_not_in("Lecturers", "lecturer_id", keep_lec_ids)
            self.delete_not_in("Courses", "course_id", keep_course_ids)
            self.delete_not_in("Semesters", "semester_id", keep_sem_ids)
            self.delete_not_in("Users", "user_id", keep_user_ids)
            
            print("🎉 XONG! Database đã được thu gọn để demo.")
            print(f"📝 Users test gốc vẫn còn: {self.keep_usernames}")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    cleaner = DatabaseCleaner()
    cleaner.cleanup()