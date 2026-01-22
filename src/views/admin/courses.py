import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class CoursesFrame(ctk.CTkFrame):
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
            toolbar, placeholder_text="Search course...", 
            width=300, height=40, border_color="#E5E7EB", border_width=1
        )
        self.search_ent.pack(side="left")
        
        # Add Button
        btn_add = ctk.CTkButton(
            toolbar, text="+ Add Course", fg_color="#0F766E", hover_color="#115E59", height=40,
            font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=40, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        
        # Columns: Code, Name, Credits, Prerequisites, Actions
        # (ĐÃ BỎ CỘT TYPE/BADGE)
        cols = [("CODE", 1), ("COURSE NAME", 4), ("CREDITS", 1), ("PREREQUISITES", 3), ("ACTIONS", 2)]
        
        for i, (text, w) in enumerate(cols):
            h_frame.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), text_color="#374151", anchor="w"
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=8)

    def load_data(self):
        for w in self.scroll_area.winfo_children(): w.destroy()
        try:
            courses = self.controller.get_all_courses()
            for idx, c in enumerate(courses): 
                self.create_row(c, idx)
        except Exception as e:
            print(f"Error loading courses: {e}")

    def create_row(self, data, idx):
        # Zebra striping
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB"
        
        row = ctk.CTkFrame(self.scroll_area, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        
        # Grid weights match Header
        weights = [1, 4, 1, 3, 2]
        for i, w in enumerate(weights): row.grid_columnconfigure(i, weight=w)

        # Data Cells
        ctk.CTkLabel(row, text=data.course_code, font=("Arial", 12, "bold"), text_color="#333", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=12)
        ctk.CTkLabel(row, text=data.course_name, font=("Arial", 12), text_color="#333", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=str(data.credits), font=("Arial", 12), text_color="#555", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)

        # Prerequisites
        prereq = data.prerequisites_str if hasattr(data, 'prerequisites_str') and data.prerequisites_str else '-'
        ctk.CTkLabel(row, text=prereq, font=("Arial", 12), text_color="gray", anchor="w").grid(row=0, column=3, sticky="ew", padx=10)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=4, sticky="w", padx=5)
        
        self._action_btn(actions, "Edit", "#3B82F6", lambda: self.open_edit_dialog(data))
        self._action_btn(actions, "Del", "#EF4444", lambda: self.delete_item(data.course_id))

    def _action_btn(self, parent, text, color, cmd):
        ctk.CTkButton(
            parent, text=text, width=40, height=30, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left", padx=2)

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
# POPUP: ADD/EDIT COURSE (ĐÃ BỎ TYPE)
# ==========================================
class CourseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("700x450") # Thu nhỏ lại chút vì bớt trường
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=40)

        # Form Container
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)

        # Row 1: Code & Name
        self.ent_code = self._add_field(form, 0, 0, "Course Code", "e.g. CS101", width=200)
        self.ent_name = self._add_field(form, 0, 1, "Course Name", "Introduction to Programming", width=400)

        # Row 2: Credits
        self.ent_credits = self._add_field(form, 1, 0, "Credits", "3", width=200)
        
        # Row 3: Description (TextArea)
        ctk.CTkLabel(form, text="Description", font=("Arial", 12, "bold"), text_color="#374151").grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.txt_desc = ctk.CTkTextbox(form, height=60, width=620, border_color="#E5E7EB", border_width=1, fg_color="white", text_color="black")
        self.txt_desc.grid(row=3, column=0, columnspan=2, sticky="w")

        # Row 4: Prerequisites
        ctk.CTkLabel(form, text="Prerequisites (comma separated codes)", font=("Arial", 12, "bold"), text_color="#374151").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 5))
        self.ent_prereq = ctk.CTkEntry(form, placeholder_text="e.g. CS101, MATH101", width=620, height=40, border_color="#E5E7EB")
        self.ent_prereq.grid(row=5, column=0, columnspan=2, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=30)
        
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
            text_color="black", hover_color="#F3F4F6", width=100, height=40,
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="Save Course", fg_color="#0F766E", hover_color="#115E59", 
            width=140, height=40, font=("Arial", 13, "bold"),
            command=self.save
        ).pack(side="right")

        # Fill Data if Edit
        if data:
            self.ent_code.insert(0, data.course_code)
            self.ent_name.insert(0, data.course_name)
            self.ent_credits.insert(0, str(data.credits))
            self.txt_desc.insert("0.0", data.description if data.description else '')
            self.ent_prereq.insert(0, data.prerequisites_str if hasattr(data, 'prerequisites_str') and data.prerequisites_str else '')
            self.ent_code.configure(state="disabled")

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _add_field(self, parent, r, c, label, placeholder, width=300):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#374151").grid(row=r*2, column=c, sticky="w", pady=(10, 5))
        ent = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width, height=40, border_color="#E5E7EB")
        ent.grid(row=r*2+1, column=c, sticky="w", padx=(0 if c==0 else 10, 0))
        return ent

    def save(self):
        try:
            credits = int(self.ent_credits.get())
        except:
            messagebox.showwarning("Input Error", "Credits must be a number", parent=self)
            return

        # Gọi controller mà không truyền Type nữa
        if self.data: # Update
            success, msg = self.controller.update_course(
                self.data.course_id, self.ent_code.get(), self.ent_name.get(),
                credits, 
                self.txt_desc.get("0.0", "end").strip(), self.ent_prereq.get()
            )
        else: # Create
            success, msg = self.controller.create_course(
                self.ent_code.get(), self.ent_name.get(), credits, 
                self.txt_desc.get("0.0", "end").strip(), self.ent_prereq.get()
            )

        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)