import customtkinter as ctk
from views.auth.login_window import LoginView
from views.student.dashboard import StudentDashboard
from views.lecturer.dashboard import LecturerDashboard
from views.admin.dashboard import AdminDashboard

class RootApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("Light")
        super().__init__()
        self.title("Student Management System")
        self.geometry("1200x700")
        
        self.current_frame = None
        self.show_login()

    def clear_window(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        self.clear_window()
        self.current_frame = LoginView(self, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self, user):
        self.clear_window()
        
        if user.role == "Student":
            self.current_frame = StudentDashboard(self, self, user)
        elif user.role == "Lecturer":
            self.current_frame = LecturerDashboard(self, self, user)
        elif user.role == "Admin":
            self.current_frame = AdminDashboard(self, self, user)
            
        if self.current_frame:
            self.current_frame.pack(fill="both", expand=True)

    def on_login_success(self, user):
        """
        user: Là Object User (src.models.user.User)
        """
        self.current_user = user
        # self.login_window might not be set if show_login creates LoginView directly into self.current_frame
        # Assuming show_dashboard handles the clearing and setting of the main view
        
        # Điều hướng dựa trên user.role (Object attribute)
        if user.role == 'Admin':
            from views.admin.dashboard import AdminDashboard
            # Truyền user object vào dashboard
            self.current_frame = AdminDashboard(self, self, user) 
            
        elif user.role == 'Student':
            from views.student.dashboard import StudentDashboard
            # StudentDashboard thường cần user_id để load data
            self.current_frame = StudentDashboard(self, self, user) 
            
        elif user.role == 'Lecturer':
            from views.lecturer.dashboard import LecturerDashboard
            self.current_frame = LecturerDashboard(self, self, user)

        if self.current_frame:
            self.current_frame.pack(fill="both", expand=True)