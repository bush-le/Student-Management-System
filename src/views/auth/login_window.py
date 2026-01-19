import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.auth_controller = AuthController()

        # Layout 2 cột: Trái (Logo/Art) - Phải (Form)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- CỘT TRÁI ---
        self.left_frame = ctk.CTkFrame(self, fg_color="#2A9D8F", corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        
        ctk.CTkLabel(
            self.left_frame, 
            text="Student\nManagement\nSystem",
            font=("Arial", 32, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # --- CỘT PHẢI ---
        self.right_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        self.form_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.form_frame, text="Welcome Back", 
            font=("Arial", 26, "bold"), text_color="#333"
        ).pack(pady=(0, 10))

        self.email_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Password", show="*", width=300, height=40)
        self.pass_entry.pack(pady=10)

        # Login Button
        ctk.CTkButton(
            self.form_frame, text="Sign In", width=300, height=40,
            fg_color="#2A9D8F", hover_color="#21867a",
            command=self.handle_login
        ).pack(pady=20)

        # Quick Demo Buttons (Xóa khi deploy thật)
        ctk.CTkLabel(self.form_frame, text="-- DEMO ACCOUNTS --", text_color="gray").pack(pady=(20,5))
        
        demo_buttons_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        demo_buttons_frame.pack(pady=5)

        ctk.CTkButton(demo_buttons_frame, text="Student", fg_color="#E9C46A", text_color="black", 
                     command=lambda: self.fill_and_login("student@test.com", "Test123!")).pack(side="left", padx=5)
        ctk.CTkButton(demo_buttons_frame, text="Lecturer", fg_color="#F4A261", text_color="black", 
                     command=lambda: self.fill_and_login("lecturer@test.com", "Test123!")).pack(side="left", padx=5)
        ctk.CTkButton(demo_buttons_frame, text="Admin", fg_color="#E76F51", text_color="white", 
                     command=lambda: self.fill_and_login("admin@test.com", "Test123!")).pack(side="left", padx=5)

    def fill_and_login(self, email, pwd):
        """Fills the entry fields and immediately attempts to log in."""
        self.email_entry.delete(0, 'end')
        self.email_entry.insert(0, email)
        self.pass_entry.delete(0, 'end')
        self.pass_entry.insert(0, pwd)
        # Pass credentials directly to handle_login to avoid potential UI update delays
        self.handle_login(email, pwd)

    def handle_login(self, email=None, pwd=None):
        """Handles the login logic. Can receive credentials directly or get them from entry fields."""
        # If credentials are not passed, get them from the UI.
        # This is for the manual "Sign In" button click.
        if email is None:
            email = self.email_entry.get()
        if pwd is None:
            pwd = self.pass_entry.get()

        user, msg = self.auth_controller.login(email, pwd)
        
        if user:
            if user.role == "Student":
                self.app.show_student_dashboard(user)
            else:
                messagebox.showinfo("Login Successful", f"Welcome, {user.full_name}!\n\nDashboard for '{user.role}' is under construction.")
        else:
            messagebox.showerror("Login Failed", msg)