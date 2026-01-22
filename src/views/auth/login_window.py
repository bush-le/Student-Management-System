import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from views.auth.forgot_password import ForgotPasswordView

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#F9FAFB")
        self.app = app
        self.auth_controller = AuthController()

        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Panel (Giữ nguyên)
        self.create_left_panel()

        # Right Panel (Main Container)
        self.right_frame = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        # Show the initial login form
        self.show_login_form()

    def create_left_panel(self):
        self.left_frame = ctk.CTkFrame(self, fg_color="#2A9D8F", corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        content_box = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        content_box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content_box, text="🎓", font=("Arial", 64)).pack(pady=(0, 20))
        ctk.CTkLabel(content_box, text="Student\nManagement\nSystems", font=("Arial", 32, "bold"), text_color="white", justify="left").pack(anchor="w")
        ctk.CTkLabel(content_box, text="Manage your academic life, courses,\nand grades in one place.", font=("Arial", 14), text_color="#E0F2F1", justify="left").pack(anchor="w", pady=(20, 0))

    # --- NAVIGATION METHODS ---
    def clear_right_panel(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_login_form(self):
        """Renders the Login form."""
        self.clear_right_panel()

        self.login_card = ctk.CTkFrame(self.right_frame, fg_color="white", corner_radius=15, width=400)
        self.login_card.place(relx=0.5, rely=0.5, anchor="center")
        
        form = ctk.CTkFrame(self.login_card, fg_color="transparent")
        form.pack(padx=40, pady=40, fill="both", expand=True)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Welcome Back", font=("Arial", 26, "bold"), text_color="#1F2937").grid(row=0, column=0, pady=(0, 5))
        ctk.CTkLabel(form, text="Please sign in to your account", font=("Arial", 12), text_color="#6B7280").grid(row=1, column=0, pady=(0, 20))

        # Error Box
        self.error_frame = ctk.CTkFrame(form, fg_color="#FEF2F2", corner_radius=6, border_width=1, border_color="#FECACA")
        self.error_label = ctk.CTkLabel(self.error_frame, text="", text_color="#B91C1C", font=("Arial", 12), wraplength=300)
        self.error_label.pack(padx=10, pady=5)

        # Inputs
        ctk.CTkLabel(form, text="Email Address", font=("Arial", 12, "bold"), text_color="#374151").grid(row=3, column=0, sticky="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form, placeholder_text="student@test.com", width=320, height=40, border_color="#D1D5DB")
        self.email_entry.grid(row=4, column=0, sticky="ew")

        ctk.CTkLabel(form, text="Password", font=("Arial", 12, "bold"), text_color="#374151").grid(row=5, column=0, sticky="w", pady=(15, 5))
        self.pass_entry = ctk.CTkEntry(form, placeholder_text="••••••••", show="•", width=320, height=40, border_color="#D1D5DB")
        self.pass_entry.grid(row=6, column=0, sticky="ew")

        # FORGOT PASSWORD BUTTON -> Calls show_forgot_view
        ctk.CTkButton(
            form, text="Forgot password?", fg_color="transparent", 
            text_color="#2A9D8F", font=("Arial", 12, "bold"), 
            hover_color="white", anchor="w", 
            command=self.show_forgot_view 
        ).grid(row=7, column=0, sticky="w", pady=(5, 20))

        ctk.CTkButton(
            form, text="Sign In", width=320, height=45,
            fg_color="#2A9D8F", hover_color="#238b7e", font=("Arial", 14, "bold"),
            command=self.handle_login
        ).grid(row=8, column=0, sticky="ew")

        # Demo buttons
        self.create_demo_buttons(form)

    def show_forgot_view(self):
        """Clears the login form and shows the forgot password view."""
        self.clear_right_panel()
        # Pass the show_login_form callback so the child view can return
        ForgotPasswordView(self.right_frame, self.auth_controller, self.show_login_form).pack(fill="both", expand=True)

    # --- LOGIN LOGIC ---
    def handle_login(self, email=None, pwd=None):
        self.error_frame.grid_forget()
        if email is None: email = self.email_entry.get()
        if pwd is None: pwd = self.pass_entry.get()

        user, msg = self.auth_controller.login(email, pwd)
        
        if user and "successful" in msg.lower():
            self.app.show_dashboard(user)
        else:
            error_text = msg
            if user and "password" in msg.lower():
                max_attempts = 5
                attempts_left = max_attempts - user.failed_login_attempts
                if attempts_left > 0:
                    error_text = f"Invalid email or password. {attempts_left} attempts remaining."
            
            self.error_label.configure(text=error_text)
            self.error_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))

    def create_demo_buttons(self, parent):
        demo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        demo_frame.grid(row=9, column=0, pady=20)
        ctk.CTkLabel(demo_frame, text="Demo:", text_color="gray", font=("Arial", 10)).pack(side="left")
        
        # Student Demo
        ctk.CTkButton(demo_frame, text="Student", height=25, width=60, fg_color="#E9C46A", text_color="black",
                     command=lambda: self.fill_login("student@test.com", "Test123!")).pack(side="left", padx=5)
        
        # Lecturer Demo
        ctk.CTkButton(demo_frame, text="Lecturer", height=25, width=60, fg_color="#2A9D8F", text_color="white",
                     command=lambda: self.fill_login("lecturer@test.com", "Test123!")).pack(side="left", padx=5)

        # Admin Demo
        ctk.CTkButton(demo_frame, text="Admin", height=25, width=60, fg_color="#E76F51", text_color="white",
                     command=lambda: self.fill_login("admin@test.com", "Test123!")).pack(side="left", padx=5)

    def fill_login(self, email, pwd):
        self.email_entry.delete(0, 'end'); self.email_entry.insert(0, email)
        self.pass_entry.delete(0, 'end'); self.pass_entry.insert(0, pwd)
        self.handle_login(email, pwd)