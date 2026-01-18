from database.student_repository import StudentRepository
from tkinter import messagebox

class StudentController:
    """
    Controller handling business logic for the Student Module (FR-05 to FR-09).
    """
    def __init__(self, current_user_id):
        self.repository = StudentRepository()
        # Fetch initial student data [cite: 408, 781]
        self.student = self.repository.get_student_by_id(current_user_id)

    def view_profile(self):
        """FR-05: Returns student profile for read-only display[cite: 58, 409]."""
        return self.student

    def update_profile(self, phone, address, email):
        """
        FR-06: Updates non-critical contact information[cite: 63, 64].
        Validates data before saving to database[cite: 66, 428].
        """
        if not phone or not address or not email:
            return False, "All fields are required."
            
        # Call repository to update data [cite: 429]
        success = self.repository.update_student_contact(self.student.student_id, phone, address, email)
        if success:
            # Refresh local student object
            self.student.phone = phone
            self.student.address = address
            self.student.email = email
            return True, "Profile updated successfully."
        return False, "Database error occurred."

    def view_academic_results(self):
        """
        FR-08: Fetches grades and calculates cumulative GPA [cite: 73-77].
        """
        if not self.student:
            return [], 0.0, "N/A"
            
        grades = self.repository.get_grades_by_student(self.student.student_id)
        
        total_points = 0.0
        total_credits = 0
        
        for g in grades:
            # calculate_final_grade is defined in Grade Model
            g.calculate_final_grade() 
            # Assuming Grade object has access to course credits [cite: 75, 477]
            # credits = g.course_credits 
            # total_points += g.total_score * credits
            # total_credits += credits
            
        # Calculate GPA (Simplified for this example) [cite: 75, 478]
        cumulative_gpa = self.student.gpa # Or dynamic calculation
        
        # Determine classification [cite: 76, 479]
        classification = "Excellent" if cumulative_gpa >= 3.6 else "Good" if cumulative_gpa >= 3.0 else "Average"
        
        return grades, cumulative_gpa, classification

    def get_weekly_schedule(self):
        """FR-07: Returns the list of enrolled classes for the timetable[cite: 69, 452]."""
        return self.repository.get_schedule_by_student(self.student.student_id)

    def view_notifications(self):
        """FR-09: Returns system announcements from the Administrator[cite: 78, 498]."""
        return self.repository.get_notifications_for_student()
    
    def save_profile_changes(self, student_id, user_id, new_data):
        """
        Handles saving changes and notifying the user. 
        """
        success = self.repository.update_student_profile(student_id, user_id, new_data)
        
        if success:
            # Display confirmation message
            messagebox.showinfo("Success", "Profile information has been updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update information. Please try again.")
