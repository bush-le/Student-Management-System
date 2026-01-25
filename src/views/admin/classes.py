import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController
from utils.threading_helper import run_in_background

class ClassesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # Pagination configuration
        self.current_page = 1
        self.per_page = 5
        self.total_pages = 1 # Initialize total pages
        self.total_items = 0
        # --- FIXED WIDTH CONFIGURATION (PIXEL) ---
        self.col_widths = [200, 180, 180, 80, 100, 200]

        # 1. Header
        self.create_header()

        # 2. Table Header
        self.create_table_header()

        # 3. Table Frame
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.table_frame.pack(fill="both", expand=True, pady=(0, 10), padx=20)

        # 4. Pagination Controls
        self.create_pagination_controls()

        # 5. Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=20)
        
        # Title
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="ACTIVE CLASSES", font=("Arial", 20, "bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Manage class schedules and assignments", font=("Arial", 12), text_color="gray").pack(anchor="w")
        
        # Search Box
        self.search_ent = ctk.CTkEntry(header, placeholder_text="Search class...", width=200, height=35, border_color="#E5E7EB")
        self.search_ent.pack(side="left", padx=(20, 10))
        self.search_ent.bind("<Return>", lambda e: self.perform_search())
        ctk.CTkButton(header, text="Search", width=60, height=35, fg_color="#0F766E", command=self.perform_search).pack(side="left")

        # Add Button
        ctk.CTkButton(
            header, text="+ Schedule Class", fg_color="#0F766E", hover_color="#115E59", 
            width=140, height=40, font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        ).pack(side="right")
        
    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=45, corner_radius=5)
        h_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        # Columns: Course, Lecturer, Schedule, Room, Capacity, Action
        cols = ["COURSE", "LECTURER", "SCHEDULE", "ROOM", "CAPACITY", "ACTIONS"]
        
        for i, text in enumerate(cols):
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), text_color="#374151", anchor="w",
                width=self.col_widths[i]
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=12)

    def create_pagination_controls(self):
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.pagination_frame.pack(fill="x", pady=(0, 10))
        
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 12), text_color="gray")
        self.page_label.pack(side="left", padx=20)
        
        btn_box = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        btn_box.pack(side="right", padx=20)

        self.prev_btn = ctk.CTkButton(
            btn_box, text="< Previous", width=90, height=32,
            fg_color="white", text_color="#333", border_color="#D1D5DB", border_width=1,
            hover_color="#F3F4F6", state="disabled", command=self.prev_page
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            btn_box, text="Next >", width=90, height=32,
            fg_color="#0F766E", text_color="white", hover_color="#115E59",
            state="disabled", command=self.next_page
        )
        self.next_btn.pack(side="left", padx=5)

    def load_data(self): # Load class data
        for w in self.table_frame.winfo_children(): w.destroy()
        ctk.CTkLabel(self.table_frame, text="Loading data...", text_color="gray").pack(pady=20)
        
        run_in_background(
            self._fetch_classes,
            on_complete=self._render_classes,
            tk_root=self.winfo_toplevel()
        )
    
    def perform_search(self):
        self.current_page = 1
        self.load_data()

    def _fetch_classes(self):
        try:
            search_query = self.search_ent.get().strip()
            # 1. Get current page data AND total count
            classes, total_items = self.controller.get_all_classes_details(page=self.current_page, per_page=self.per_page, search_query=search_query)
            
            total_pages = (total_items + self.per_page - 1) // self.per_page
            
            return {
                'data': classes,
                'page': self.current_page,
                'per_page': self.per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': self.current_page < total_pages,
                'has_prev': self.current_page > 1
            }
        except Exception as e:
            print(f"Error loading classes: {e}")
            return None

    def _render_classes(self, result):
        if not self.winfo_exists(): return
        for w in self.table_frame.winfo_children(): w.destroy()

        if not result or not result['data']:
            ctk.CTkLabel(self.table_frame, text="No classes found.", text_color="gray").pack(pady=20)
            self.page_label.configure(text="0 items")
            self.prev_btn.configure(state="disabled"); self.next_btn.configure(state="disabled")
            return

        self.total_pages = result['total_pages'] # Update total pages
        self.total_items = result['total_items']
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages} ({self.total_items} items)")
        
        self.prev_btn.configure(
            state="normal" if result['has_prev'] else "disabled", 
            fg_color="white" if result['has_prev'] else "#F3F4F6"
        )
        self.next_btn.configure(
            state="normal" if result['has_next'] else "disabled", 
            fg_color="#0F766E" if result['has_next'] else "#9CA3AF"
        )

        for idx, item in enumerate(result['data']): # Render each class item
            self.create_row(item, idx) 

    def create_row(self, data, idx):
        # Zebra Striping
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB" # Apply alternating row colors 
        
        row = ctk.CTkFrame(self.table_frame, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        
        # 1. Course Name 
        ctk.CTkLabel(row, text=data.course_name, font=("Arial", 12, "bold"), text_color="#333", anchor="w", width=self.col_widths[0]).grid(row=0, column=0, sticky="ew", padx=10, pady=12)
        
        # 2. Lecturer (Text Only - No Icon)
        lec_name = data.lecturer_name if data.lecturer_name else "Unassigned"
        lec_color = "#333" if data.lecturer_name else "#EF4444" # Red if no lecturer assigned
        ctk.CTkLabel(row, text=lec_name, font=("Arial", 12), text_color=lec_color, anchor="w", width=self.col_widths[1]).grid(row=0, column=1, sticky="ew", padx=10)

        # 3. Schedule
        sched = data.schedule if data.schedule else 'TBA'
        ctk.CTkLabel(row, text=sched, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[2]).grid(row=0, column=2, sticky="ew", padx=10)

        # 4. Room
        ctk.CTkLabel(row, text=data.room, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[3]).grid(row=0, column=3, sticky="ew", padx=10)

        # 5. Capacity
        cap_text = f"{data.current_enrolled} / {data.max_capacity}"
        ctk.CTkLabel(row, text=cap_text, font=("Arial", 12, "bold"), text_color="#059669", anchor="w", width=self.col_widths[4]).grid(row=0, column=4, sticky="ew", padx=10)

        # 6. Actions (Text Buttons)
        actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[5])
        actions.grid(row=0, column=5, sticky="ew", padx=10)
        actions.grid_propagate(False)
        # Assign Btn 
        self._action_btn(actions, "Assign", "#4F46E5", lambda: self.open_assign_dialog(data))
        # Edit Btn
        self._action_btn(actions, "Edit", "#3B82F6", lambda: self.open_edit_dialog(data))
        # Delete Btn
        self._action_btn(actions, "Del", "#EF4444", lambda: self.delete_item(data.class_id)) # Delete button

        ctk.CTkFrame(self.table_frame, height=1, fg_color="#F3F4F6").pack(fill="x")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def _action_btn(self, parent, text, color, cmd):
        ctk.CTkButton(
            parent, text=text, width=50, height=30, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left", padx=2)

    def delete_item(self, cid):
        if messagebox.askyesno("Confirm", "Delete this class?"):
            run_in_background(
                lambda: self.controller.delete_class(cid),
                lambda res: self.load_data() if res[0] else messagebox.showerror("Error", res[1]),
                tk_root=self.winfo_toplevel()
            )

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
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=40)
        # Form container 
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)

        # 1. Course Dropdown
        ctk.CTkLabel(form, text="Select Course", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(5, 5))
        
        # Fetch ALL courses for dropdown (disable pagination)
        courses, _ = self.controller.get_all_courses(page=None, per_page=None)
        # Create a map for robust selection
        self.course_map = {f"{c.course_code} - {c.course_name}": c.course_id for c in courses}
        
        self.combo_course = ctk.CTkComboBox(
            form, values=list(self.course_map.keys()), width=520, height=40,
            border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_course.pack()

        # 2. Semester & Room 
        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", pady=10)
        
        # --- SEMESTER DROPDOWN (Connected to DB) ---
        self.semesters = self.controller.get_all_semesters()
        self.sem_map = {s.name: s.semester_id for s in self.semesters}
        
        f_sem = ctk.CTkFrame(r1, fg_color="transparent")
        f_sem.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(f_sem, text="Semester", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        
        self.combo_sem = ctk.CTkComboBox(
            f_sem, values=list(self.sem_map.keys()), height=40, 
            border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_sem.pack(fill="x", pady=5)

        self.ent_room = self._add_field(r1, "Room Number", "e.g. A101", side="right")

        # 3. Day & Time 
        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", pady=10)
        # Day Dropdown
        f_day = ctk.CTkFrame(r2, fg_color="transparent")
        f_day.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(f_day, text="Day of Week", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        self.combo_day = ctk.CTkComboBox(
            f_day, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], 
            height=40, border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_day.pack(fill="x", pady=5)

        # Time Entry 
        self.ent_time = self._add_input_only(r2, "Time Slot", "08:00 - 09:30", side="right")

        # 4. Capacity 
        ctk.CTkLabel(form, text="Max Capacity", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(5, 5))
        self.ent_cap = ctk.CTkEntry(form, placeholder_text="e.g. 50", width=520, height=40, border_color="#E5E7EB")
        self.ent_cap.pack()

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=30)
        
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
            text_color="black", hover_color="#F3F4F6", width=100, height=40,
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="Save Class", fg_color="#0F766E", hover_color="#115E59", 
            width=140, height=40, font=("Arial", 13, "bold"),
            command=self.save
        ).pack(side="right") # Save button 

        # Fill Data if Edit
        if data:
            self.combo_course.set(f"{data.course_code} - {data.course_name}")
            self.combo_course.configure(state="disabled")
            
            # Populate Semester
            # Find name by ID
            sem_name = next((name for name, sid in self.sem_map.items() if sid == data.semester_id), "")
            self.combo_sem.set(sem_name)
            self.combo_sem.configure(state="disabled")
            
            self.ent_room.insert(0, data.room)
            self.ent_cap.insert(0, str(data.max_capacity))
            
            # Simple parsing for display
            sched_parts = data.schedule.split(' ', 1)
            if len(sched_parts) == 2:
                self.combo_day.set(sched_parts[0])
                self.ent_time.insert(0, sched_parts[1])

        self.lift()
        self.after(100, lambda: [self.focus_force(), self.grab_set()])

    def _add_field(self, parent, label, placeholder, side):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, fill="x", expand=True, padx=(0 if side=="left" else 10, 0 if side=="right" else 10))
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        ent = ctk.CTkEntry(f, placeholder_text=placeholder, height=40, border_color="#E5E7EB")
        ent.pack(fill="x", pady=5)
        return ent

    def _add_input_only(self, parent, label, placeholder, side):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        ent = ctk.CTkEntry(f, placeholder_text=placeholder, height=40, border_color="#E5E7EB")
        ent.pack(fill="x", pady=5)
        return ent

    def save(self):
        course_str = self.combo_course.get()
        course_id = self.course_map.get(course_str)
        
        sem_name = self.combo_sem.get()
        semester_id = self.sem_map.get(sem_name)

        if not course_id or not semester_id:
            messagebox.showerror("Error", "Please select valid Course and Semester", parent=self)
            return

        schedule = f"{self.combo_day.get()} {self.ent_time.get()}" if self.combo_day.get() and self.ent_time.get() else ""
        
        # Gather data from widgets in the main thread (Thread Safety)
        room = self.ent_room.get()
        cap = self.ent_cap.get()

        def _save_task():
            if self.data: # Update
                return self.controller.update_class(
                    self.data.class_id, room, schedule, cap
                )
            else: # Create
                return self.controller.create_class(
                    course_id, semester_id, room, schedule, cap
                )

        def _on_complete(result):
            success, msg = result
            if success:
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)

        run_in_background(_save_task, _on_complete, tk_root=self.winfo_toplevel())


