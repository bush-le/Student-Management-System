import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController
from views.auth.forgot_password import ForgotPasswordView
from utils.threading_helper import run_in_background

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#F9FAFB")
        self.app = app
        self.auth_controller = AuthController()

        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Panel (Unchanged)
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
        self.email_entry = ctk.CTkEntry(form, placeholder_text="youremail@uth.edu.vn", width=320, height=40, border_color="#D1D5DB")
        self.email_entry.grid(row=4, column=0, sticky="ew")

        ctk.CTkLabel(form, text="Password", font=("Arial", 12, "bold"), text_color="#374151").grid(row=5, column=0, sticky="w", pady=(15, 5))
        self.pass_entry = ctk.CTkEntry(form, placeholder_text="password", show="•", width=320, height=40, border_color="#D1D5DB")
        self.pass_entry.grid(row=6, column=0, sticky="ew")

        # FORGOT PASSWORD BUTTON -> Calls show_forgot_view
        ctk.CTkButton(
            form, text="Forgot password?", fg_color="transparent", 
            text_color="#2A9D8F", font=("Arial", 12, "bold"), 
            hover_color="white", anchor="w", 
            command=self.show_forgot_view 
        ).grid(row=7, column=0, sticky="w", pady=(5, 20))

        self.login_btn = ctk.CTkButton(
            form, text="Sign In", width=320, height=45,
            fg_color="#2A9D8F", hover_color="#238b7e", font=("Arial", 14, "bold"),
            command=self.on_login_click
        )
        self.login_btn.grid(row=8, column=0, sticky="ew")

    def show_forgot_view(self):
        """Clears the login form and shows the forgot password view."""
        self.clear_right_panel()
        # Pass the show_login_form callback so the child view can return
        ForgotPasswordView(self.right_frame, self.auth_controller, self.show_login_form).pack(fill="both", expand=True) # Forgot password view

    # --- LOGIN LOGIC ---
    def on_login_click(self):
        self.error_frame.grid_forget() 
        email = self.email_entry.get()
        password = self.pass_entry.get()
        
        self.login_btn.configure(state="disabled", text="Signing in...")

        def _login_task():
            return self.auth_controller.login(email, password)

        def _on_login_complete(result):
            user, message = result
            self.login_btn.configure(state="normal", text="Sign In")
            if user:
                self.app.show_dashboard(user)
            else:
                # Hiển thị lỗi ngay trên form thay vì popup
                self.error_label.configure(text=message)
                self.error_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        run_in_background(_login_task, _on_login_complete, tk_root=self.winfo_toplevel())