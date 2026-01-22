import customtkinter as ctk
from tkinter import messagebox
from controllers.student_controller import StudentController

class ProfileView(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.controller = StudentController(user.user_id)
        self.is_editing = False # Trạng thái đang sửa hay không
        
        # Lưu tham chiếu các ô nhập liệu để lấy dữ liệu sau này
        self.entries = {} 

        # Container Card
        self.card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.card.pack(fill="both", expand=True, padx=0, pady=0)

        # 1. HEADER
        self.create_header()

        ctk.CTkFrame(self.card, height=2, fg_color="#F3F4F6").pack(fill="x", padx=30, pady=(0, 20))

        # 2. DETAILS GRID
        self.create_details_grid()

    def create_header(self):
        header = ctk.CTkFrame(self.card, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=30)

        # Avatar
        avatar = ctk.CTkLabel(header, text="👤", font=("Arial", 45), width=90, height=90, fg_color="#E0F2F1", text_color="#2A9D8F", corner_radius=45)
        avatar.pack(side="left")

        # Info
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left", padx=20)
        ctk.CTkLabel(info, text=self.user.full_name, font=("Arial", 24, "bold"), text_color="#1F2937").pack(anchor="w")
        ctk.CTkLabel(info, text=self.user.email, font=("Arial", 14), text_color="#2A9D8F").pack(anchor="w", pady=(2, 8))
        
        # Badges
        badge_row = ctk.CTkFrame(info, fg_color="transparent")
        badge_row.pack(anchor="w")
        self.create_badge(badge_row, "STUDENT", "#F3F4F6", "#4B5563")
        self.create_badge(badge_row, "SV2024001", "#DBEAFE", "#1E40AF")

        # --- EDIT BUTTON ---
        self.edit_btn = ctk.CTkButton(
            header, text="✏️ Edit Info", 
            fg_color="#2A9D8F", hover_color="#238b7e",
            width=120, height=35,
            font=("Arial", 12, "bold"),
            command=self.toggle_edit_mode
        )
        self.edit_btn.pack(side="right", anchor="n")

    def create_details_grid(self):
        grid = ctk.CTkFrame(self.card, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # --- CỘT TRÁI (READ-ONLY) ---
        col1 = ctk.CTkFrame(grid, fg_color="transparent")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        ctk.CTkLabel(col1, text="Academic Information", font=("Arial", 14, "bold"), text_color="#111827").pack(anchor="w", pady=(0, 15))
        
        # Các trường này KHÔNG BAO GIỜ được sửa
        self.create_field(col1, "DEPARTMENT", "Computer Science", is_editable=False)
        self.create_field(col1, "CLASS", "SE_K24_01", is_editable=False)
        self.create_field(col1, "ENROLLMENT STATUS", "Active", is_editable=False)

        # --- CỘT PHẢI (EDITABLE) ---
        col2 = ctk.CTkFrame(grid, fg_color="transparent")
        col2.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        ctk.CTkLabel(col2, text="Contact Details", font=("Arial", 14, "bold"), text_color="#111827").pack(anchor="w", pady=(0, 15))

        # Các trường này ĐƯỢC PHÉP sửa
        # Lưu ý: Lấy dữ liệu từ self.user (cần đảm bảo model User có các field này)
        # Giả sử address và dob chưa có trong object user, ta dùng text mẫu
        user_dob = getattr(self.user, 'dob', '2002-05-15')
        user_addr = getattr(self.user, 'address', '123 Vo Van Ngan, Thu Duc')

        self.create_field(col2, "DATE OF BIRTH", str(user_dob), is_editable=False) # Ngày sinh thường không cho sửa tự do
        
        # Ba trường quan trọng cần sửa:
        self.create_field(col2, "EMAIL ADDRESS", self.user.email, field_key="email", is_editable=True)
        self.create_field(col2, "PHONE NUMBER", self.user.phone, field_key="phone", is_editable=True)
        self.create_field(col2, "ADDRESS", str(user_addr), field_key="address", is_editable=True)

    def create_field(self, parent, label, value, field_key=None, is_editable=False):
        ctk.CTkLabel(parent, text=label, font=("Arial", 11, "bold"), text_color="#6B7280").pack(anchor="w", pady=(10, 5))
        
        entry = ctk.CTkEntry(
            parent, height=45, 
            fg_color="#F9FAFB", border_color="#E5E7EB", 
            text_color="#111827", font=("Arial", 13),
            state="normal" # Mặc định normal để insert text
        )
        entry.insert(0, str(value) if value else "")
        entry.configure(state="disabled") # Sau đó disable ngay
        entry.pack(fill="x")

        # Nếu là trường có thể sửa, lưu tham chiếu lại để dùng sau
        if is_editable and field_key:
            self.entries[field_key] = entry

    def create_badge(self, parent, text, bg_col, text_col):
        badge = ctk.CTkLabel(parent, text=text, fg_color=bg_col, text_color=text_col, font=("Arial", 10, "bold"), corner_radius=6, padx=10, pady=2)
        badge.pack(side="left", padx=(0, 10))

    # --- LOGIC XỬ LÝ EDIT/SAVE ---
    def toggle_edit_mode(self):
        if not self.is_editing:
            # BẬT CHẾ ĐỘ SỬA
            self.is_editing = True
            self.edit_btn.configure(text="💾 Save Changes", fg_color="#E76F51", hover_color="#D65A3F") # Đổi màu cam
            
            # Mở khóa các ô nhập liệu được phép sửa
            for key, entry in self.entries.items():
                entry.configure(state="normal", border_color="#2A9D8F", fg_color="white")
                if key == "email": entry.focus() # Focus vào ô đầu tiên
        else:
            # LƯU THAY ĐỔI
            self.save_changes()

    def save_changes(self):
        # 1. Lấy dữ liệu từ Form
        new_email = self.entries['email'].get()
        new_phone = self.entries['phone'].get()
        new_addr = self.entries['address'].get()

        # 2. Validate cơ bản
        if not new_email or not new_phone:
            messagebox.showerror("Error", "Email and Phone cannot be empty!")
            return

        # 3. Gọi Controller cập nhật DB
        success, msg = self.controller.update_contact_info(new_email, new_phone, new_addr)

        if success:
            messagebox.showinfo("Success", "Personal information updated successfully!")
            
            # Cập nhật lại object user trong bộ nhớ để đồng bộ
            self.user.email = new_email
            self.user.phone = new_phone
            # self.user.address = new_addr (Nếu User model có attr này)

            # Tắt chế độ sửa
            self.is_editing = False
            self.edit_btn.configure(text="✏️ Edit Info", fg_color="#2A9D8F", hover_color="#238b7e")
            
            # Khóa lại các ô
            for entry in self.entries.values():
                entry.configure(state="disabled", border_color="#E5E7EB", fg_color="#F9FAFB")
        else:
            messagebox.showerror("Update Failed", msg)