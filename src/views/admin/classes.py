import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class ClassesFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = AdminController(user_id)
        
        self.COLOR_PRIMARY = "#10B981"
        self.COLOR_ICON = "#4B5563"

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
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="ACTIVE CLASSES", font=("Arial", 20, "bold"), text_color="#115E59").pack(anchor="w")

        ctk.CTkButton(header, text="+ Schedule Class", fg_color=self.COLOR_PRIMARY, hover_color="#059669", 
                      width=140, command=self.open_add_dialog).pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", height=45, corner_radius=0)
        h_frame.pack(fill="x", padx=20)
        
        cols = [("COURSE", 2), ("CURRENT LECTURER", 2), ("SCHEDULE", 2), ("ROOM", 1), ("CAPACITY", 1), ("ACTION", 1)]
        for i, (text, w) in enumerate(cols):
            h_frame.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(h_frame, text=text, font=("Arial", 11, "bold"), text_color="gray", anchor="w" if i<5 else "center").grid(row=0, column=i, sticky="ew", padx=10, pady=12)

    def load_data(self):
        for w in self.scroll_area.winfo_children(): w.destroy()
        classes = self.controller.get_all_classes_details()
        for c in classes: self.create_row(c)

    def create_row(self, data):
        row = ctk.CTkFrame(self.scroll_area, fg_color="white", corner_radius=0)
        row.pack(fill="x", pady=1)
        
        weights = [2, 2, 2, 1, 1, 1]
        for i, w in enumerate(weights): row.grid_columnconfigure(i, weight=w)

        # Course Name
        ctk.CTkLabel(row, text=data['course_name'], font=("Arial", 12, "bold"), text_color="#333", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=15)
        
        # Lecturer (Icon + Name)
        lec_frame = ctk.CTkFrame(row, fg_color="transparent")
        lec_frame.grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(lec_frame, text="👤", text_color="gray").pack(side="left")
        lec_name = data['lecturer_name'] if data['lecturer_name'] else "Unassigned"
        lec_color = "#333" if data['lecturer_name'] else "gray"
        ctk.CTkLabel(lec_frame, text=lec_name, text_color=lec_color).pack(side="left", padx=5)

        # Schedule
        # DB store: "Monday 10:00-11:30" -> Split to display nicely
        sched = data.get('schedule', 'TBA')
        ctk.CTkLabel(row, text=sched, text_color="#555", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)

        # Room
        ctk.CTkLabel(row, text=data['room'], text_color="#555", anchor="w").grid(row=0, column=3, sticky="ew", padx=10)

        # Capacity (Enrolled / Max)
        cap_text = f"{data.get('current_enrolled', 0)} / {data['max_capacity']}"
        ctk.CTkLabel(row, text=cap_text, font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=4, sticky="ew", padx=10)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5)
        
        # Assign Lecturer Btn
        ctk.CTkButton(actions, text="👤+", width=30, fg_color="transparent", text_color="#4F46E5", hover_color="#EEF2FF", 
                      font=("Arial", 14), command=lambda: self.open_assign_dialog(data)).pack(side="left")
        
        # Edit Btn
        ctk.CTkButton(actions, text="✎", width=30, fg_color="transparent", text_color="#3B82F6", hover_color="#EFF6FF", 
                      font=("Arial", 16), command=lambda: self.open_edit_dialog(data)).pack(side="left")
        
        # Delete Btn
        ctk.CTkButton(actions, text="🗑", width=30, fg_color="transparent", text_color="#EF4444", hover_color="#FEF2F2", 
                      font=("Arial", 16), command=lambda: self.delete_item(data['class_id'])).pack(side="left")

        ctk.CTkFrame(self.scroll_area, height=1, fg_color="#F3F4F6").pack(fill="x")

    def delete_item(self, cid):
        if messagebox.askyesno("Confirm", "Delete this class?"):
            success, msg = self.controller.delete_class(cid)
            if success: self.load_data()
            else: messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        ClassDialog(self, "Schedule New Class", self.controller, self.load_data)

    def open_edit_dialog(self, data):
        ClassDialog(self, "Edit Class Details", self.controller, self.load_data, data)

    def open_assign_dialog(self, data):
        AssignLecturerDialog(self, data, self.controller, self.load_data)


