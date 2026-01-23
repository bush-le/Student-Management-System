from datetime import datetime
from database.repositories.lecturer_repo import LecturerRepository
from database.repositories.class_repo import ClassRepository
from database.repositories.grade_repo import GradeRepository
from database.repositories.semester_repo import SemesterRepository
from models.academic.grade import Grade
from utils.validators import Validators

class LecturerController:
    def __init__(self, user_id):
        self.user_id = user_id
        
        # OPTIMIZATION: Lazy load repositories
        self._lecturer_repo = None
        self._class_repo = None
        self._grade_repo = None
        self._semester_repo = None
        
        # Load lecturer information immediately upon initialization
        # OPTIMIZATION: Use Lazy Loading to avoid blocking UI during init
        self.current_lecturer = None
        self._schedule_cache = None # Cache for teaching schedule

    @property
    def lecturer_repo(self):
        if self._lecturer_repo is None: self._lecturer_repo = LecturerRepository()
        return self._lecturer_repo

    @property
    def class_repo(self):
        if self._class_repo is None: self._class_repo = ClassRepository()
        return self._class_repo

    @property
    def grade_repo(self):
        if self._grade_repo is None: self._grade_repo = GradeRepository()
        return self._grade_repo

    @property
    def semester_repo(self):
        if self._semester_repo is None: self._semester_repo = SemesterRepository()
        return self._semester_repo

    def _ensure_lecturer_loaded(self):
        if self.current_lecturer is None:
            self.current_lecturer = self.lecturer_repo.get_by_user_id(self.user_id)

    def get_teaching_schedule(self, force_update=False):
        """
        FR-10: View Assigned Schedule
        """
        self._ensure_lecturer_loaded()
        if not self.current_lecturer:
            return []
        
        if not force_update and self._schedule_cache is not None:
            return self._schedule_cache
            
        self._schedule_cache = self.class_repo.get_schedule_by_lecturer(self.current_lecturer.lecturer_id)
        return self._schedule_cache

    def get_class_student_list(self, class_id):
        """
        FR-11: View Student List # FR-11: View Student List
        """
        # Reuse existing function in GradeRepo
        return self.grade_repo.get_by_class(class_id)

    def get_upcoming_teaching_class(self):
        """Get upcoming class"""
        self._ensure_lecturer_loaded()
        if not self.current_lecturer:
            return None
        
        schedule = self.get_teaching_schedule(force_update=False)
        if not schedule:
            return None
        
        # Get the first class (requires more complex logic for real-time filtering)
        return schedule[0] if schedule else None

    def get_teaching_stats(self):
        """Get teaching statistics"""
        self._ensure_lecturer_loaded()
        if not self.current_lecturer:
            return {'total_students': 0, 'total_classes': 0}
        
        schedule = self.get_teaching_schedule(force_update=False)
        
        total_classes = len(schedule)
        total_students = sum(s.get('enrolled_count', 0) for s in schedule)
        
        return {
            'total_classes': total_classes,
            'total_students': total_students
        }

    def input_grade(self, student_id, class_id, attendance, midterm, final):
        """
        FR-12 & FR-13: Enter/Update Grades
        """
        # Validate inputs # Validate inputs
        if not (Validators.is_valid_grade(attendance) and Validators.is_valid_grade(midterm) and Validators.is_valid_grade(final)):
             return False, "Grades must be between 0.0 and 10.0"

        # --- UC13: Check Semester Status & Date ---
        cls_info = self.class_repo.get_by_id(class_id)
        if cls_info:
            sem = self.semester_repo.get_by_id(cls_info.semester_id)
            if sem:
                # AF1.1: Check if semester is active
                if sem.status == 'CLOSED':
                    return False, "Grade update period has expired (Semester Closed)."
                
                # AF1.1: Check if date passed
                if sem.end_date:
                    end_date = sem.end_date
                    if isinstance(end_date, str):
                        try:
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                    
                    # Compare if end_date is valid date object
                    if hasattr(end_date, 'year') and datetime.now().date() > end_date:
                        return False, "Grade update period has expired (Date passed)."

        # 1. Find corresponding grade_id
        grade_id = self.grade_repo.get_id_by_enrollment(student_id, class_id)
        
        if not grade_id:
            return False, "Enrollment record not found."

        # 2. Create Grade object with new data
        # Note: No need to calculate total/letter here, GradeRepo.update_scores will automatically call the model to calculate
        grade_obj = Grade(
            grade_id=grade_id,
            student_id=student_id,
            class_id=class_id,
            attendance_score=attendance,
            midterm=midterm,
            final=final,
            total=0,       # Will be recalculated in Repo
            letter_grade="" # Will be recalculated in Repo
        )

        # 3. Call Repo to update
        # Repo will automatically check is_locked and return an error if grades are locked for the class
        return self.grade_repo.update_scores(grade_obj)

    def update_class_grades(self, class_id, grades_data):
        """
        OPTIMIZATION: Bulk update grades to reduce DB calls.
        grades_data: list of tuples (student_id, attendance, midterm, final)
        """
        # 1. Validate Semester Status ONCE for the whole batch
        cls_info = self.class_repo.get_by_id(class_id)
        if cls_info:
            sem = self.semester_repo.get_by_id(cls_info.semester_id)
            if sem:
                if sem.status == 'CLOSED':
                    return False, "Grade update period has expired (Semester Closed)."
                
                if sem.end_date:
                    end_date = sem.end_date
                    if isinstance(end_date, str):
                        try:
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                    
                    if hasattr(end_date, 'year') and datetime.now().date() > end_date:
                        return False, "Grade update period has expired (Date passed)."

        # 2. Process Updates
        
        # OPTIMIZATION: Fetch all grade IDs for this class once to avoid N queries inside loop
        # This reduces complexity from O(N) DB queries to O(1) DB query for lookups
        class_grades = self.grade_repo.get_by_class(class_id)
        grade_map = {} # Map student_id -> grade_id
        if class_grades:
            for g in class_grades:
                # Handle dictionary or object return type safely
                sid = g.get('student_id') if isinstance(g, dict) else getattr(g, 'student_id', None)
                gid = g.get('grade_id') if isinstance(g, dict) else getattr(g, 'grade_id', None)
                if sid and gid:
                    grade_map[sid] = gid

        success_count = 0
        
        for sid, att, mid, fin in grades_data:
            # Validate inputs locally
            if not (Validators.is_valid_grade(att) and Validators.is_valid_grade(mid) and Validators.is_valid_grade(fin)):
                 continue

            # Find grade_id from map (Memory lookup instead of DB query)
            grade_id = grade_map.get(sid)
            if not grade_id:
                continue
                
            grade_obj = Grade(
                grade_id=grade_id, student_id=sid, class_id=class_id,
                attendance_score=att, midterm=mid, final=fin,
                total=0, letter_grade=""
            )
            if self.grade_repo.update_scores(grade_obj):
                success_count += 1
                
        return True, f"Successfully saved grades for {success_count} students."

    def get_dashboard_summary(self):
        """
        OPTIMIZATION: Fetch schedule once for both upcoming class and stats.
        """
        self._ensure_lecturer_loaded()
        if not self.current_lecturer:
            return None, {'total_classes': 0, 'total_students': 0}

        # 1. Fetch Schedule (Use Cache if available)
        schedule = self.get_teaching_schedule(force_update=False)
        
        # 2. Process Upcoming Class
        upcoming = None
        if schedule:
            now = datetime.now()
            days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            today_str = days_map[now.weekday()]
            
            # Filter today's classes
            todays_classes = [c for c in schedule if c.get('schedule') and today_str in c.get('schedule', '').lower()]
            
            def parse_times(cls_obj):
                try:
                    txt = cls_obj.get('schedule', '').lower().replace(today_str, "").strip()
                    parts = txt.split('-')
                    start_str = parts[0].strip()
                    h, m = map(int, start_str.split(':'))
                    start_mins = h * 60 + m
                    end_mins = start_mins + 120
                    if len(parts) > 1:
                        end_str = parts[1].strip()
                        if ':' in end_str:
                            eh, em = map(int, end_str.split(':'))
                            end_mins = eh * 60 + em
                    return start_mins, end_mins
                except: return 9999, 9999

            if todays_classes:
                todays_classes.sort(key=lambda x: parse_times(x)[0])
                current_minutes = now.hour * 60 + now.minute
                for cls in todays_classes:
                    start, end = parse_times(cls)
                    if end > current_minutes:
                        upcoming = cls; break
                if not upcoming: upcoming = todays_classes[-1]
            else:
                upcoming = schedule[0]

        # ENRICHMENT: Add UI status labels (Return a copy to avoid modifying cache if we add caching later)
        if upcoming and isinstance(upcoming, dict):
            upcoming = upcoming.copy()
            # Check if it's actually today's class
            if today_str in upcoming.get('schedule', '').lower():
                start, end = parse_times(upcoming)
                current_minutes = now.hour * 60 + now.minute
                if start <= current_minutes <= end:
                    upcoming['ui_status'] = "HAPPENING NOW"
                    upcoming['ui_color'] = "#FECACA" # Light Red
                else:
                    upcoming['ui_status'] = "UPCOMING CLASS"
                    upcoming['ui_color'] = "#CCFBF1" # Light Teal
            else:
                upcoming['ui_status'] = "NEXT CLASS"
                upcoming['ui_color'] = "#CCFBF1"
        
        # 3. Process Stats (Deduplicate classes to avoid double counting students/classes)
        # Schedule might contain multiple slots for the same class_id
        unique_classes = {s.get('class_id'): s for s in schedule if s.get('class_id')}.values()
        
        total_classes = len(unique_classes)
        total_students = sum(s.get('enrolled_count', 0) for s in unique_classes)
        
        stats = {
            'total_classes': total_classes,
            'total_students': total_students
        }
        
        return upcoming, stats