import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class SemestersFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = AdminController(user_id)
        
        # --- COLORS ---
        self.COLOR_PRIMARY = "#10B981"  # Emerald Green
        self.COLOR_EDIT = "#3B82F6"     # Blue
        self.COLOR_DELETE = "#EF4444"   # Red

        # 1. Header Section
        self.create_header()

        # 2. Table Header
        self.create_table_header()

        # 3. List Container
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 4. Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=20)
        
        # Title
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Semesters Management", font=("Arial", 20, "bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Manage academic terms and registration status", font=("Arial", 12), text_color="gray").pack(anchor="w")

        # Add Button
        btn_add = ctk.CTkButton(
            header, text="+ New Semester", 
            fg_color=self.COLOR_PRIMARY, hover_color="#059669",
            font=("Arial", 13, "bold"), height=35,
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", height=45, corner_radius=0)
        h_frame.pack(fill="x", padx=20)
        
        h_frame.grid_columnconfigure(0, weight=2) # Name
        h_frame.grid_columnconfigure(1, weight=1) # Start
        h_frame.grid_columnconfigure(2, weight=1) # End
        h_frame.grid_columnconfigure(3, weight=1) # Status
        h_frame.grid_columnconfigure(4, weight=1) # Action

        headers = ["SEMESTER NAME", "START DATE", "END DATE", "STATUS", "ACTION"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, font=("Arial", 11, "bold"), text_color="gray").grid(row=0, column=i, sticky="ew", padx=10, pady=12)

    def load_data(self):
        for widget in self.scroll_area.winfo_children(): widget.destroy()
        semesters = self.controller.get_all_semesters()
        for sem in semesters:
            self.create_row(sem)

    def create_row(self, data):
        row = ctk.CTkFrame(self.scroll_area, fg_color="white", corner_radius=0)
        row.pack(fill="x", pady=1)
        
        row.grid_columnconfigure(0, weight=2)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=1)
        row.grid_columnconfigure(3, weight=1)
        row.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(row, text=data['name'], font=("Arial", 12, "bold"), text_color="#333").grid(row=0, column=0, sticky="w", padx=20, pady=15)
        ctk.CTkLabel(row, text=str(data['start_date']), text_color="#555").grid(row=0, column=1)
        ctk.CTkLabel(row, text=str(data['end_date']), text_color="#555").grid(row=0, column=2)

        status = data['status'].upper()
        bg_col = "#DCFCE7" if status == "OPEN" else "#F3F4F6"
        text_col = "#166534" if status == "OPEN" else "#4B5563"
        
        badge = ctk.CTkFrame(row, fg_color=bg_col, corner_radius=12, height=24)
        badge.grid(row=0, column=3)
        ctk.CTkLabel(badge, text=status, font=("Arial", 10, "bold"), text_color=text_col).pack(padx=10, pady=2)

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=4)
        
        ctk.CTkButton(actions, text="✎", width=30, fg_color="transparent", text_color="gray", hover_color="#EFF6FF", 
                      font=("Arial", 16), command=lambda: self.open_edit_dialog(data)).pack(side="left", padx=2)
        ctk.CTkButton(actions, text="🗑", width=30, fg_color="transparent", text_color="gray", hover_color="#FEF2F2", 
                      font=("Arial", 16), command=lambda: self.delete_item(data['semester_id'])).pack(side="left", padx=2)

        ctk.CTkFrame(self.scroll_area, height=1, fg_color="#F3F4F6").pack(fill="x")

    def delete_item(self, sem_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this semester?"):
            success, msg = self.controller.delete_semester(sem_id)
            if success:
                self.load_data()
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        SemesterDialog(self, "Add Semester", controller=self.controller, callback=self.load_data)

    def open_edit_dialog(self, data):
        SemesterDialog(self, "Edit Semester", controller=self.controller, callback=self.load_data, data=data)


# ==========================================
# POPUP DIALOG CLASS (ĐÃ SỬA LỖI GRAB FAILED)
# ==========================================
class SemesterDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("450x500")
        self.resizable(False, False)
        
        # --- FIX LỖI: Không gọi grab_set() ngay lập tức ---
        self.transient(parent) # Đặt cửa sổ con nằm trên cửa sổ cha
        
        # --- UI FORM ---
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(pady=(20, 20))

        # Name
        self.entry_name = self.create_input("Semester Name", "e.g. Summer 2025")
        
        # Dates
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(fill="x", padx=40, pady=0)
        
        f1 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f1, text="Start Date", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        self.entry_start = ctk.CTkEntry(f1, placeholder_text="YYYY-MM-DD", height=35)
        self.entry_start.pack(fill="x", pady=5)

        f2 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f2, text="End Date", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        self.entry_end = ctk.CTkEntry(f2, placeholder_text="YYYY-MM-DD", height=35)
        self.entry_end.pack(fill="x", pady=5)

        # Status
        ctk.CTkLabel(self, text="Status", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", padx=40, pady=(15, 5))
        self.combo_status = ctk.CTkComboBox(self, values=["OPEN", "CLOSED"], width=320, height=35, state="readonly")
        self.combo_status.pack(padx=40)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=40)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#E5E7EB", border_width=1, 
                      text_color="black", width=100, command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save", fg_color="#10B981", hover_color="#059669", 
                      width=100, command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            self.entry_name.insert(0, data['name'])
            self.entry_start.insert(0, str(data['start_date']))
            self.entry_end.insert(0, str(data['end_date']))
            self.combo_status.set(data['status'])

        # --- FIX LỖI: Đợi 100ms để cửa sổ hiện lên rồi mới grab ---
        self.lift()
        self.focus_force()
        self.after(100, self.grab_set) 

    def create_input(self, label, placeholder):
        ctk.CTkLabel(self, text=label, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", padx=40, pady=(10, 5))
        entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=320, height=35)
        entry.pack(padx=40)
        return entry

    def save(self):
        name = self.entry_name.get()
        start = self.entry_start.get()
        end = self.entry_end.get()
        status = self.combo_status.get()

        if not name or not start or not end:
            messagebox.showwarning("Warning", "Please fill all fields", parent=self)
            return

        # Gọi controller
        if self.data: # Update
            success, msg = self.controller.update_semester(self.data['semester_id'], name, start, end, status)
        else: # Create
            success, msg = self.controller.create_semester(name, start, end)
        
        if success:
            self.callback() # Load lại bảng ở frame cha
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)