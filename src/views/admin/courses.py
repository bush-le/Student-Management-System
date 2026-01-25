import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController
from utils.threading_helper import run_in_background

class CoursesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # Pagination configuration
        self.current_page = 1
        self.per_page = 10
        self.total_pages = 1 # Initialize total pages
        self.total_items = 0
        # --- FIXED WIDTH CONFIGURATION (PIXEL) ---
        # [Code, Name, Credits, Prereq, Actions]
        self.col_widths = [100, 350, 100, 250, 150]

        # 1. Toolbar
        self.create_toolbar()

        # 2. Table Header 
        self.create_table_header()

        # 3. Table Frame (Regular frame, not scrollable)
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10) # Regular frame, not scrollable
        self.table_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 4. Pagination Controls
        self.create_pagination_controls()
        
        # 5. Load Data
        self.load_data()

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        toolbar.pack(fill="x", pady=(0, 15))
        
        self.search_ent = ctk.CTkEntry(
            toolbar, placeholder_text="Search course...", 
            width=300, height=40, border_color="#E5E7EB", border_width=1
        )
        self.search_ent.pack(side="left")
        self.search_ent.bind("<Return>", lambda e: self.perform_search())
        
        btn_search = ctk.CTkButton(toolbar, text="Search", width=60, height=40, fg_color="#0F766E", command=self.perform_search)
        btn_search.pack(side="left", padx=5)
        
        btn_add = ctk.CTkButton(
            toolbar, text="+ Add Course", fg_color="#0F766E", hover_color="#115E59", height=40,
            font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=45, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        
        cols = ["CODE", "COURSE NAME", "CREDITS", "PREREQUISITES", "ACTIONS"]
        
        for i, text in enumerate(cols):
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), 
                text_color="#374151", anchor="w",
                width=self.col_widths[i]
            ).grid(row=0, column=i, sticky="ew", padx=5, pady=10)

    def create_pagination_controls(self):
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.pagination_frame.pack(fill="x", pady=(0, 10))
        
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 12), text_color="gray")
        self.page_label.pack(side="left", padx=20)
        
        btn_box = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        btn_box.pack(side="right", padx=20)

        self.prev_btn = ctk.CTkButton(
            btn_box, text="← Previous", width=90, height=32,
            fg_color="white", text_color="#333", border_color="#D1D5DB", border_width=1,
            hover_color="#F3F4F6", state="disabled", command=self.prev_page
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            btn_box, text="Next →", width=90, height=32,
            fg_color="#0F766E", text_color="white", hover_color="#115E59",
            state="disabled", command=self.next_page
        )
        self.next_btn.pack(side="left", padx=5)

    def load_data(self): # Load course data
        for w in self.table_frame.winfo_children(): w.destroy()
        ctk.CTkLabel(self.table_frame, text="Loading data...", text_color="gray").pack(pady=20)
        
        run_in_background( # Run data fetching in background
            self._fetch_courses,
            on_complete=self._render_courses,
            tk_root=self.winfo_toplevel()
        )

    def perform_search(self):
        self.current_page = 1
        self.load_data()

    def _fetch_courses(self):
        try:
            search_query = self.search_ent.get().strip()
            # 1. Get current page data
            courses, total_items = self.controller.get_all_courses(
                page=self.current_page, per_page=self.per_page, search_query=search_query
            )
            
            total_pages = (total_items + self.per_page - 1) // self.per_page
            
            return {
                'data': courses,
                'page': self.current_page,
                'per_page': self.per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': self.current_page < total_pages,
                'has_prev': self.current_page > 1
            }
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _render_courses(self, result):
        if not self.winfo_exists(): return
        for w in self.table_frame.winfo_children(): w.destroy() # Clear existing widgets

        if not result or not result['data']:
            ctk.CTkLabel(self.table_frame, text="No courses found.", text_color="gray").pack(pady=20)
            self.page_label.configure(text="0 items")
            self.prev_btn.configure(state="disabled"); self.next_btn.configure(state="disabled")
            return

        self.total_pages = result['total_pages'] # Update total pages
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages} ({result['total_items']} items)")
        
        self.prev_btn.configure(
            state="normal" if result['has_prev'] else "disabled", 
            fg_color="white" if result['has_prev'] else "#F3F4F6"
        )
        self.next_btn.configure(
            state="normal" if result['has_next'] else "disabled", 
            fg_color="#0F766E" if result['has_next'] else "#9CA3AF"
        )

        for idx, item in enumerate(result['data']): # Render each course item
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
        
        # 1. Code 
        ctk.CTkLabel(row, text=data.course_code, font=("Arial", 12, "bold"), text_color="#333", anchor="w", 
                     width=self.col_widths[0]).grid(row=0, column=0, sticky="ew", padx=5, pady=12)
        
        # 2. Name 
        ctk.CTkLabel(row, text=data.course_name, font=("Arial", 12), text_color="#333", anchor="w",
                     width=self.col_widths[1]).grid(row=0, column=1, sticky="ew", padx=5)
        
        # 3. Credits
        ctk.CTkLabel(row, text=str(data.credits), font=("Arial", 12), text_color="#555", anchor="w",
                     width=self.col_widths[2]).grid(row=0, column=2, sticky="ew", padx=5)

        # 4. Prereq
        prereq = data.prerequisites_id if hasattr(data, 'prerequisites_id') and data.prerequisites_id else '-'
        ctk.CTkLabel(row, text=prereq, font=("Arial", 12), text_color="gray", anchor="w",
                     width=self.col_widths[3]).grid(row=0, column=3, sticky="ew", padx=5)
        # 5. Actions
        actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[4])
        actions.grid(row=0, column=4, sticky="ew", padx=5)
        actions.grid_propagate(False) 
        
        ctk.CTkButton(actions, text="Edit", width=40, height=28, fg_color="transparent", text_color="#3B82F6", 
                      hover_color="#EFF6FF", command=lambda: self.open_edit_dialog(data)).pack(side="left", padx=5)
        
        ctk.CTkButton(actions, text="Del", width=40, height=28, fg_color="transparent", text_color="#EF4444", 
                      hover_color="#FEF2F2", command=lambda: self.delete_item(data.course_id)).pack(side="left")

        ctk.CTkFrame(self.table_frame, height=1, fg_color="#F3F4F6").pack(fill="x")

    def delete_item(self, cid):
        if messagebox.askyesno("Confirm", "Delete this course?"):
            run_in_background(
                lambda: self.controller.delete_course(cid),
                lambda res: self.load_data() if res[0] else messagebox.showerror("Error", res[1]),
                tk_root=self.winfo_toplevel()
            )

    def open_add_dialog(self):
        CourseDialog(self, "Add New Course", self.controller, self.load_data)

    def open_edit_dialog(self, data):
        CourseDialog(self, "Edit Course", self.controller, self.load_data, data)

