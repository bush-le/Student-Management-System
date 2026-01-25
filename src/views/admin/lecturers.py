import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController
from utils.threading_helper import run_in_background

class LecturersFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # Pagination configuration
        self.current_page = 1
        self.per_page = 5
        self.total_pages = 1 # Initialize total pages
        self.total_items = 0
        # --- FIXED WIDTH CONFIGURATION (PIXEL) ---
        self.col_widths = [80, 200, 200, 120, 150, 100, 120]

        # 1. Toolbar
        self.create_toolbar()

        # 2. Table Header
        self.create_table_header()

        # 3. Table Container
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 4. Pagination Controls
        self.create_pagination_controls()

        # 5. Load Data
        self.load_data()

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        toolbar.pack(fill="x", pady=(0, 15))
        
        self.search_ent = ctk.CTkEntry(
            toolbar, placeholder_text="Search lecturer...", 
            width=300, height=40, border_color="#E5E7EB", border_width=1
        )
        self.search_ent.pack(side="left")
        self.search_ent.bind("<Return>", lambda e: self.perform_search())
        
        btn_search = ctk.CTkButton(toolbar, text="Search", width=60, height=40, fg_color="#0F766E", command=self.perform_search)
        btn_search.pack(side="left", padx=5)
        
        btn_add = ctk.CTkButton(
            toolbar, text="+ Add Lecturer", fg_color="#0F766E", hover_color="#115E59", height=40,
            font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=45, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        
        cols = ["ID", "FULL NAME", "EMAIL", "PHONE", "DEPT", "DEGREE", "ACTIONS"]
        
        for i, text in enumerate(cols):
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), 
                text_color="#374151", anchor="w",
                width=self.col_widths[i]
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=10)

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

    def load_data(self): # Load data into the table
        for w in self.table_frame.winfo_children(): w.destroy()
        ctk.CTkLabel(self.table_frame, text="Loading data...", text_color="gray").pack(pady=20)
        
        run_in_background( # Run data fetching in background
            self._fetch_lecturers,
            on_complete=self._render_lecturers,
            tk_root=self.winfo_toplevel()
        )
    
    def perform_search(self):
        self.current_page = 1
        self.load_data()

    def _fetch_lecturers(self):
        try:
            search_query = self.search_ent.get().strip()
            # 1. Get current page data
            lecturers, total_items = self.controller.get_all_lecturers(
                page=self.current_page, per_page=self.per_page, search_query=search_query
            )
            
            total_pages = (total_items + self.per_page - 1) // self.per_page
            
            return {
                'data': lecturers,
                'page': self.current_page,
                'per_page': self.per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': self.current_page < total_pages,
                'has_prev': self.current_page > 1
            }
        except Exception as e:
            print(f"Error fetching: {e}")
            return None
    
    def _render_lecturers(self, result):
        if not self.winfo_exists(): return
        for w in self.table_frame.winfo_children(): w.destroy()
        
        if not result or not result['data']:
            ctk.CTkLabel(self.table_frame, text="No lecturers found.", text_color="gray").pack(pady=20)
            self.page_label.configure(text="0 items")
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            return

        self.total_pages = result['total_pages']
        self.total_items = result['total_items']
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages} ({self.total_items} items)")
        
        # --- FIX ERROR 2: SyntaxError (Removed equals sign after else) ---
        self.prev_btn.configure(
            state="normal" if result['has_prev'] else "disabled", 
            fg_color="white" if result['has_prev'] else "#F3F4F6"
        )
        self.next_btn.configure(
            state="normal" if result['has_next'] else "disabled", 
            fg_color="#0F766E" if result['has_next'] else "#9CA3AF"
        )

        for idx, item in enumerate(result['data']):
            self.create_row(item, idx)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def create_row(self, data, idx):
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB" # Alternating row background color
        row = ctk.CTkFrame(self.table_frame, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        
        ctk.CTkLabel(row, text=data.lecturer_code, font=("Arial", 12, "bold"), text_color="#333", anchor="w", width=self.col_widths[0]).grid(row=0, column=0, sticky="ew", padx=10, pady=12)
        ctk.CTkLabel(row, text=data.full_name, font=("Arial", 12), text_color="#333", anchor="w", width=self.col_widths[1]).grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data.email, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[2]).grid(row=0, column=2, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data.phone, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[3]).grid(row=0, column=3, sticky="ew", padx=10)
        
        dept = data.dept_name if data.dept_name else 'N/A'
        ctk.CTkLabel(row, text=dept, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[4]).grid(row=0, column=4, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data.degree, font=("Arial", 11, "bold"), text_color="#0F766E", anchor="w", width=self.col_widths[5]).grid(row=0, column=5, sticky="ew", padx=10)

        actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[6])
        actions.grid(row=0, column=6, sticky="ew", padx=5)
        actions.grid_propagate(False)
        # Edit and Delete buttons
        self._action_btn(actions, "Edit", "#3B82F6", lambda: self.open_edit_dialog(data))
        ctk.CTkLabel(actions, text=" ", width=5).pack(side="left")
        self._action_btn(actions, "Del", "#EF4444", lambda: self.delete_item(data.lecturer_id))
        
        ctk.CTkFrame(self.table_frame, height=1, fg_color="#F3F4F6").pack(fill="x")

    def _action_btn(self, parent, text, color, cmd):
        ctk.CTkButton(
            parent, text=text, width=40, height=28, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left")

    def delete_item(self, lid):
        if messagebox.askyesno("Confirm", "Delete this lecturer?"):
            run_in_background(
                lambda: self.controller.delete_lecturer(lid),
                lambda res: self.load_data() if res[0] else messagebox.showerror("Error", res[1]),
                tk_root=self.winfo_toplevel()
            )

    def open_add_dialog(self):
        LecturerDialog(self, "Add New Lecturer", self.controller, self.load_data)

    def open_edit_dialog(self, data):
        LecturerDialog(self, "Edit Lecturer", self.controller, self.load_data, data)

# ==========================================
# POPUP: ADD/EDIT LECTURER (FIXED DEPT MAP)
# ==========================================
class LecturerDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        
        self.departments = self.controller.get_all_departments() # Fetch departments for dropdown
        self.dept_map = {d.dept_name: d.dept_id for d in self.departments}
        dept_names = list(self.dept_map.keys())
        
        self.geometry("700x480")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=40)
        # Form fields
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        self.ent_id = self._add_field(form, 0, 0, "Lecturer ID", "e.g. L101")
        self.ent_name = self._add_field(form, 0, 1, "Full Name", "e.g. Phan Gia Kiet")
        self.ent_email = self._add_field(form, 1, 0, "Email Address", "lecturer@test.com")
        self.ent_phone = self._add_field(form, 1, 1, "Phone Number", "0912345678")

        ctk.CTkLabel(form, text="Department", font=("Arial", 12, "bold"), text_color="#374151").grid(row=4, column=0, sticky="w", pady=(10, 5))
        self.combo_dept = ctk.CTkComboBox( # Department dropdown
            form, values=dept_names, height=40, border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_dept.grid(row=5, column=0, sticky="ew", padx=(0, 20))

        self.ent_degree = self._add_field(form, 2, 1, "Academic Degree", "e.g. Ph.D. in AI")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent") # Buttons container
        btn_frame.pack(fill="x", padx=40, pady=30)
        
        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
            text_color="black", hover_color="#F3F4F6", width=100, height=40,
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="Save Details", fg_color="#0F766E", hover_color="#115E59", 
            width=140, height=40, font=("Arial", 13, "bold"),
            command=self.save
        ).pack(side="right") # Save button 

        if data:
            self.ent_id.insert(0, data.lecturer_code)
            self.ent_name.insert(0, data.full_name)
            self.ent_email.insert(0, data.email)
            self.ent_phone.insert(0, data.phone)
            
            current_dept = data.dept_name if data.dept_name else ""
            if current_dept in self.dept_map:
                self.combo_dept.set(current_dept)
            else:
                self.combo_dept.set(dept_names[0] if dept_names else "")
            # Set degree and disable ID field
            self.ent_degree.delete(0, 'end'); self.ent_degree.insert(0, data.degree)
            self.ent_id.configure(state="disabled") 

        self.lift()
        self.after(100, lambda: [self.focus_force(), self.grab_set()])

    def _add_field(self, parent, r, c, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#374151").grid(row=r*2, column=c, sticky="w", pady=(10, 5), padx=(0 if c==0 else 20, 0))
        ent = ctk.CTkEntry(parent, placeholder_text=placeholder, height=40, border_color="#E5E7EB")
        ent.grid(row=r*2+1, column=c, sticky="ew", padx=(0 if c==0 else 20, 0))
        return ent

    def save(self):
        dept_name = self.combo_dept.get() # Get selected department name
        dept_id = self.dept_map.get(dept_name)
        
        if not dept_id:
            messagebox.showerror("Error", "Please select a valid department", parent=self)
            return

        # Gather data from widgets in the main thread (Thread Safety)
        l_id = self.ent_id.get()
        name = self.ent_name.get()
        email = self.ent_email.get()
        phone = self.ent_phone.get()
        degree = self.ent_degree.get()

        def _save_task():
            if self.data:
                return self.controller.update_lecturer(
                    self.data.lecturer_id, name, email, 
                    phone, dept_id, degree
                )
            else:
                return self.controller.create_lecturer(
                    l_id, name, email, 
                    phone, dept_id, degree
                )

        def _on_complete(result):
            success, msg = result
            if success:
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)

        run_in_background(_save_task, _on_complete, tk_root=self.winfo_toplevel())