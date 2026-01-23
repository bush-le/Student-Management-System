from database.repositories.student_repo import StudentRepository
from database.repositories.class_repo import ClassRepository
from database.repositories.grade_repo import GradeRepository
from database.repositories.announcement_repo import AnnouncementRepository
from database.repositories.semester_repo import SemesterRepository
from utils.validators import Validators
from datetime import datetime

class StudentController:
    # Constants for GPA calculation
    GPA_POINT_MAP = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
    DEFAULT_CREDITS = 3

    def __init__(self, user_id):
        self.user_id = user_id
        
        # OPTIMIZATION: Lazy load repositories.
        # Initialize as None to avoid DB connection overhead during startup.
        self._student_repo = None
        self._class_repo = None
        self._grade_repo = None
        self._ann_repo = None
        self._semester_repo = None
        
        # OPTIMIZATION: Use Lazy Loading. Student data is fetched only when needed via _ensure_student_loaded
        self.current_student = None
        
        # OPTIMIZATION: Cache expensive data to avoid re-fetching/re-calculating in the same request
        self._grade_data_cache = None
        self._schedule_cache = None

    @property
    def student_repo(self):
        if self._student_repo is None: self._student_repo = StudentRepository()
        return self._student_repo

    @property
    def class_repo(self):
        if self._class_repo is None: self._class_repo = ClassRepository()
        return self._class_repo

    @property
    def grade_repo(self):
        if self._grade_repo is None: self._grade_repo = GradeRepository()
        return self._grade_repo

    @property
    def ann_repo(self):
        if self._ann_repo is None: self._ann_repo = AnnouncementRepository()
        return self._ann_repo

    @property
    def semester_repo(self):
        if self._semester_repo is None: self._semester_repo = SemesterRepository()
        return self._semester_repo

    def _ensure_student_loaded(self):
        """Helper to lazy load student data only when needed"""
        if self.current_student is None:
            self.current_student = self.student_repo.get_by_user_id(self.user_id)

    def view_profile(self):
        """
        FR-05: View Personal Information
        Returns: Student Object
        """
        self._ensure_student_loaded()
        return self.current_student

    def update_contact_info(self, email, phone, address, dob=None):
        """
        FR-06: Update Personal Information
        """
        self._ensure_student_loaded()
        if not self.current_student:
            return False, "Student profile not found."

        # OPTIMIZATION: Sanitize inputs to remove accidental whitespace
        email = email.strip()
        phone = phone.strip()
        address = address.strip()

        # OPTIMIZATION: Dirty Check - Check if data actually changed to avoid unnecessary DB write
        current_address = getattr(self.current_student, 'address', '')
        current_dob = self.current_student.dob
        
        if (self.current_student.email == email and 
            self.current_student.phone == phone and 
            current_address == address and
            (dob is None or current_dob == dob)):
            return True, "No changes made."

        if not Validators.is_valid_email(email):
            return False, "Invalid email format."
            
        if not Validators.is_valid_phone(phone):
            return False, "Invalid phone number format."

        # Update data in the current Object
        self.current_student.email = email # Update student's email
        self.current_student.phone = phone
        
        # Lưu ý: Model Student cần có thuộc tính address
        if hasattr(self.current_student, 'address'):
            self.current_student.address = address
            
        # Update DOB if provided
        if dob:
            self.current_student.dob = dob

        # Call Repo to save to DB
        result = self.student_repo.update_contact_info(self.current_student)
        
        # OPTIMIZATION: Data Consistency
        # If update failed, invalidate local object to force reload from DB next time.
        success = result[0] if isinstance(result, tuple) else result
        if not success:
            self.current_student = None
            
        return result

    def view_schedule(self, force_update=False):
        """
        FR-07: View Weekly Schedule
        """
        if not force_update and self._schedule_cache is not None:
            return self._schedule_cache

        self._ensure_student_loaded()
        if not self.current_student: return []
        
        self._schedule_cache = self.class_repo.get_schedule_by_student(self.current_student.student_id)
        return self._schedule_cache

    def view_grades(self, force_update=False):
        """
        FR-08: View Academic Results
        """
        if not force_update and self._grade_data_cache:
            return self._grade_data_cache

        self._ensure_student_loaded()
        if not self.current_student: 
            return {'transcript': [], 'cumulative_gpa': 0.0, 'earned_credits': 0}
            
        grades = self.grade_repo.get_by_student(self.current_student.student_id)
        
        # Calculate cumulative GPA (Optional - Business logic)
        total_points = 0
        total_credits_attempted = 0
        total_credits_earned = 0

        for g in grades: # Iterate through grades
            # Assume Grade model has joined credits
            cred = getattr(g, 'credits', self.DEFAULT_CREDITS)
            
            if g.letter_grade:
                if g.letter_grade in self.GPA_POINT_MAP:
                    total_points += self.GPA_POINT_MAP.get(g.letter_grade, 0) * cred
                    total_credits_attempted += cred
                
                # Calculate Earned Credits (exclude F)
                if g.letter_grade != 'F':
                    total_credits_earned += cred
        
        gpa = round(total_points / total_credits_attempted, 2) if total_credits_attempted > 0 else 0.0
        
        self._grade_data_cache = {
            "transcript": grades,
            "cumulative_gpa": gpa,
            "earned_credits": total_credits_earned
        }
        
        return self._grade_data_cache

    # --- For DASHBOARD ---
    def get_upcoming_class(self):
        """Retrieves the upcoming class for the Student Dashboard"""
        schedule = self.view_schedule()
        if not schedule: return None
        
        now = datetime.now()
        # Map python weekday (0=Mon) to strings used in DB/Schedule
        days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        today_str = days_map[now.weekday()]
        
        # 1. Filter classes for today
        todays_classes = [cls for cls in schedule if cls.get('schedule') and today_str in cls.get('schedule', '').lower()]
        
        if not todays_classes:
            # Fallback: Return the first class in the list (e.g. Monday morning)
            return schedule[0]

        # 2. Helper to parse start and end time
        def parse_times(cls_obj):
            try:
                # "monday 07:00-09:00" -> remove "monday" -> " 07:00-09:00"
                txt = cls_obj.get('schedule', '').lower().replace(today_str, "").strip()
                parts = txt.split('-')
                start_str = parts[0].strip()
                
                h, m = map(int, start_str.split(':'))
                start_mins = h * 60 + m
                
                # Try to parse end time, default to +120 mins if missing
                end_mins = start_mins + 120
                if len(parts) > 1:
                    end_str = parts[1].strip()
                    if ':' in end_str:
                        eh, em = map(int, end_str.split(':'))
                        end_mins = eh * 60 + em
                
                return start_mins, end_mins
            except:
                return 9999, 9999

        # 3. Find the most relevant class (Current or Next)
        todays_classes.sort(key=lambda x: parse_times(x)[0])
        current_minutes = now.hour * 60 + now.minute
        
        found_class = None
        for cls in todays_classes:
            start, end = parse_times(cls)
            # Show class if it ends in the future (meaning it's current or upcoming)
            if end > current_minutes: 
                found_class = cls
                break
                
        # If all classes today finished, return the last one (to show what was just finished)
        if not found_class and todays_classes:
            found_class = todays_classes[-1]
            
        # Fallback to the first class if no class today
        if not found_class:
            found_class = schedule[0]

        # ENRICHMENT: Add UI status labels (Return a copy to avoid modifying cache)
        if found_class and isinstance(found_class, dict):
            found_class = found_class.copy()
            # Check if it's actually today's class
            if today_str in found_class.get('schedule', '').lower():
                start, end = parse_times(found_class)
                if start <= current_minutes <= end:
                    found_class['ui_status'] = "HAPPENING NOW"
                    found_class['ui_color'] = "#FECACA" # Light Red text for urgency
                else:
                    found_class['ui_status'] = "UPCOMING CLASS"
                    found_class['ui_color'] = "#CCFBF1" # Light Teal
            else:
                found_class['ui_status'] = "NEXT CLASS"
                found_class['ui_color'] = "#CCFBF1"

        return found_class

    def get_academic_stats(self):
        """Retrieves GPA/Credits statistics for the Dashboard"""
        data = self.view_grades()
        
        # Get current semester name
        active_sem = self.semester_repo.get_active()
        sem_name = active_sem.name if active_sem else 'N/A'

        return {
            'gpa': data['cumulative_gpa'],
            'credits': data['earned_credits'],
            'semester': sem_name
        }

    def get_recent_grades(self, limit=3):
        """Retrieves the 3 most recent grades"""
        data = self.view_grades()
        transcript = data['transcript'] # Get transcript from data
        # Assume transcript is sorted or take the last 3
        return transcript[:limit]

    def get_latest_announcements(self, limit=3):
        return self.ann_repo.get_recent(limit)

    def get_dashboard_academic_summary(self):
        """
        OPTIMIZATION: Fetch grades once for both stats and recent list.
        Reduces DB queries by 50% for this section.
        """
        # 1. Fetch all grade data (Single DB Query)
        data = self.view_grades() 
        
        active_sem = self.semester_repo.get_active()
        sem_name = active_sem.name if active_sem else 'N/A'

        stats = {
            'gpa': data['cumulative_gpa'],
            'credits': data['earned_credits'],
            'semester': sem_name
        }

        # 3. Get Recent (Top 3) from cached transcript
        recent = data['transcript'][:3]

        return stats, recent

    def get_all_semesters(self):
        return self.semester_repo.get_all()

    def get_student_profile(self):
        """Retrieves full profile including class, department"""
        # Need repo support for join, temporarily return current object as dict
        self._ensure_student_loaded()
        if not self.current_student: return {}
        return {
            'full_name': self.current_student.full_name,
            'email': self.current_student.email,
            'phone': self.current_student.phone,
            'student_code': self.current_student.student_code,
            'dept_name': getattr(self.current_student, 'dept_name', 'N/A'),
            'class_name': getattr(self.current_student, 'major', 'N/A'), # Using Major as Class/Cohort
            'dob': str(self.current_student.dob) if self.current_student.dob else '',
            'address': getattr(self.current_student, 'address', '')
        }
    
    def update_student_profile(self, user_id, email, phone, address, dob): # Update Profile from View
        """Updates the Profile from the View"""
        return self.update_contact_info(email, phone, address, dob)