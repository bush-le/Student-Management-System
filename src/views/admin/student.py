import customtkinter as ctk
from tkinter import messagebox, filedialog
from controllers.admin_controller import AdminController

class StudentsFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = AdminController(user_id)
        
        self.create_toolbar()
        self.create_table_header()

        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.scroll_area.pack(fill="both", expand=True, pady=(0, 20))

        self.load_data()

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        toolbar.pack(fill="x", pady=(0, 15))
        
        # Search Entry (Không icon)
        self.search_ent = ctk.CTkEntry(
            toolbar, placeholder_text="Search student...", 
            width=300, height=40, border_color="#E5E7EB", border_width=1
        )
        self.search_ent.pack(side="left")
        
        # Buttons (Không icon)
        btn_import = ctk.CTkButton(
            toolbar, text="Import CSV", fg_color="white", text_color="#333", 
            border_color="#D1D5DB", border_width=1, hover_color="#F3F4F6", height=40,
            command=self.import_csv
        )
        btn_import.pack(side="right", padx=10)

        btn_add = ctk.CTkButton(
            toolbar, text="+ Add Student", fg_color="#0F766E", hover_color="#115E59", height=40,
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=40, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        
        columns = [("ID", 1), ("FULL NAME", 3), ("DEPARTMENT", 2), ("EMAIL", 3), ("STATUS", 1), ("ACTIONS", 2)]
        
        for i, (col_name, w) in enumerate(columns):
            h_frame.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(
                h_frame, text=col_name, font=("Arial", 11, "bold"), text_color="#374151", anchor="w"
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=8)

    def load_data(self):
        for widget in self.scroll_area.winfo_children(): widget.destroy()
        try:
            students = self.controller.get_all_students()
            for idx, s in enumerate(students):
                self.create_row(s, idx)
        except Exception as e:
            print(f"Error loading data: {e}")

    def create_row(self, data, idx):
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB"
        row = ctk.CTkFrame(self.scroll_area, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        
        weights = [1, 3, 2, 3, 1, 2]
        for i, w in enumerate(weights): 
            row.grid_columnconfigure(i, weight=w)

        ctk.CTkLabel(row, text=data.student_code, font=("Arial", 12, "bold"), text_color="#333", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=12)
        ctk.CTkLabel(row, text=data.full_name, font=("Arial", 12), text_color="#333", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        dept = data.dept_name if data.dept_name else 'N/A'
        ctk.CTkLabel(row, text=dept, font=("Arial", 12), text_color="#555", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data.email, font=("Arial", 12), text_color="#555", anchor="w").grid(row=0, column=3, sticky="ew", padx=10)

        status = data.academic_status
        status_col = "#059669" if status == 'ACTIVE' else "#DC2626"
        ctk.CTkLabel(row, text=status, font=("Arial", 10, "bold"), text_color=status_col, anchor="w").grid(row=0, column=4, sticky="ew", padx=10)

        # Actions (Thay icon bằng text)
        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.grid(row=0, column=5, sticky="w", padx=5)
        
        self._action_btn(action_frame, "View", "#6366F1", lambda: self.open_academic_record(data))
        self._action_btn(action_frame, "Edit", "#3B82F6", lambda: self.open_edit_dialog(data))
        self._action_btn(action_frame, "Del", "#EF4444", lambda: self.delete_item(data.student_id))

    def _action_btn(self, parent, text, color, cmd):
        # Sử dụng text thay vì icon
        ctk.CTkButton(
            parent, text=text, width=40, height=30, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left", padx=2)

    # --- CÁC HÀM LOGIC (Giữ nguyên như cũ) ---

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            success, msg = self.controller.import_students_csv(file_path)
            if success:
                messagebox.showinfo("Success", msg)
                self.load_data()
            else:
                messagebox.showerror("Error", msg)

    def delete_item(self, sid):
        if messagebox.askyesno("Confirm", "Delete this student?"):
            success, msg = self.controller.delete_student(sid)
            if success: self.load_data()
            else: messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        StudentDialog(self, "Add New Student", self.controller, self.load_data)

    def open_edit_dialog(self, data):
        StudentDialog(self, "Edit Student", self.controller, self.load_data, data)

    def open_academic_record(self, data):
        AcademicRecordDialog(self, data, self.controller)


# ==========================================
# POPUP: ADD/EDIT STUDENT
# ==========================================
class StudentDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("700x450")
        self.resizable(False, False)
        self.transient(parent)
        
        self.configure(fg_color="white")
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(pady=20, anchor="w", padx=30)

        # Form Container (Grid layout 2 columns)
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # Fields
        self.ent_name = self._add_field(form, 0, 0, "Full Name", "e.g. Nguyen Van A")
        self.ent_id = self._add_field(form, 0, 1, "Student ID", "e.g. S001")
        self.ent_email = self._add_field(form, 1, 0, "Email Address", "student@university.edu")
        self.ent_dob = self._add_field(form, 1, 1, "Date of Birth", "YYYY-MM-DD") # Placeholder
        
        # Dept Dropdown (Giả lập data)
        ctk.CTkLabel(form, text="Department", font=("Arial", 12, "bold"), text_color="#555").grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.combo_dept = ctk.CTkComboBox(form, values=["Computer Science", "Electrical Engineering", "Business"], width=300, height=35)
        self.combo_dept.grid(row=3, column=0, sticky="w", padx=(0, 10))

        # Status Dropdown
        ctk.CTkLabel(form, text="Enrollment Status", font=("Arial", 12, "bold"), text_color="#555").grid(row=2, column=1, sticky="w", pady=(10, 5))
        self.combo_status = ctk.CTkComboBox(form, values=["Active", "On Leave", "Dropped", "Graduated"], width=300, height=35)
        self.combo_status.grid(row=3, column=1, sticky="w", padx=(10, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=30)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#DDD", border_width=1, text_color="black", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save Student", fg_color="#0F766E", command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            self.ent_name.insert(0, data.full_name)
            self.ent_id.insert(0, data.student_code)
            self.ent_email.insert(0, data.email)
            # Note: DoB, Dept mapping cần logic mapping ID sang tên trong thực tế
            self.combo_dept.set(data.dept_name if data.dept_name else 'Computer Science') 
            self.combo_status.set(data.academic_status)
            # Nếu edit, có thể disable ID
            self.ent_id.configure(state="disabled")

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _add_field(self, parent, r, c, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#555").grid(row=r*2, column=c, sticky="w", pady=(10, 5))
        ent = ctk.CTkEntry(parent, placeholder_text=placeholder, width=300, height=35)
        ent.grid(row=r*2+1, column=c, sticky="w", padx=(0 if c==0 else 10, 0))
        return ent

    def save(self):
        # Logic gọi Controller create/update
        # Để đơn giản, map Dept Name sang ID giả
        dept_map = {"Computer Science": 1, "Electrical Engineering": 2, "Business": 3}
        dept_id = dept_map.get(self.combo_dept.get(), 1)
        
        if self.data: # Update
             success, msg = self.controller.update_student(
                 self.data.student_id, self.ent_name.get(), self.ent_email.get(), dept_id, self.combo_status.get()
             )
        else: # Create
             # Create cần username/password, ở đây demo sẽ auto-gen
             success, msg = self.controller.create_student(
                 username=self.ent_id.get(), password="123", # Default Pwd
                 full_name=self.ent_name.get(), email=self.ent_email.get(),
                 phone="0000000000", student_code=self.ent_id.get(),
                 dept_id=dept_id, major="N/A", year=2024
             )
        
        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


# ==========================================
# POPUP: ACADEMIC RECORD
# ==========================================
class AcademicRecordDialog(ctk.CTkToplevel):
    def __init__(self, parent, student_data, controller):
        super().__init__(parent)
        self.title("Academic Record")
        self.geometry("700x500")
        self.transient(parent)
        self.configure(fg_color="white")
        
        # 1. Header
        header = ctk.CTkFrame(self, fg_color="white")
        header.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header, text="Academic Record", font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(header, text=f"Student: {student_data.full_name} ({student_data.student_code})", text_color="gray").pack(anchor="w")

        # 2. Fetch Data
        record = controller.get_student_academic_record(student_data.student_id)

        # 3. Stats Cards
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=30, pady=10)
        self._card(stats, "GPA", str(record['gpa']), "#EFF6FF", "#2563EB")
        self._card(stats, "CREDITS EARNED", str(record['credits']), "#F0FDF4", "#16A34A")
        self._card(stats, "STATUS", record['status'], "#FAF5FF", "#9333EA")

        # 4. Grades Table
        ctk.CTkLabel(self, text="Course Performance", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=30, pady=(20, 10))
        
        table = ctk.CTkScrollableFrame(self, fg_color="#F9FAFB", height=200)
        table.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Header
        headers = ["COURSE", "MIDTERM", "FINAL", "TOTAL"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 10, "bold"), text_color="gray", width=150, anchor="w" if i==0 else "center").grid(row=0, column=i, pady=10)

        # Rows
        if not record['grades']:
            ctk.CTkLabel(table, text="No grade records found.").grid(row=1, column=0, columnspan=4, pady=20)
        
        for idx, g in enumerate(record['grades'], start=1):
            ctk.CTkLabel(table, text=g['course_name'], font=("Arial", 12, "bold"), anchor="w", width=150).grid(row=idx, column=0, pady=5)
            ctk.CTkLabel(table, text=str(g['midterm']), anchor="center", width=150).grid(row=idx, column=1)
            ctk.CTkLabel(table, text=str(g['final']), anchor="center", width=150).grid(row=idx, column=2)
            ctk.CTkLabel(table, text=str(g['total']), font=("Arial", 12, "bold"), text_color="#10B981", anchor="center", width=150).grid(row=idx, column=3)

        # Close Btn
        ctk.CTkButton(self, text="Close", fg_color="#333", command=self.destroy, width=100).pack(pady=20, anchor="e", padx=30)
        
        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _card(self, parent, title, value, bg, fg):
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8, width=200)
        card.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(card, text=title, font=("Arial", 10, "bold"), text_color=fg).pack(anchor="w", padx=15, pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"), text_color="#333").pack(anchor="w", padx=15, pady=(0, 15))