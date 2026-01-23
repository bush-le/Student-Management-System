import customtkinter as ctk
from controllers.student_controller import StudentController
from utils.threading_helper import run_in_background

class GradesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # --- UI CONFIGURATION ---
        self.COLOR_PRIMARY = "#0F766E"
        self.COLOR_TEXT = "#333333"
        self.COLOR_PASS = "#16A34A"  # Green
        self.COLOR_FAIL = "#DC2626"  

        # [Code, Course Name, Credits, Midterm, Final, Total, Status]
        self.col_widths = [80, 300, 80, 100, 100, 100, 100]

        # Initialize UI containers first (empty)
        self.create_header_stats_container()
        self.create_toolbar()
        self.create_table_header()
        
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.scroll_area.pack(fill="both", expand=True, pady=(0, 20))

        # --- LOAD DATA ---
        self.load_data_async()

    def load_data_async(self, force=False):
        # Show loading state
        self.loading_lbl = ctk.CTkLabel(self.scroll_area, text="Loading grades...", text_color="gray")
        self.loading_lbl.pack(pady=20)
        
        run_in_background(
            lambda: self._fetch_data(force),
            self._on_data_loaded,
            tk_root=self.winfo_toplevel()
        )
        
    def _fetch_data(self, force):
        try: # Get data from DB
            data = self.controller.view_grades(force_update=force)
            return data
        except Exception as e:
            print(f"Error loading grades: {e}")
            return None

    def _on_data_loaded(self, result):
        if not self.winfo_exists(): return
        if hasattr(self, 'loading_lbl'): self.loading_lbl.destroy()
        
        if not result:
            self.transcript = []
            self.gpa = 0.0
            self.total_credits = 0
        else:
            self.transcript = result.get('transcript', [])
            self.gpa = result.get('cumulative_gpa', 0.0)
            self.total_credits = result.get('earned_credits', 0)
            
        self.filtered_transcript = self.transcript
        self.update_header_stats()
        self.render_table()

    def create_header_stats_container(self):
        # Container for Stats
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(10, 20))

    def update_header_stats(self):
        for w in self.stats_frame.winfo_children(): w.destroy()
        
        # 1. GPA Card
        self._create_stat_card(self.stats_frame, "Cumulative GPA", f"{self.gpa:.2f}", "#EFF6FF", "#2563EB", side="left")
        
        # 2. Credits Card
        self._create_stat_card(self.stats_frame, "Credits Earned", str(self.total_credits), "#F0FDF4", "#16A34A", side="left")
        
        # 3. Status Card (Based on GPA)
        status_text = "Good Standing" if self.gpa >= 2.0 else "Warning"
        status_color = "#16A34A" if self.gpa >= 2.0 else "#DC2626"
        bg_color = "#F0FDF4" if self.gpa >= 2.0 else "#FEF2F2"
        self._create_stat_card(self.stats_frame, "Academic Status", status_text, bg_color, status_color, side="left")

    def _create_stat_card(self, parent, title, value, bg, color, side):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(side=side, fill="y", padx=(0, 15), ipadx=10, ipady=5)
        
        # Left Icon/Color bar
        bar = ctk.CTkFrame(card, width=4, fg_color=color, height=40)
        bar.pack(side="left", padx=(10, 10), pady=10)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", pady=10, padx=(0, 20))
        
        ctk.CTkLabel(content, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(content, text=value, font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=40)
        toolbar.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(toolbar, text="Grade History", font=("Arial", 16, "bold"), text_color="#333").pack(side="left")

        # Refresh Button
        ctk.CTkButton(
            toolbar, text="↻ Refresh", width=80, height=30,
            fg_color="white", text_color="#0F766E", border_width=1, border_color="#CCFBF1",
            font=("Arial", 11, "bold"), command=lambda: self.load_data_async(force=True)
        ).pack(side="right", padx=(10, 0))

        # Filter Dropdown (Dynamic Data)
        self.semester_cb = ctk.CTkComboBox(
            toolbar, values=["All Semesters"],
            width=160, height=35, border_color="#E5E7EB", 
            fg_color="white", text_color="#333", state="readonly",
            command=self._filter_data
        )
        self.semester_cb.set("All Semesters")
        self.semester_cb.pack(side="right")
        ctk.CTkLabel(toolbar, text="Filter:", font=("Arial", 12, "bold"), text_color="gray").pack(side="right", padx=10)
        
        # Load semesters in background to avoid freezing UI
        run_in_background(self._fetch_semesters, self._update_semester_cb, tk_root=self.winfo_toplevel())

    def _fetch_semesters(self):
        try:
            return self.controller.get_all_semesters() if hasattr(self.controller, 'get_all_semesters') else []
        except: return []

    def _filter_data(self, choice):
        if not hasattr(self, 'transcript'): return
        
        if choice == "All Semesters":
            self.filtered_transcript = self.transcript
        else:
            self.filtered_transcript = [
                g for g in self.transcript 
                if str(getattr(g, 'semester_name', getattr(g, 'semester', ''))) == choice
            ]
        self.render_table()

    def _update_semester_cb(self, semesters):
        if not self.winfo_exists() or not semesters: return
        try:
            values = ["All Semesters"] + [s.name for s in semesters]
            self.semester_cb.configure(values=values)
        except: pass

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=45, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        
        cols = ["CODE", "COURSE NAME", "CREDITS", "MIDTERM", "FINAL", "TOTAL", "STATUS"]
        
        for i, text in enumerate(cols):
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), 
                text_color="#374151", anchor="w",
                width=self.col_widths[i] # Fixed Width
            ).grid(row=0, column=i, sticky="ew", padx=5, pady=10)

    def render_table(self):
        # Clear old widgets
        for w in self.scroll_area.winfo_children(): w.destroy()
        
        data = getattr(self, 'filtered_transcript', [])
        if not data:
            ctk.CTkLabel(self.scroll_area, text="No grade records found.", text_color="gray", font=("Arial", 12)).pack(pady=30)
            return

        for idx, grade in enumerate(data):
            self.create_row(grade, idx)

    def create_row(self, grade, idx):
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB"
        row = ctk.CTkFrame(self.scroll_area, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        # Helper format
        def fmt(v): return str(v) if v is not None else "-"
        
        # 1. Course Code (Assuming you have this field, otherwise leave blank)
        code = getattr(grade, 'course_code', '---') 
        ctk.CTkLabel(row, text=code, font=("Arial", 12, "bold"), text_color="#333", anchor="w", width=self.col_widths[0]).grid(row=0, column=0, padx=5, pady=10)
        # 2. Name
        name = grade.course_name if grade.course_name else "Unknown Course"
        ctk.CTkLabel(row, text=name, font=("Arial", 12), text_color="#333", anchor="w", width=self.col_widths[1]).grid(row=0, column=1, padx=5)
        
        # 3. Credits
        cred = str(getattr(grade, 'credits', 3)) # Default 3 if not yet joined
        ctk.CTkLabel(row, text=cred, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[2]).grid(row=0, column=2, padx=5)

        # 4. Midterm
        ctk.CTkLabel(row, text=fmt(grade.midterm), font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[3]).grid(row=0, column=3, padx=5)
        
        # 5. Final
        ctk.CTkLabel(row, text=fmt(grade.final), font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[4]).grid(row=0, column=4, padx=5)
        # 6. Total
        total_val = grade.total
        total_str = fmt(total_val)
        # Highlight high scores
        total_color = self.COLOR_PRIMARY if total_val and total_val >= 8.5 else "#333"
        ctk.CTkLabel(row, text=total_str, font=("Arial", 12, "bold"), text_color=total_color, anchor="w", width=self.col_widths[5]).grid(row=0, column=5, padx=5)
        # 7. Status Badge
        if total_val is not None: 
            status = "PASSED" if total_val >= 4.0 else "FAILED" 
            fg = self.COLOR_PASS if total_val >= 4.0 else self.COLOR_FAIL
        else:
            status = "IN PROGRESS"
            fg = "gray"
            
        ctk.CTkLabel(row, text=status, font=("Arial", 10, "bold"), text_color=fg, anchor="w", width=self.col_widths[6]).grid(row=0, column=6, padx=5)
        # Divider
        ctk.CTkFrame(self.scroll_area, height=1, fg_color="#F3F4F6").pack(fill="x")