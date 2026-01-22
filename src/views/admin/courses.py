import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class CoursesFrame(ctk.CTkFrame):
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

        # 3. List Container
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 4. Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="MANAGE COURSES", font=("Arial", 20, "bold"), text_color="#115E59").pack(side="left")
        ctk.CTkButton(header, text="+ Add Course", fg_color=self.COLOR_PRIMARY, hover_color="#059669", 
                      width=120, command=self.open_add_dialog).pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", height=45, corner_radius=0)
        h_frame.pack(fill="x", padx=20)
        
        # Columns: Code, Name, Credits, Type, Prerequisites, Actions
        cols = [("COURSE CODE", 1), ("COURSE NAME", 3), ("CREDITS", 1), ("TYPE", 1), ("PREREQUISITES", 2), ("ACTIONS", 1)]
        
        for i, (text, w) in enumerate(cols):
            h_frame.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(h_frame, text=text, font=("Arial", 11, "bold"), text_color="gray", anchor="w").grid(row=0, column=i, sticky="ew", padx=10, pady=12)

    def load_data(self):
        for w in self.scroll_area.winfo_children(): w.destroy()
        courses = self.controller.get_all_courses()
        for c in courses: self.create_row(c)

    def create_row(self, data):
        row = ctk.CTkFrame(self.scroll_area, fg_color="white", corner_radius=0)
        row.pack(fill="x", pady=1)
        
        weights = [1, 3, 1, 1, 2, 1]
        for i, w in enumerate(weights): row.grid_columnconfigure(i, weight=w)

        # Cells
        ctk.CTkLabel(row, text=data.course_code, font=("Arial", 12, "bold"), text_color="#333", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=15)
        ctk.CTkLabel(row, text=data.course_name, anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=str(data.credits), anchor="w").grid(row=0, column=2, sticky="ew", padx=10)

        # Type Badge (Core/Elective)
        ctype = data.course_type
        bg = "#DBEAFE" if ctype == "Core" else "#F3E8FF" # Blue vs Purple
        fg = "#1E40AF" if ctype == "Core" else "#7E22CE"
        badge = ctk.CTkFrame(row, fg_color=bg, corner_radius=6, height=22)
        badge.grid(row=0, column=3, sticky="w", padx=10)
        ctk.CTkLabel(badge, text=ctype, font=("Arial", 10, "bold"), text_color=fg).pack(padx=8, pady=2)

        prereq = data.prerequisites_str if data.prerequisites_str else 'None'
        ctk.CTkLabel(row, text=prereq, text_color="gray", anchor="w").grid(row=0, column=4, sticky="ew", padx=10)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5)
        ctk.CTkButton(actions, text="✎", width=30, fg_color="transparent", text_color=self.COLOR_EDIT, hover_color="#EFF6FF", 
                      font=("Arial", 16), command=lambda: self.open_edit_dialog(data)).pack(side="left")
        ctk.CTkButton(actions, text="🗑", width=30, fg_color="transparent", text_color=self.COLOR_DELETE, hover_color="#FEF2F2", 
                      font=("Arial", 16), command=lambda: self.delete_item(data.course_id)).pack(side="left")

        ctk.CTkFrame(self.scroll_area, height=1, fg_color="#F3F4F6").pack(fill="x")

    def delete_item(self, cid):
        if messagebox.askyesno("Confirm", "Delete this course?"):
            success, msg = self.controller.delete_course(cid)
            if success: self.load_data()
            else: messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        CourseDialog(self, "Add New Course", self.controller, self.load_data)

    def open_edit_dialog(self, data):
        CourseDialog(self, "Edit Course", self.controller, self.load_data, data)


# ==========================================
# POPUP: ADD/EDIT COURSE
# ==========================================
class CourseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("750x500")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(pady=20, anchor="w", padx=30)

        # Form Container
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # Row 1: Code & Name
        self.ent_code = self._add_field(form, 0, 0, "Course Code", "e.g. CS101", width=200)
        self.ent_name = self._add_field(form, 0, 1, "Course Name", "Introduction to Programming", width=420)

        # Row 2: Credits & Type
        self.ent_credits = self._add_field(form, 1, 0, "Credits", "3", width=200)
        
        ctk.CTkLabel(form, text="Type", font=("Arial", 12, "bold"), text_color="#555").grid(row=2, column=1, sticky="w", pady=(10, 5))
        self.combo_type = ctk.CTkComboBox(form, values=["Core", "Elective"], width=420, height=35)
        self.combo_type.grid(row=3, column=1, sticky="w", padx=(10, 0))

        # Row 3: Description (TextArea)
        ctk.CTkLabel(form, text="Description", font=("Arial", 12, "bold"), text_color="#555").grid(row=4, column=0, sticky="w", pady=(10, 5))
        self.txt_desc = ctk.CTkTextbox(form, height=80, width=640, border_color="#E5E7EB", border_width=1)
        self.txt_desc.grid(row=5, column=0, columnspan=2, sticky="w")

        # Row 4: Prerequisites
        ctk.CTkLabel(form, text="Prerequisites (comma separated codes)", font=("Arial", 12, "bold"), text_color="#555").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 5))
        self.ent_prereq = ctk.CTkEntry(form, placeholder_text="e.g. CS101, MATH101", width=640, height=35)
        self.ent_prereq.grid(row=7, column=0, columnspan=2, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=30)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#DDD", border_width=1, text_color="black", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save Course", fg_color="#10B981", hover_color="#059669", command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            self.ent_code.insert(0, data.course_code)
            self.ent_name.insert(0, data.course_name)
            self.ent_credits.insert(0, str(data.credits))
            self.combo_type.set(data.course_type)
            self.txt_desc.insert("0.0", data.description if data.description else '')
            self.ent_prereq.insert(0, data.prerequisites_str if data.prerequisites_str else '')
            self.ent_code.configure(state="disabled") # Code usually unique

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _add_field(self, parent, r, c, label, placeholder, width=300):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#555").grid(row=r*2, column=c, sticky="w", pady=(10, 5))
        ent = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width, height=35)
        ent.grid(row=r*2+1, column=c, sticky="w", padx=(0 if c==0 else 10, 0))
        return ent

    def save(self):
        try:
            credits = int(self.ent_credits.get())
        except:
            messagebox.showwarning("Input Error", "Credits must be a number", parent=self)
            return

        if self.data: # Update
            success, msg = self.controller.update_course(
                self.data.course_id, self.ent_code.get(), self.ent_name.get(),
                credits, self.combo_type.get(), 
                self.txt_desc.get("0.0", "end").strip(), self.ent_prereq.get()
            )
        else: # Create
            success, msg = self.controller.create_course(
                self.ent_code.get(), self.ent_name.get(), credits, 
                self.combo_type.get(), 
                self.txt_desc.get("0.0", "end").strip(), self.ent_prereq.get()
            )

        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)