# ==========================================
# POPUP: SCHEDULE/EDIT CLASS
# ==========================================
class ClassDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("600x550")
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(pady=20, anchor="w", padx=30)

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # 1. Course Dropdown (Lấy từ DB)
        ctk.CTkLabel(form, text="Course", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(5, 5))
        
        courses = self.controller.get_all_courses() # Reuse existing method
        course_names = [f"{c['course_code']} - {c['course_name']}" for c in courses]
        self.combo_course = ctk.CTkComboBox(form, values=course_names, width=540, height=35)
        self.combo_course.pack()

        # 2. Semester & Room (Row)
        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", pady=10)
        self.ent_sem = self._add_field(r1, "Semester", "e.g. Fall 2024", side="left")
        self.ent_room = self._add_field(r1, "Room", "e.g. A101", side="right")

        # 3. Day & Time (Row)
        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", pady=10)
        
        # Day Dropdown
        f_day = ctk.CTkFrame(r2, fg_color="transparent")
        f_day.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_day, text="Day", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        self.combo_day = ctk.CTkComboBox(f_day, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], height=35)
        self.combo_day.pack(fill="x", pady=5)

        # Time Entry
        self.ent_time = self._add_input_only(r2, "Time Slot", "08:00 - 09:30", side="right")

        # 4. Capacity
        ctk.CTkLabel(form, text="Capacity", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(5, 5))
        self.ent_cap = ctk.CTkEntry(form, placeholder_text="50", width=540, height=35)
        self.ent_cap.pack()

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=30)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#DDD", border_width=1, text_color="black", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save Class", fg_color="#10B981", command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            # Set course info (Logic tìm index hơi phức tạp với combobox, ta set text tạm)
            self.combo_course.set(f"{data['course_code']} - {data['course_name']}")
            self.combo_course.configure(state="disabled") # Không đổi môn khi sửa lớp
            
            self.ent_room.insert(0, data['room'])
            self.ent_cap.insert(0, str(data['max_capacity']))
            
            # Parse Schedule "Monday 10:00 - 11:30"
            sched_parts = data['schedule'].split(' ', 1)
            if len(sched_parts) == 2:
                self.combo_day.set(sched_parts[0])
                self.ent_time.insert(0, sched_parts[1])

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _add_field(self, parent, label, placeholder, side):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, fill="x", expand=True, padx=(0 if side=="left" else 5, 0 if side=="right" else 5))
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        ent = ctk.CTkEntry(f, placeholder_text=placeholder, height=35)
        ent.pack(fill="x", pady=5)
        return ent

    def _add_input_only(self, parent, label, placeholder, side):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        ent = ctk.CTkEntry(f, placeholder_text=placeholder, height=35)
        ent.pack(fill="x", pady=5)
        return ent

    def save(self):
        # Parse inputs
        course_str = self.combo_course.get()
        course_code = course_str.split(' - ')[0]
        
        # Tìm course_id từ code (Cần logic tốt hơn, ở đây loop qua list cũ)
        courses = self.controller.get_all_courses()
        course_id = next((c['course_id'] for c in courses if c['course_code'] == course_code), None)

        schedule = f"{self.combo_day.get()} {self.ent_time.get()}"
        
        if self.data: # Update
            success, msg = self.controller.update_class(
                self.data['class_id'], self.ent_room.get(), schedule, self.ent_cap.get()
            )
        else: # Create
            success, msg = self.controller.create_class(
                course_id, self.ent_sem.get(), self.ent_room.get(), schedule, self.ent_cap.get()
            )

        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


# ==========================================
# POPUP: ASSIGN LECTURER
# ==========================================
class AssignLecturerDialog(ctk.CTkToplevel):
    def __init__(self, parent, class_data, controller, callback):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.class_data = class_data
        
        self.title("Assign Lecturer")
        self.geometry("500x450")
        self.transient(parent)
        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="Assign Lecturer", font=("Arial", 18, "bold"), text_color="#333").pack(pady=20, anchor="w", padx=30)

        # 1. Class Context Box (Blue Background)
        ctx_frame = ctk.CTkFrame(self, fg_color="#F0F9FF", corner_radius=8, border_color="#BAE6FD", border_width=1)
        ctx_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(ctx_frame, text="CLASS CONTEXT", font=("Arial", 10, "bold"), text_color="#3B82F6").pack(anchor="w", padx=15, pady=(10, 5))
        
        self._ctx_row(ctx_frame, "Course", class_data['course_name'], "Time Slot", class_data['schedule'])
        self._ctx_row(ctx_frame, "Room", class_data['room'], "Capacity", f"{class_data['max_capacity']} Students")
        ctk.CTkFrame(ctx_frame, height=10, fg_color="transparent").pack() # Spacer

        # 2. Select Lecturer
        ctk.CTkLabel(self, text="Select Lecturer", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", padx=30)
        
        # Lấy danh sách giảng viên
        lecturers = self.controller.get_all_lecturers()
        # Format: "Name (Code)"
        self.lec_map = {f"{l['full_name']} ({l['lecturer_code']})": l['lecturer_id'] for l in lecturers}
        
        self.combo_lec = ctk.CTkComboBox(self, values=list(self.lec_map.keys()), width=440, height=40)
        self.combo_lec.pack(padx=30, pady=10)
        
        ctk.CTkLabel(self, text="* Selecting a lecturer will check for schedule conflicts.", font=("Arial", 10), text_color="gray").pack(anchor="w", padx=30)

        # 3. Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=40)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#DDD", border_width=1, text_color="black", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Confirm Assignment", fg_color="#0F766E", command=self.confirm).pack(side="right")

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def _ctx_row(self, parent, l1, v1, l2, v2):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=2)
        
        # Col 1
        f1 = ctk.CTkFrame(row, fg_color="transparent", width=200)
        f1.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(f1, text=l1, font=("Arial", 10), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(f1, text=v1, font=("Arial", 11, "bold"), text_color="#333").pack(anchor="w")
        
        # Col 2
        f2 = ctk.CTkFrame(row, fg_color="transparent", width=200)
        f2.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(f2, text=l2, font=("Arial", 10), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(f2, text=v2, font=("Arial", 11, "bold"), text_color="#333").pack(anchor="w")

    def confirm(self):
        selection = self.combo_lec.get()
        if not selection or selection not in self.lec_map:
            messagebox.showerror("Error", "Please select a lecturer", parent=self)
            return
            
        lecturer_id = self.lec_map[selection]
        success, msg = self.controller.assign_lecturer_to_class(self.class_data['class_id'], lecturer_id)
        
        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)