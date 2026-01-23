import customtkinter as ctk
from tkinter import messagebox
from utils.threading_helper import run_in_background

class ForgotPasswordView(ctk.CTkFrame):
    def __init__(self, parent, auth_controller, back_callback):
        super().__init__(parent, fg_color="transparent")
        self.controller = auth_controller
        self.back_callback = back_callback
        self.current_email = None

        # --- MAIN CARD (Matches design) ---
        self.card = ctk.CTkFrame(self, fg_color="white", corner_radius=16, width=420)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        # Inner frame for padding within the card
        # Content frame (Padding inside card)
        self.inner = ctk.CTkFrame(self.card, fg_color="transparent")
        self.inner.pack(padx=40, pady=40, fill="both", expand=True)

        # 1. ICON LOGO (Graduation cap in rounded square)
        self.create_icon_header()

        # 2. TITLE & SUBTITLE
        ctk.CTkLabel(self.inner, text="Forgot Password", font=("Arial", 26, "bold"), text_color="#0F5132").pack(pady=(15, 5))
        
        self.subtitle = ctk.CTkLabel(self.inner, text="Enter your email to receive a recovery code.", font=("Arial", 12), text_color="#6B7280")
        self.subtitle.pack(pady=(0, 20))

        # 3. STATUS LABEL (To report error/success right below subtitle)
        self.status_lbl = ctk.CTkLabel(self.inner, text="", font=("Arial", 12))
        self.status_lbl.pack(pady=(0, 5))

        # --- STEP 1: EMAIL INPUT FORM ---
        self.step1_frame = ctk.CTkFrame(self.inner, fg_color="transparent")
        self.step1_frame.pack(fill="x")

        ctk.CTkLabel(self.step1_frame, text="Email Address", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(0, 5))
        
        self.email_ent = ctk.CTkEntry(
            self.step1_frame, 
            placeholder_text="student@university.com", 
            width=340, height=45, 
            border_color="#D1D5DB", 
            fg_color="#F9FAFB",
            text_color="#111827"
        )
        self.email_ent.pack(pady=(0, 20))
        
        self.send_btn = ctk.CTkButton(
            self.step1_frame, 
            text="Send Recovery Code", 
            width=340, height=45, 
            fg_color="#367c74", hover_color="#2A6B63", # Dark Teal color matching image
            font=("Arial", 14, "bold"),
            command=self.send_code
        )
        self.send_btn.pack()

        # --- STEP 2: OTP & PASSWORD FORM (Hidden by default) ---
        self.step2_frame = ctk.CTkFrame(self.inner, fg_color="transparent") # Hidden by default
        
        # OTP Input
        ctk.CTkLabel(self.step2_frame, text="Recovery Code (OTP)", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(0, 5))
        self.otp_ent = ctk.CTkEntry(self.step2_frame, placeholder_text="123456", width=340, height=45, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="black")
        self.otp_ent.pack(pady=(0, 15))

        # New Password Input
        ctk.CTkLabel(self.step2_frame, text="New Password", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(0, 5))
        self.pass_ent = ctk.CTkEntry(self.step2_frame, placeholder_text="New Password", show="•", width=340, height=45, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="black")
        self.pass_ent.pack(pady=(0, 20))

        ctk.CTkButton(
            self.step2_frame, 
            text="Reset Password", 
            width=340, height=45, 
            fg_color="#E76F51", hover_color="#D65A3F", # Prominent orange for important action
            font=("Arial", 14, "bold"),
            command=self.do_reset
        ).pack()
        # Button to reset password
        # 4. FOOTER LINK (Back to Login)
        # Style matching image: "Remember password? Sign in"
        self.footer_frame = ctk.CTkFrame(self.inner, fg_color="transparent")
        self.footer_frame.pack(pady=(20, 0))

        ctk.CTkLabel(self.footer_frame, text="Remember password?", font=("Arial", 12), text_color="#6B7280").pack(side="left")
        
        link_btn = ctk.CTkButton(self.footer_frame,
            text="Sign in", # Button to navigate back to login
            fg_color="transparent", 
            text_color="#367c74", # Teal text color
            font=("Arial", 12, "bold"), 
            hover_color="white",
            width=50,
            command=self.back_callback
        )
        link_btn.pack(side="left", padx=(5, 0))

    def create_icon_header(self):
        """Creates a graduation cap icon in a rounded square frame"""
        # Icon container (Simulated light blue rounded square)
        icon_bg = ctk.CTkFrame(self.inner, fg_color="#E0F2F1", width=70, height=70, corner_radius=15)
        icon_bg.pack()
        icon_bg.pack_propagate(False)
        # Centered Emoji Icon
        ctk.CTkLabel(icon_bg, text="KEY", font=("Arial", 16, "bold"), text_color="#0F766E").place(relx=0.5, rely=0.5, anchor="center")

    # --- PROCESSING LOGIC ---
    def send_code(self):
        email = self.email_ent.get()
        if not email:
            self.status_lbl.configure(text="Please enter your email address.", text_color="#DC2626")
            return
        
        # Loading UI feedback
        self.status_lbl.configure(text="Sending...", text_color="#2563EB")
        self.send_btn.configure(state="disabled", text="Sending...")
        
        def _send_task():
            return self.controller.request_password_reset(email)

        def _on_send_complete(result):
            success, msg = result
            self.send_btn.configure(state="normal", text="Send Recovery Code")
            
            if success:
                self.current_email = email
                self.status_lbl.configure(text=f"Code sent! Check your inbox.", text_color="#16A34A")
                # Switch to Step 2
                self.step1_frame.pack_forget()
                self.step2_frame.pack(fill="x")
                # Update instructions
                self.subtitle.configure(text="Enter the code sent to your email and a new password.")
            else:
                self.status_lbl.configure(text=msg, text_color="#DC2626")

        run_in_background(_send_task, _on_send_complete, tk_root=self.winfo_toplevel())

    def do_reset(self):
        otp = self.otp_ent.get()
        new_pass = self.pass_ent.get()
        
        if not otp or not new_pass:
            self.status_lbl.configure(text="Please fill in all fields.", text_color="#DC2626")
            return

        def _reset_task():
            return self.controller.reset_password(self.current_email, otp, new_pass)

        def _on_reset_complete(result):
            success, msg = result
            if success:
                messagebox.showinfo("Success", "Password reset successfully!\nPlease sign in with your new password.")
                self.back_callback()
            else:
                self.status_lbl.configure(text=msg, text_color="#DC2626")

        run_in_background(_reset_task, _on_reset_complete, tk_root=self.winfo_toplevel())