# ==========================================
# POPUP: ADD/EDIT COURSE (Unchanged)
# ==========================================
class CourseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("700x550")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=40)
        # Form container
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        self.ent_code = self._add_field(form, 0, 0, "Course Code", "e.g. CS101")
        self.ent_name = self._add_field(form, 0, 1, "Course Name", "Introduction to Programming")
        self.ent_credits = self._add_field(form, 1, 0, "Credits", "3")
        
        ctk.CTkLabel(form, text="Description", font=("Arial", 12, "bold"), text_color="#374151").grid(row=4, column=0, sticky="w", pady=(10, 5)) # Description label
        self.txt_desc = ctk.CTkTextbox(form, height=60, border_color="#E5E7EB", border_width=1, fg_color="white", text_color="black")
        self.txt_desc.grid(row=5, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(form, text="Prerequisites (codes)", font=("Arial", 12, "bold"), text_color="#374151").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 5)) # Prerequisites label
        self.ent_prereq = ctk.CTkEntry(form, placeholder_text="e.g. CS101, MATH101", height=40, border_color="#E5E7EB")
        self.ent_prereq.grid(row=7, column=0, columnspan=2, sticky="ew")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=30)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, text_color="black", hover_color="#F3F4F6", width=100, height=40, command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save Course", fg_color="#0F766E", hover_color="#115E59", width=140, height=40, font=("Arial", 13, "bold"), command=self.save).pack(side="right")

        if data:
            self.ent_code.insert(0, data.course_code)
            self.ent_name.insert(0, data.course_name)
            self.ent_credits.insert(0, str(data.credits))
            self.txt_desc.insert("0.0", data.description if data.description else '')
            self.ent_prereq.insert(0, data.prerequisites_id if hasattr(data, 'prerequisites_id') and data.prerequisites_id else '')
            self.ent_code.configure(state="disabled")

        self.lift()
        self.after(100, lambda: [self.focus_force(), self.grab_set()])

    def _add_field(self, parent, r, c, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#374151").grid(row=r*2, column=c, sticky="w", pady=(10, 5), padx=(0 if c==0 else 10, 0))
        ent = ctk.CTkEntry(parent, placeholder_text=placeholder, height=40, border_color="#E5E7EB")
        ent.grid(row=r*2+1, column=c, sticky="ew", padx=(0 if c==0 else 10, 0))
        return ent

    def save(self):
        try:
            credits = int(self.ent_credits.get())
        except:
            messagebox.showwarning("Input Error", "Credits must be a number", parent=self)
            return

        # Gather data from widgets in the main thread (Thread Safety)
        code = self.ent_code.get()
        name = self.ent_name.get()
        desc = self.txt_desc.get("0.0", "end").strip()
        prereq = self.ent_prereq.get()

        def _save_task():
            if self.data:
                return self.controller.update_course(
                    self.data.course_id, code, name,
                    credits, desc, prereq
                )
            else:
                return self.controller.create_course(
                    code, name, credits,
                    desc, prereq
                )

        def _on_complete(result):
            success, msg = result
            if success:
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)

        run_in_background(_save_task, _on_complete, tk_root=self.winfo_toplevel())