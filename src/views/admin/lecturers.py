import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class LecturersFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = AdminController(user_id)
        
        self.COLOR_PRIMARY = "#10B981"
        self.COLOR_EDIT = "#3B82F6"
        self.COLOR_DELETE = "#EF4444"

        # 1. Header
        self.create_header()

        # 2. Table Header
        self.create_table_header()

        # 3. List
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 4. Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="MANAGE LECTURERS", font=("Arial", 20, "bold"), text_color="#115E59").pack(side="left")
        ctk.CTkButton(header, text="+ Add Lecturer", fg_color=self.COLOR_PRIMARY, hover_color="#059669", 
                      width=120, command=self.open_add_dialog).pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", height=45, corner_radius=0)
        h_frame.pack(fill="x", padx=20)
        
        # Columns: ID, Name, Email, Phone, Dept, Degree, Actions
        cols = [("ID", 1), ("FULL NAME", 2), ("EMAIL", 2), ("PHONE", 1), ("DEPARTMENT", 2), ("DEGREE", 1), ("ACTIONS", 1)]
        
        for i, (text, w) in enumerate(cols):
            h_frame.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(h_frame, text=text, font=("Arial", 11, "bold"), text_color="gray", anchor="w").grid(row=0, column=i, sticky="ew", padx=10, pady=12)

    def load_data(self):
        for w in self.scroll_area.winfo_children(): w.destroy()
        lecturers = self.controller.get_all_lecturers()
        for lec in lecturers: self.create_row(lec)

    def create_row(self, data):
        row = ctk.CTkFrame(self.scroll_area, fg_color="white", corner_radius=0)
        row.pack(fill="x", pady=1)
        
        weights = [1, 2, 2, 1, 2, 1, 1]
        for i, w in enumerate(weights): row.grid_columnconfigure(i, weight=w)

        # Data Cells
        ctk.CTkLabel(row, text=data.lecturer_code, font=("Arial", 12, "bold"), text_color="#333", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=15)
        ctk.CTkLabel(row, text=data.full_name, anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data.email, text_color="gray", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data.phone, text_color="gray", anchor="w").grid(row=0, column=3, sticky="ew", padx=10)
        
        dept = data.dept_name if data.dept_name else 'N/A'
        ctk.CTkLabel(row, text=dept, anchor="w").grid(row=0, column=4, sticky="ew", padx=10)
        
        # Degree Badge (M.Sc, Ph.D...)
        ctk.CTkLabel(row, text=data.degree, font=("Arial", 11), text_color="#555", anchor="w").grid(row=0, column=5, sticky="ew", padx=10)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=6)
        
        ctk.CTkButton(actions, text="✎", width=30, fg_color="transparent", text_color=self.COLOR_EDIT, hover_color="#EFF6FF", 
                      font=("Arial", 16), command=lambda: self.open_edit_dialog(data)).pack(side="left")
        ctk.CTkButton(actions, text="🗑", width=30, fg_color="transparent", text_color=self.COLOR_DELETE, hover_color="#FEF2F2", 
                      font=("Arial", 16), command=lambda: self.delete_item(data.lecturer_id)).pack(side="left")

        ctk.CTkFrame(self.scroll_area, height=1, fg_color="#F3F4F6").pack(fill="x")

    def delete_item(self, lid):
        if messagebox.askyesno("Confirm", "Delete this lecturer?"):
            success, msg = self.controller.delete_lecturer(lid)
            if success: self.load_data()
            else: messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        LecturerDialog(self, "Add New Lecturer", self.controller, self.load_data)

    def open_edit_dialog(self, data):
        LecturerDialog(self, "Edit Lecturer", self.controller, self.load_data, data)


# ==========================================
# POPUP: ADD/EDIT LECTURER
# ==========================================
class LecturerDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("700x420")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(pady=20, anchor="w", padx=30)

        # Form Layout
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # Fields
        self.ent_id = self._add_field(form, 0, 0, "Lecturer ID", "e.g. L101")
        self.ent_name = self._add_field(form, 0, 1, "Full Name", "e.g. Phan Gia Kiet")
        self.ent_email = self._add_field(form, 1, 0, "Email", "lecturer@test.com")
        self.ent_phone = self._add_field(form, 1, 1, "Phone Number", "0912345678")

        # Dept & Degree
        ctk.CTkLabel(form, text="Department", font=("Arial", 12, "bold"), text_color="#555").grid(row=4, column=0, sticky="w", pady=(10, 5))
        self.combo_dept = ctk.CTkComboBox(form, values=["Computer Science", "Electrical Engineering", "Business"], width=300, height=35)
        self.combo_dept.grid(row=5, column=0, sticky="w", padx=(0, 10))

        self.ent_degree = self._add_field(form, 2, 1, "Academic Degree", "e.g. Ph.D. in AI") # Dùng entry cho Degree

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=30)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#DDD", border_width=1, text_color="black", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save Lecturer", fg_color="#0F766E", command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            self.ent_id.insert(0, data.lecturer_code)
            self.ent_name.insert(0, data.full_name)
            self.ent_email.insert(0, data.email)
            self.ent_phone.insert(0, data.phone)
            self.combo_dept.set(data.dept_name if data.dept_name else 'Computer Science')
            self.ent_degree.delete(0, 'end'); self.ent_degree.insert(0, data.degree)
            
            self.ent_id.configure(state="disabled") # Không sửa ID

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _add_field(self, parent, r, c, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#555").grid(row=r*2, column=c, sticky="w", pady=(10, 5))
        ent = ctk.CTkEntry(parent, placeholder_text=placeholder, width=300, height=35)
        ent.grid(row=r*2+1, column=c, sticky="w", padx=(0 if c==0 else 10, 0))
        return ent

    def save(self):
        # Map Dept Name -> ID (Giả lập)
        dept_map = {"Computer Science": 1, "Electrical Engineering": 2, "Business": 3}
        dept_id = dept_map.get(self.combo_dept.get(), 1)

        if self.data: # Update
            success, msg = self.controller.update_lecturer(
                self.data.lecturer_id, self.ent_name.get(), self.ent_email.get(), 
                self.ent_phone.get(), dept_id, self.ent_degree.get()
            )
        else: # Create
            success, msg = self.controller.create_lecturer(
                self.ent_id.get(), self.ent_name.get(), self.ent_email.get(), 
                self.ent_phone.get(), dept_id, self.ent_degree.get()
            )

        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)