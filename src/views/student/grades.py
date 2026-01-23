import customtkinter as ctk
from controllers.student_controller import StudentController

class GradesFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = StudentController(user_id)
        
        # --- CẤU HÌNH GIAO DIỆN ---
        self.COLOR_PRIMARY = "#0F766E"
        self.COLOR_TEXT = "#333333"
        self.COLOR_PASS = "#16A34A"  # Xanh lá
        self.COLOR_FAIL = "#DC2626"  # Đỏ

        # Cấu hình độ rộng cột (Tổng ~900px)
        # [Code, Course Name, Credits, Midterm, Final, Total, Status]
        self.col_widths = [80, 300, 80, 100, 100, 100, 100]

        # --- LOAD DATA ---
        self.load_data()

        # --- UI LAYOUT ---
        # 1. Header & Stats
        self.create_header_stats()

        # 2. Filter Toolbar
        self.create_toolbar()

        # 3. Table Header
        self.create_table_header()

        # 4. Grades List (Scrollable)
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.scroll_area.pack(fill="both", expand=True, pady=(0, 20))

        # 5. Render Rows
        self.render_table()

    def load_data(self):
        try:
            # Lấy dữ liệu từ DB
            data = self.controller.view_grades()
            self.transcript = data.get('transcript', [])
            self.gpa = data.get('cumulative_gpa', 0.0)
            
            # Tính tổng tín chỉ tích lũy (Chỉ tính môn đã đậu, ví dụ điểm >= 4.0)
            self.total_credits = sum(
                g.credits for g in self.transcript 
                if g.total is not None and g.total >= 4.0
            )
        except Exception as e:
            print(f"Error loading grades: {e}")
            self.transcript = []
            self.gpa = 0.0
            self.total_credits = 0

    def create_header_stats(self):
        # Container cho Stats
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(10, 20))

        # 1. GPA Card
        self._create_stat_card(stats_frame, "Cumulative GPA", f"{self.gpa:.2f}", "#EFF6FF", "#2563EB", side="left")
        
        # 2. Credits Card
        self._create_stat_card(stats_frame, "Credits Earned", str(self.total_credits), "#F0FDF4", "#16A34A", side="left")
        
        # 3. Status Card (Dựa trên GPA)
        status_text = "Good Standing" if self.gpa >= 2.0 else "Warning"
        status_color = "#16A34A" if self.gpa >= 2.0 else "#DC2626"
        bg_color = "#F0FDF4" if self.gpa >= 2.0 else "#FEF2F2"
        self._create_stat_card(stats_frame, "Academic Status", status_text, bg_color, status_color, side="left")

    def _create_stat_card(self, parent, title, value, bg, color, side):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(side=side, fill="y", padx=(0, 15), ipadx=10, ipady=5)
        
        # Icon/Color bar bên trái
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

        # Filter Dropdown
        self.semester_cb = ctk.CTkComboBox(
            toolbar, values=["All Semesters", "Fall 2024", "Spring 2025"],
            width=160, height=35, border_color="#E5E7EB", 
            fg_color="white", text_color="#333", state="readonly"
        )
        self.semester_cb.set("All Semesters")
        self.semester_cb.pack(side="right")
        ctk.CTkLabel(toolbar, text="Filter:", font=("Arial", 12, "bold"), text_color="gray").pack(side="right", padx=10)

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
        # Xóa cũ
        for w in self.scroll_area.winfo_children(): w.destroy()
        
        if not self.transcript:
            ctk.CTkLabel(self.scroll_area, text="No grade records found.", text_color="gray", font=("Arial", 12)).pack(pady=30)
            return

        for idx, grade in enumerate(self.transcript):
            self.create_row(grade, idx)

    def create_row(self, grade, idx):
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB"
        row = ctk.CTkFrame(self.scroll_area, fg_color=bg_color, corner_radius=0, height=45)
        row.pack(fill="x")
        
        # Helper format
        def fmt(v): return str(v) if v is not None else "-"
        
        # 1. Course Code (Giả sử bạn có trường này, nếu không thì để trống)
        # Nếu model grade chưa có course_code, bạn cần join bảng ở Repo. Tạm thời hiển thị placeholder.
        code = getattr(grade, 'course_code', '---') 
        ctk.CTkLabel(row, text=code, font=("Arial", 12, "bold"), text_color="#333", anchor="w", width=self.col_widths[0]).grid(row=0, column=0, padx=5, pady=10)
        
        # 2. Name
        name = grade.course_name if grade.course_name else "Unknown Course"
        ctk.CTkLabel(row, text=name, font=("Arial", 12), text_color="#333", anchor="w", width=self.col_widths[1]).grid(row=0, column=1, padx=5)
        
        # 3. Credits
        cred = str(getattr(grade, 'credits', 3)) # Default 3 nếu chưa join
        ctk.CTkLabel(row, text=cred, font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[2]).grid(row=0, column=2, padx=5)

        # 4. Midterm
        ctk.CTkLabel(row, text=fmt(grade.midterm), font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[3]).grid(row=0, column=3, padx=5)
        
        # 5. Final
        ctk.CTkLabel(row, text=fmt(grade.final), font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[4]).grid(row=0, column=4, padx=5)
        
        # 6. Total
        total_val = grade.total
        total_str = fmt(total_val)
        # Highlight điểm cao
        total_color = self.COLOR_PRIMARY if total_val and total_val >= 8.5 else "#333"
        ctk.CTkLabel(row, text=total_str, font=("Arial", 12, "bold"), text_color=total_color, anchor="w", width=self.col_widths[5]).grid(row=0, column=5, padx=5)

        # 7. Status Badge
        if total_val is not None:
            status = "PASSED" if total_val >= 4.0 else "FAILED" # Giả định thang 10, >=4 là đậu
            fg = self.COLOR_PASS if total_val >= 4.0 else self.COLOR_FAIL
        else:
            status = "IN PROGRESS"
            fg = "gray"
            
        ctk.CTkLabel(row, text=status, font=("Arial", 10, "bold"), text_color=fg, anchor="w", width=self.col_widths[6]).grid(row=0, column=6, padx=5)

        # Divider
        ctk.CTkFrame(self.scroll_area, height=1, fg_color="#F3F4F6").pack(fill="x")