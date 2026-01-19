from datetime import datetime

class Grade:
    """
    Grade class managing scores.
    Contains business logic for calculating Total Score and Letter Grade.
    """
    def __init__(self, grade_id, student_id, class_id, attendance, midterm, final, total=None, letter=None, is_locked=False):
        self.grade_id = grade_id
        self.student_id = student_id
        self.class_id = class_id
        
        # Convert to float, default is 0.0 if None
        self.attendance_score = float(attendance) if attendance is not None else 0.0
        self.midterm_score = float(midterm) if midterm is not None else 0.0
        self.final_score = float(final) if final is not None else 0.0
        
        # If total exists from DB, use it; otherwise, recalculate
        self.total_score = float(total) if total is not None else self.calculate_total()
        self.letter_grade = letter if letter else self.convert_to_letter()
        
        self.is_locked = bool(is_locked)
        self.updated_at = datetime.now()

    def calculate_total(self):
        """
        FR-12: Calculate total score based on weights.
        Attendance: 10%, Midterm: 30%, Final: 60%.
        """
        self.total_score = (self.attendance_score * 0.1) + \
                           (self.midterm_score * 0.3) + \
                           (self.final_score * 0.6)
        # Round to 2 decimal places
        self.total_score = round(self.total_score, 2)
        self.convert_to_letter()
        return self.total_score

    def convert_to_letter(self):
        """
        Convert score to letter grade (4.0 scale or ABC).
        Assumption based on common grading scale (can be adjusted per school regulations).
        """
        if self.total_score >= 8.5: self.letter_grade = "A"
        elif self.total_score >= 7.0: self.letter_grade = "B"
        elif self.total_score >= 5.5: self.letter_grade = "C"
        elif self.total_score >= 4.0: self.letter_grade = "D"
        else: self.letter_grade = "F"
        return self.letter_grade