# ==========================================
# POPUP: ASSIGN LECTURER (STYLE UPDATE)
# ==========================================
class AssignLecturerDialog(ctk.CTkToplevel):
    def __init__(self, parent, class_data, controller, callback):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.class_data = class_data
        
        self.title("Assign Lecturer")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="Assign Lecturer", font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=30)
        # 1. Class Context Box (Blue Background)
        ctx_frame = ctk.CTkFrame(self, fg_color="#F0F9FF", corner_radius=8, border_color="#BAE6FD", border_width=1)
        ctx_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(ctx_frame, text="CLASS INFORMATION", font=("Arial", 10, "bold"), text_color="#0284C7").pack(anchor="w", padx=15, pady=(15, 5))
        
        # Use Grid for better alignment
        info_grid = ctk.CTkFrame(ctx_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=15, pady=(0, 15))
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)

        self._add_info_item(info_grid, 0, 0, "Course", class_data.course_name)
        self._add_info_item(info_grid, 0, 1, "Time Slot", class_data.schedule if class_data.schedule else "TBA")
        self._add_info_item(info_grid, 1, 0, "Room", class_data.room)
        self._add_info_item(info_grid, 1, 1, "Capacity", f"{class_data.max_capacity} Students")

        # 2. Select Lecturer
        ctk.CTkLabel(self, text="Select Lecturer", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", padx=30)
        
        # Fetch ALL lecturers for dropdown (disable pagination)
        lecturers, _ = self.controller.get_all_lecturers(page=None, per_page=None)
        self.lec_map = {f"{l.full_name} ({l.lecturer_code})": l.lecturer_id for l in lecturers}
        
        self.combo_lec = ctk.CTkComboBox(
            self, values=list(self.lec_map.keys()), width=440, height=40,
            border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_lec.pack(padx=30, pady=10)
        
        ctk.CTkLabel(self, text="* Selecting a lecturer will check for schedule conflicts.", font=("Arial", 11), text_color="#6B7280").pack(anchor="w", padx=30)
        # 3. Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=40)
        
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
            text_color="black", hover_color="#F3F4F6", width=100, height=40,
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="Save Assignment", fg_color="#0F766E", hover_color="#115E59", 
            width=160, height=40, font=("Arial", 13, "bold"),
            command=self.confirm # Confirm assignment button 
        ).pack(side="right")

        self.lift()
        self.after(100, lambda: [self.focus_force(), self.grab_set()])

    def _add_info_item(self, parent, r, c, label, value):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=r, column=c, sticky="ew", pady=5, padx=5)
        ctk.CTkLabel(f, text=label, font=("Arial", 11), text_color="#6B7280").pack(anchor="w")
        ctk.CTkLabel(f, text=str(value), font=("Arial", 12, "bold"), text_color="#111827").pack(anchor="w")

    def confirm(self):
        selection = self.combo_lec.get()
        if not selection or selection not in self.lec_map:
            messagebox.showerror("Error", "Please select a lecturer", parent=self)
            return
            
        lecturer_id = self.lec_map[selection]
        
        def _assign_task():
            # Check for schedule conflicts
            all_classes, _ = self.controller.get_all_classes_details(page=None, per_page=None)
            
            target_sem = self.class_data.semester_id
            target_sched = self.class_data.schedule
            
            if target_sched and target_sched != "TBA":
                for c in all_classes:
                    # Check if lecturer is already teaching in this semester at the same time
                    if c.lecturer_id == lecturer_id and c.semester_id == target_sem:
                        if c.class_id != self.class_data.class_id and c.schedule == target_sched:
                            return False, f"Conflict: Lecturer is busy with {c.course_name} at {c.schedule}"

            return self.controller.assign_lecturer_to_class(self.class_data.class_id, lecturer_id)
            
        def _on_complete(result):
            success, msg = result
            if success:
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)

        run_in_background(_assign_task, _on_complete, tk_root=self.winfo_toplevel())