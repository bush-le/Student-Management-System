import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Thêm đường dẫn root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.database.connection import DatabaseConnection
from src.utils.security import Security

class DataSeeder:
    def __init__(self):
        self.conn = DatabaseConnection.get_connection()
        self.cursor = self.conn.cursor(dictionary=True)
        # Mật khẩu mặc định: Test123!
        self.common_pass = Security.hash_password("Test123!")
        # Init Faker English
        self.fake = Faker('en_US')

    def update_schema(self):
        print("🛠 Checking schema updates...")
        try:
            self.cursor.execute("SHOW COLUMNS FROM Announcements LIKE 'user_id'")
            if not self.cursor.fetchone():
                print("   -> Adding 'user_id' column to Announcements...")
                self.cursor.execute("ALTER TABLE Announcements ADD COLUMN user_id INT NULL AFTER officer_id")
                self.cursor.execute("ALTER TABLE Announcements ADD CONSTRAINT fk_ann_user FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE")
                self.cursor.execute("ALTER TABLE Announcements MODIFY COLUMN officer_id INT NULL")
                self.conn.commit()
        except Exception as e:
            print(f"   ⚠️ Schema update skipped: {e}")

    def clean_db(self):
        print("🧹 Cleaning old data (TRUNCATE)...")
        tables = [
            "Announcements", "Grades", "Course_Classes", 
            "Courses", "Semesters", "Students", "Lecturers", 
            "Academic_Officers", "Departments", "Users"
        ]
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for t in tables:
            try:
                self.cursor.execute(f"SHOW TABLES LIKE '{t}'")
                if self.cursor.fetchone():
                    self.cursor.execute(f"TRUNCATE TABLE {t};")
            except: pass
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        self.conn.commit()

    def seed_data(self):
        print("🌱 Starting data seeding (Dynamic Date)...")

        # ==========================================
        # 1. DEPARTMENTS
        # ==========================================
        print("   -> 1. Creating Departments...")
        depts = [
            ("Information Technology", "Building C"),
            ("Electrical & Electronics", "Building B"),
            ("Transport Economics", "Building E"),
            ("Mechanical Engineering", "Building A"),
            ("Civil Engineering", "Building D")
        ]
        self.cursor.executemany("INSERT INTO Departments (dept_name, office_location) VALUES (%s, %s)", depts)
        
        # Fetch Dept IDs
        self.cursor.execute("SELECT dept_id FROM Departments")
        dept_ids = [row['dept_id'] for row in self.cursor.fetchall()]

        # ==========================================
        # 2. SEMESTERS - DYNAMIC SYSTEM TIME
        # ==========================================
        print("   -> 2. Creating Semesters (Based on current date)...")
        today = datetime.now()
        
        past_start = (today - timedelta(days=150)).strftime('%Y-%m-%d')
        past_end = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        curr_start = (today - timedelta(days=10)).strftime('%Y-%m-%d')
        curr_end = (today + timedelta(days=120)).strftime('%Y-%m-%d')
        
        fut_start = (today + timedelta(days=130)).strftime('%Y-%m-%d')
        fut_end = (today + timedelta(days=250)).strftime('%Y-%m-%d')

        sems = [
            ("Fall 2024 (Past)", past_start, past_end, "CLOSED"),
            ("Spring 2025 (Current)", curr_start, curr_end, "OPEN"),
            ("Summer 2025 (Upcoming)", fut_start, fut_end, "OPEN")
        ]
        self.cursor.executemany("INSERT INTO Semesters (name, start_date, end_date, status) VALUES (%s, %s, %s, %s)", sems)
        
        self.cursor.execute("SELECT semester_id FROM Semesters WHERE name LIKE '%Past%'")
        sem_closed_id = self.cursor.fetchone()['semester_id']
        
        self.cursor.execute("SELECT semester_id FROM Semesters WHERE name LIKE '%Current%'")
        sem_open_id = self.cursor.fetchone()['semester_id']

        # ==========================================
        # 3. COURSES
        # ==========================================
        print("   -> 3. Creating Courses...")
        base_courses = [
            ("CS101", "Intro to Programming", 3), ("MATH1", "Calculus A1", 3),
            ("ENG01", "English 1", 2), ("PHY01", "General Physics", 3),
            ("MAR01", "Philosophy", 2), ("EE101", "Electric Circuits", 3)
        ]
        for c, n, cr in base_courses:
            self.cursor.execute(
                "INSERT INTO Courses (course_code, dept_id, course_name, credits, description, prerequisite_id) VALUES (%s, %s, %s, %s, %s, NULL)",
                (c, random.choice(dept_ids), n, cr, self.fake.sentence())
            )
        
        self.cursor.execute("SELECT course_id FROM Courses WHERE course_code='CS101'")
        id_cs101 = self.cursor.fetchone()['course_id']

        adv_courses = [
            ("CS201", "Data Structures", 4, id_cs101), ("SOFT1", "Software Engineering", 3, id_cs101),
            ("WEB1", "Web Development", 3, id_cs101), ("DB101", "Database Systems", 3, id_cs101),
            ("AI101", "Artificial Intelligence", 3, None), ("NET1", "Computer Networks", 3, None)
        ]
        for c, n, cr, pre in adv_courses:
            self.cursor.execute(
                "INSERT INTO Courses (course_code, dept_id, course_name, credits, description, prerequisite_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (c, random.choice(dept_ids), n, cr, self.fake.sentence(), pre)
            )
        
        self.cursor.execute("SELECT course_id FROM Courses")
        all_course_ids = [r['course_id'] for r in self.cursor.fetchall()]

        # ==========================================
        # 4. USERS (Users creation)
        # ==========================================
        print("   -> 4. Creating Users...")

        def create_user_db(username, email, name, role):
            phone = f"09{self.fake.random_number(digits=8)}"
            dob = self.fake.date_of_birth(minimum_age=18, maximum_age=55)
            addr = self.fake.address().replace('\n', ', ')
            self.cursor.execute(
                """INSERT INTO Users (username, password, full_name, email, phone, role, status, address, dob) 
                   VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE', %s, %s)""",
                (username, self.common_pass, name, email, phone, role, addr, dob)
            )
            return self.cursor.lastrowid

        # 4.1 ADMIN
        uid_admin = create_user_db("admin", "admin@uth.edu.vn", "System Admin", "Admin")
        self.cursor.execute("INSERT INTO Academic_Officers (user_id, admin_code) VALUES (%s, 'ADM01')", (uid_admin,))
        officer_id = self.cursor.lastrowid

        # 4.2 LECTURERS
        lecturer_ids = []
        uid_l_main = create_user_db("lecturer", "lecturer@test.com", "Dr. Sarah Jones", "Lecturer")
        self.cursor.execute("INSERT INTO Lecturers (user_id, dept_id, lecturer_code, degree) VALUES (%s, %s, 'L001', 'PhD')", (uid_l_main, dept_ids[0]))
        lecturer_ids.append(self.cursor.lastrowid)
        lid_main = self.cursor.lastrowid

        for i in range(2, 21):
            name = self.fake.name()
            uname = f"lec{i:02d}"
            uid = create_user_db(uname, f"{uname}@uth.edu.vn", f"Prof. {name}", "Lecturer")
            self.cursor.execute("INSERT INTO Lecturers (user_id, dept_id, lecturer_code, degree) VALUES (%s, %s, %s, 'Master')", 
                                (uid, random.choice(dept_ids), f"L{i:03d}"))
            lecturer_ids.append(self.cursor.lastrowid)

        # 4.3 STUDENTS
        student_ids = []

        # Student 1: Main Demo
        uid_s_main = create_user_db("student", "student@test.com", "Le Hoang Tuan", "Student")
        self.cursor.execute("INSERT INTO Students (user_id, dept_id, student_code, major, academic_year) VALUES (%s, %s, '211101', 'Software Eng', 2024)", (uid_s_main, dept_ids[0]))
        student_ids.append(self.cursor.lastrowid)
        sid_main = self.cursor.lastrowid

        # Student 2: Forgot Password Demo (Requested)
        uid_s_forgot = create_user_db("nguyenvana", "", "Nguyen Van A", "Student")
        self.cursor.execute("INSERT INTO Students (user_id, dept_id, student_code, major, academic_year) VALUES (%s, %s, '211102', 'IT', 2024)", (uid_s_forgot, dept_ids[0]))
        student_ids.append(self.cursor.lastrowid)

        # Random Students (Increased to ~50 total)
        for i in range(3, 51):
            name = self.fake.name()
            uname = f"stu{i:02d}"
            uid = create_user_db(uname, f"{uname}@uth.edu.vn", name, "Student")
            self.cursor.execute("INSERT INTO Students (user_id, dept_id, student_code, major, academic_year) VALUES (%s, %s, %s, 'IT', 2024)", 
                                (uid, random.choice(dept_ids), f"2111{i:02d}"))
            student_ids.append(self.cursor.lastrowid)

        # ==========================================
        # 5. CLASSES & SCHEDULE
        # ==========================================
        print("   -> 5. Creating Classes & Schedules...")
        
        slots = [
            "Monday 07:00-09:30", "Monday 13:00-15:30",
            "Tuesday 07:00-09:30", "Tuesday 13:00-15:30",
            "Wednesday 07:00-09:30", "Wednesday 13:00-15:30",
            "Thursday 07:00-09:30", "Thursday 13:00-15:30",
            "Friday 07:00-09:30", "Friday 13:00-15:30"
        ]
        
        class_ids_open = []
        class_ids_closed = []

        # Past Semester Classes
        for i in range(20):
            course = random.choice(all_course_ids)
            lecturer = random.choice(lecturer_ids)
            self.cursor.execute(
                "INSERT INTO Course_Classes (course_id, semester_id, lecturer_id, room, schedule, max_capacity) VALUES (%s, %s, %s, %s, %s, 50)",
                (course, sem_closed_id, lecturer, f"OLD-{i}", random.choice(slots))
            )
            class_ids_closed.append(self.cursor.lastrowid)

        # Current Semester Classes (Main Lecturer has specific schedule)
        my_slots = ["Monday 07:00-09:30", "Wednesday 13:00-15:30"] 
        for i, slot in enumerate(my_slots):
            course = random.choice(all_course_ids)
            self.cursor.execute(
                "INSERT INTO Course_Classes (course_id, semester_id, lecturer_id, room, schedule, max_capacity) VALUES (%s, %s, %s, %s, %s, 50)",
                (course, sem_open_id, lid_main, f"MY-ROOM-{i}", slot)
            )
            class_ids_open.append(self.cursor.lastrowid)

        # Random classes
        for i in range(20):
            course = random.choice(all_course_ids)
            lecturer = random.choice(lecturer_ids)
            self.cursor.execute(
                "INSERT INTO Course_Classes (course_id, semester_id, lecturer_id, room, schedule, max_capacity) VALUES (%s, %s, %s, %s, %s, 50)",
                (course, sem_open_id, lecturer, f"NEW-{i}", random.choice(slots))
            )
            class_ids_open.append(self.cursor.lastrowid)

        # ==========================================
        # 6. ENROLLMENTS & GRADES
        # ==========================================
        print("   -> 6. Enrolling Students & Grading...")

        # 6.1 Main Student
        my_classes = random.sample(class_ids_open, 3) 
        for cid in my_classes:
            self.cursor.execute("INSERT INTO Grades (student_id, class_id, is_locked) VALUES (%s, %s, 0)", (sid_main, cid))
        
        old_classes = random.sample(class_ids_closed, 3)
        for cid in old_classes:
            final = random.randint(5, 10)
            self.cursor.execute(
                "INSERT INTO Grades (student_id, class_id, attendance_score, midterm, final, total, letter_grade, is_locked) VALUES (%s, %s, 10, %s, %s, %s, 'A', 1)",
                (sid_main, cid, final, final, final)
            )

        # 6.2 Other Students (Include the Forgot Password user)
        for sid in student_ids:
            if sid == sid_main: continue 
            k = random.randint(2, 4)
            for cid in random.sample(class_ids_open, k):
                self.cursor.execute("INSERT INTO Grades (student_id, class_id, is_locked) VALUES (%s, %s, 0)", (sid, cid))

        # ==========================================
        # 7. ANNOUNCEMENTS
        # ==========================================
        print("   -> 7. Posting Announcements...")
        anns = [
            ("Lunar New Year Holiday", f"School closed from {today.strftime('%d/%m')} to {(today+timedelta(days=20)).strftime('%d/%m')}."),
            ("Course Registration Open", "Registration for Summer Semester opens tomorrow."),
            ("Tuition Fee Deadline", "Please pay your tuition fees before the final exams.")
        ]
        for t, c in anns:
            self.cursor.execute("INSERT INTO Announcements (officer_id, title, content, created_date) VALUES (%s, %s, %s, NOW())", (officer_id, t, c))

        # ==========================================
        # 8. UPDATE METADATA
        # ==========================================
        print("   -> 8. Updating Class Enrollment Counts...")
        try:
            self.cursor.execute("UPDATE Course_Classes c SET current_enrolled = (SELECT COUNT(*) FROM Grades g WHERE g.class_id = c.class_id)")
        except Exception:
            print("      ⚠️ Skipped updating current_enrolled (Column might not exist or is calculated dynamically)")

        self.conn.commit()
        
        print("\n✅ SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("DEMO ACCOUNTS (Password: Test123!)")
        print("-" * 60)
        print("1. [STUDENT]  student@test.com")
        print("   -> Features: Current Schedule, Past Transcript")
        print("2. [LECTURER] lecturer@test.com")
        print("   -> Features: Class Management (Mon 7:00, Wed 13:00)")
        print("3. [ADMIN]    admin@uth.edu.vn")
        print("4. [STUDENT]  tidk54737@gmail.com")
        print("   -> Feature: Forgot Password Demo")
        print("="*60)

if __name__ == "__main__":
    try:
        seeder = DataSeeder()
        seeder.update_schema() # Cập nhật bảng trước khi seed
        seeder.clean_db()
        seeder.seed_data()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")