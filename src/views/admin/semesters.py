import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class SemestersFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = AdminController(user_id)
        
        # 1. Toolbar
        self.create_toolbar()

        # 2. Table Header
        self.create_table_header()

        # 3. List Container
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.scroll_area.pack(fill="both", expand=True, pady=(0, 20))

        # 4. Load Data
        self.load_data()

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        toolbar.pack(fill="x", pady=(0, 15))
        
        # Search Entry
        self.search_ent = ctk.CTkEntry(
            toolbar, placeholder_text="Search semester...", 
            width=300, height=40, border_color="#E5E7EB", border_width=1
        )
        self.search_ent.pack(side="left")
        
        # Add Button
        btn_add = ctk.CTkButton(
            toolbar, text="+ New Semester", fg_color="#0F766E", hover_color="#115E59", height=40,
            font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=40, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        
        # Columns: Name, Start, End, Status, Actions
        cols = [("SEMESTER NAME", 3), ("START DATE", 1), ("END DATE", 1), ("STATUS", 1), ("ACTIONS", 2)]
        
        for i, (text, w) in enumerate(cols):
            h_frame.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), text_color="#374151", anchor="w"
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=8)

    def load_data(self):
        for widget in self.scroll_area.winfo_children(): widget.destroy()
        try:
            semesters = self.controller.get_all_semesters()
            for idx, sem in enumerate(semesters):
                self.create_row(sem, idx)
        except Exception as e:
            print(f"Error loading semesters: {e}")

    def create_row(self, data, idx):
        # Zebra striping
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB"
        
        row = ctk.CTkFrame(self.scroll_area, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        
        # Grid weights match Header
        weights = [3, 1, 1, 1, 2]
        for i, w in enumerate(weights): row.grid_columnconfigure(i, weight=w)

        # Data Cells
        ctk.CTkLabel(row, text=data.name, font=("Arial", 12, "bold"), text_color="#333", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=12)
        ctk.CTkLabel(row, text=str(data.start_date), font=("Arial", 12), text_color="#555", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=str(data.end_date), font=("Arial", 12), text_color="#555", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)

        # Status
        status = data.status.upper()
        status_col = "#059669" if status == "OPEN" else "#9CA3AF"
        ctk.CTkLabel(row, text=status, font=("Arial", 11, "bold"), text_color=status_col, anchor="w").grid(row=0, column=3, sticky="ew", padx=10)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=4, sticky="w", padx=5)
        
        self._action_btn(actions, "Edit", "#3B82F6", lambda: self.open_edit_dialog(data))
        self._action_btn(actions, "Del", "#EF4444", lambda: self.delete_item(data.semester_id))

    def _action_btn(self, parent, text, color, cmd):
        ctk.CTkButton(
            parent, text=text, width=40, height=30, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left", padx=2)

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
# POPUP DIALOG (STYLE UPDATE)
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
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=40)

        # Name
        self.entry_name = self.create_input("Semester Name", "e.g. Summer 2025")
        
        # Dates
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(fill="x", padx=40, pady=0)
        
        f1 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f1, text="Start Date", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        self.entry_start = ctk.CTkEntry(f1, placeholder_text="YYYY-MM-DD", height=40, border_color="#E5E7EB")
        self.entry_start.pack(fill="x", pady=5)

        f2 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f2, text="End Date", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        self.entry_end = ctk.CTkEntry(f2, placeholder_text="YYYY-MM-DD", height=40, border_color="#E5E7EB")
        self.entry_end.pack(fill="x", pady=5)

        # Status
        ctk.CTkLabel(self, text="Status", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", padx=40, pady=(15, 5))
        self.combo_status = ctk.CTkComboBox(
            self, values=["OPEN", "CLOSED"], width=320, height=40, 
            state="readonly", border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_status.pack(padx=40)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=40)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
                      text_color="black", hover_color="#F3F4F6", width=100, height=40, command=self.destroy).pack(side="left")
        
        ctk.CTkButton(btn_frame, text="Save", fg_color="#0F766E", hover_color="#115E59", 
                      width=100, height=40, font=("Arial", 13, "bold"), command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            self.entry_name.insert(0, data.name)
            self.entry_start.insert(0, str(data.start_date))
            self.entry_end.insert(0, str(data.end_date))
            self.combo_status.set(data.status)

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set) 

    def create_input(self, label, placeholder):
        ctk.CTkLabel(self, text=label, font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", padx=40, pady=(10, 5))
        entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=320, height=40, border_color="#E5E7EB")
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

        if self.data: # Update
            success, msg = self.controller.update_semester(self.data.semester_id, name, start, end, status)
        else: # Create
            success, msg = self.controller.create_semester(name, start, end)
        
        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)