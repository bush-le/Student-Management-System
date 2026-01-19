import customtkinter as ctk
from views.auth.login_window import LoginView
from views.student.dashboard import StudentDashboard

class RootApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Student Management System - Group 01")
        self.geometry("1280x720")
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # Start with Login screen
        self.show_login()

    def show_login(self):
        self._clear_frame()
        login_screen = LoginView(self.container, self)
        login_screen.pack(fill="both", expand=True)

    def show_student_dashboard(self, user):
        self._clear_frame()
        # Pass user object to dashboard
        dashboard = StudentDashboard(self.container, self, user)
        dashboard.pack(fill="both", expand=True)

    def _clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()