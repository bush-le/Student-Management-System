import customtkinter as ctk
from tkinter import messagebox
from controllers.student_controller import StudentController
from utils.threading_helper import run_in_background

class ProfileView(ctk.CTkFrame):
    def __init__(self, parent, user, controller):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.controller = controller
        
        # State
        self.is_editing = False
        self.entries = {}
        
        # Theme colors
        self.COLOR_PRIMARY = "#0F766E"  # Teal
        self.COLOR_EDIT = "#F59E0B"     # Amber (Save button color)
        self.COLOR_BG_READONLY = "#F9FAFB"
        self.COLOR_BG_EDIT = "#FFFFFF"

        # --- UI LAYOUT ---
        # Main Card Container
        self.card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        self.card.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Show loading initially
        self.loading_lbl = ctk.CTkLabel(self.card, text="Loading profile...", text_color="gray")
        self.loading_lbl.pack(pady=40)

        # --- LOAD LATEST DATA FROM DB ---
        self.load_data_async()

    def load_data_async(self):
        run_in_background(
            self._fetch_profile,
            self._render_ui,
            tk_root=self.winfo_toplevel()
        )
        
    def _fetch_profile(self):
        """Retrieves full student information from DB (including class, department, date of birth...)"""
        try:
            # If not available, it will use basic information from self.user
            return self.controller.get_student_profile()
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def _render_ui(self, full_info):
        if not self.winfo_exists(): return
        if hasattr(self, 'loading_lbl'): self.loading_lbl.destroy()
        
        if full_info:
            self.student_info = full_info
        else:
            # Fallback data if DB error
            self.student_info = {
                'full_name': self.user.full_name,
                'email': self.user.email,
                'phone': getattr(self.user, 'phone', ''),
                'student_code': getattr(self.user, 'student_code', '---'),
                'dept_name': 'N/A', 
                'class_name': 'N/A',         
                'dob': 'N/A',           
                'address': 'N/A'  
            }
            
        # 1. Header Section
        self.create_header()

        # Separator
        ctk.CTkFrame(self.card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=40, pady=(0, 30))

        # 2. Form Grid
        self.create_form_grid()

    def create_header(self):
        header = ctk.CTkFrame(self.card, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=40)

        # Avatar Circle (First letter of name)
        initial = self.user.full_name[0].upper() if self.user.full_name else "U"
        avatar = ctk.CTkFrame(header, width=80, height=80, corner_radius=40, fg_color="#CCFBF1")
        avatar.pack(side="left")
        ctk.CTkLabel(avatar, text=initial, font=("Arial", 36, "bold"), text_color="#0F766E").place(relx=0.5, rely=0.5, anchor="center")

        # Info Text
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left", padx=25)
        
        ctk.CTkLabel(info, text=self.user.full_name, font=("Arial", 26, "bold"), text_color="#111827").pack(anchor="w")
        
        # Badges Row
        badges = ctk.CTkFrame(info, fg_color="transparent")
        badges.pack(anchor="w", pady=(8, 0))
        
        self.create_badge(badges, "STUDENT", "#F3F4F6", "#4B5563")
        self.create_badge(badges, self.student_info.get('student_code', '---'), "#DBEAFE", "#1E40AF")

        # Edit Button (Prominent on the right)
        self.edit_btn = ctk.CTkButton(
            header, text="Edit Profile", # Button to toggle edit mode
            fg_color="white", text_color="#374151", 
            hover_color="#F3F4F6", border_width=1, border_color="#D1D5DB",
            width=130, height=40, font=("Arial", 13, "bold"),
            command=self.toggle_edit_mode
        )
        self.edit_btn.pack(side="right", anchor="c")
        
        # Cancel Button (Hidden initially)
        self.cancel_btn = ctk.CTkButton(
            header, text="Cancel", 
            fg_color="white", text_color="#EF4444", 
            hover_color="#FEF2F2", border_width=1, border_color="#EF4444",
            width=100, height=40, font=("Arial", 13, "bold"),
            command=self.cancel_edit
        )

    def create_form_grid(self):
        grid = ctk.CTkFrame(self.card, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # --- LEFT COLUMN (Academic - Read Only) ---
        col1 = ctk.CTkFrame(grid, fg_color="transparent")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(col1, text="Academic Details", font=("Arial", 16, "bold"), text_color="#111827").pack(anchor="w", pady=(0, 20))
        
        self.create_field(col1, "DEPARTMENT", self.student_info.get('dept_name', 'N/A'))
        self.create_field(col1, "CLASS", self.student_info.get('class_name', 'N/A'))
        self.create_field(col1, "ENROLLMENT STATUS", "Active", text_color="#059669")

        # --- RIGHT COLUMN (Personal - Editable) ---
        col2 = ctk.CTkFrame(grid, fg_color="transparent")
        col2.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        
        ctk.CTkLabel(col2, text="Personal Information", font=("Arial", 16, "bold"), text_color="#111827").pack(anchor="w", pady=(0, 20))

        # Editable fields -> Assign key
        self.create_field(col2, "DATE OF BIRTH", self.student_info.get('dob', ''), key="dob", editable=True)
        self.create_field(col2, "EMAIL ADDRESS", self.student_info.get('email', ''), key="email", editable=True)
        self.create_field(col2, "PHONE NUMBER", self.student_info.get('phone', ''), key="phone", editable=True)
        self.create_field(col2, "CURRENT ADDRESS", self.student_info.get('address', ''), key="address", editable=True)

    def create_field(self, parent, label, value, text_color="#1F2937", key=None, editable=False):
        # Label
        ctk.CTkLabel(parent, text=label, font=("Arial", 11, "bold"), text_color="#6B7280").pack(anchor="w", pady=(0, 6))
        
        # Entry (Input Box)
        entry = ctk.CTkEntry(
            parent, height=42, 
            fg_color=self.COLOR_BG_READONLY, 
            border_color="#E5E7EB", border_width=1,
            text_color=text_color, font=("Arial", 13)
        )
        entry.insert(0, str(value) if value else "")
        entry.configure(state="disabled")
        entry.pack(fill="x", pady=(0, 15))

        # Store reference if editable field
        if editable and key:
            self.entries[key] = entry

    def create_badge(self, parent, text, bg, fg):
        lbl = ctk.CTkLabel(
            parent, text=text, 
            fg_color=bg, text_color=fg, 
            font=("Arial", 10, "bold"), 
            corner_radius=6, height=24
        )
        lbl.pack(side="left", padx=(0, 8), ipadx=8)

    # --- LOGIC ---
    def toggle_edit_mode(self):
        if not self.is_editing:
            self.is_editing = True # START EDITING
            self.edit_btn.configure(
                text="Save Changes", 
                fg_color=self.COLOR_PRIMARY, text_color="white",
                hover_color="#115E59", border_width=0
            )
            self.cancel_btn.pack(side="right", anchor="c", padx=(0, 10)) # Show cancel button
            
            # Unlock fields
            for key, ent in self.entries.items():
                ent.configure(state="normal", fg_color="white", border_color="#2A9D8F")
                if key == "email": ent.focus()
        else:
            # SAVE CHANGES
            self.save_data()

    def cancel_edit(self):
        """Revert changes and exit edit mode"""
        self.is_editing = False
        self.edit_btn.configure(
            text="Edit Profile", 
            fg_color="white", text_color="#374151",
            hover_color="#F3F4F6", border_width=1, border_color="#D1D5DB"
        )
        self.cancel_btn.pack_forget() # Hide cancel button
        
        # Reset fields to original values
        for key, ent in self.entries.items():
            ent.configure(state="normal")
            ent.delete(0, "end")
            val = self.student_info.get(key, "")
            ent.insert(0, str(val))
            ent.configure(state="disabled", fg_color=self.COLOR_BG_READONLY, border_color="#E5E7EB")

    def save_data(self):
        # 1. Collect Data
        updates = {k: v.get().strip() for k, v in self.entries.items()}
        
        # 2. Validate
        if not updates['email'] or not updates['phone']:
            messagebox.showerror("Error", "Email and Phone are required!")
            return

        # 3. Call Controller
        def _save_task():
            return self.controller.update_student_profile(
                self.user.user_id, 
                updates.get('email'),
                updates.get('phone'),
                updates.get('address'),
                updates.get('dob')
            )

        def _on_complete(result):
            success, msg = result
            if success:
                messagebox.showinfo("Success", "Profile updated successfully!")
                
                # Reset UI state
                self.is_editing = False
                self.edit_btn.configure(
                    text="Edit Profile", 
                    fg_color="white", text_color="#374151",
                    hover_color="#F3F4F6", border_width=1, border_color="#D1D5DB"
                )
                self.cancel_btn.pack_forget()
                
                # Lock fields
                for ent in self.entries.values():
                    ent.configure(state="disabled", fg_color=self.COLOR_BG_READONLY, border_color="#E5E7EB")
                # (Optional) Update self.user object in session
                self.user.email = updates.get('email')
                self.user.phone = updates.get('phone')
            else:
                messagebox.showerror("Update Failed", msg)

        run_in_background(_save_task, _on_complete, tk_root=self.winfo_toplevel())