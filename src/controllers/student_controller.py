from database.student_repository import StudentRepository
from utils.validators import validate_email, validate_phone 

class StudentController:
    """
    Controller handling business logic for the Student Module (FR-05 to FR-09).
    This class acts as a bridge between the View and the Data Repository.
    """
    def __init__(self, current_user_id):
        self.repository = StudentRepository()
        # Fetch initial student data based on logged-in User ID  
        self.student = self.repository.get_student_by_id(current_user_id)

    def view_profile(self):
        """
        FR-05: Returns the student profile object.
        The View will handle displaying specific fields in read-only mode [cite: 58-62].
        """
        return self.student

    def update_profile(self, phone, address, email):
        """
        FR-06: Updates non-critical contact information.
        Separates business logic from UI by returning status and messages [cite: 63-68].
        """
        # 1. Basic validation for empty fields
        if not all([phone, address, email]):
            return False, "All contact fields are required."

        # 2. Data format validation as required by FR-06 
        if not validate_email(email):
            return False, "Invalid email format. Please try again."
        
        if not validate_phone(phone):
            return False, "Invalid phone number length or format."

        # 3. Call repository to update data
        success = self.repository.update_student_contact(self.student.student_id, phone, address, email)
        
        if success:
            # 4. Record action for audit purposes as required by FR-06
            self.repository.log_audit_action(self.student.student_id, "Update Personal Information")
            
            # Update local state
            self.student.phone = phone
            self.student.address = address
            self.student.email = email
            return True, "Profile updated successfully."
            
        return False, "A database error occurred while saving changes."

    def view_academic_results(self):
        """
        FR-08: Fetches grades and calculates cumulative GPA performance.
        """
        if not self.student:
            return None, 0.0, "N/A"
            
        # Get all grade records for the student 
        grades = self.repository.get_grades_by_student(self.student.student_id)
        
        # In a real scenario, calculation logic might reside in the Grade Model
        # This controller summarizes it for the View 
        current_gpa = self.student.gpa 
        
        # Classification rules based on GPA 
        if current_gpa >= 3.6:
            classification = "Excellent"
        elif current_gpa >= 3.2:
            classification = "Very Good"
        elif current_gpa >= 2.5:
            classification = "Good"
        else:
            classification = "Average"
            
        return grades, current_gpa, classification

    def get_weekly_schedule(self):
        """
        FR-07: Retrieves the list of enrolled classes for the visual timetable.
        """
        return self.repository.get_schedule_by_student(self.student.student_id)

    def view_notifications(self):
        """
        FR-09: Retrieves system alerts and announcements for the dashboard.
        """
        notifications = self.repository.get_notifications_for_student()
        # Mark as read after retrieval if necessary
        return notifications
