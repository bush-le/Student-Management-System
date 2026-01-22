import customtkinter as ctk
from controllers.student_controller import StudentController

class GradesFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = StudentController(user_id)

        # --- 1. HEADER (Giảm padding) ---
        header_lbl = ctk.CTkLabel(
            self, 
            text="MY GRADES & ACADEMIC RESULTS", 
            font=("Arial", 14, "bold"), 
            text_color="#2A9D8F"
        )
        # Giảm pady từ (20,15) xuống (20, 10)
        header_lbl.pack(anchor="w", pady=(20, 10), padx=30)

        # --- 2. SUMMARY CARD ---
        self.create_summary_card()

        # --- 3. GRADES TABLE ---
        self.create_grades_table()

    def create_summary_card(self):
        # Giảm ipady từ 15 xuống 10 để card mỏng hơn
        card = ctk.CTkFrame(self, fg_color="#F0F9FF", corner_radius=6)
        card.pack(fill="x", padx=30, pady=(0, 20), ipady=10)

        # Left Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=20)

        # GPA Row
        gpa_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        gpa_frame.pack(anchor="w")
        ctk.CTkLabel(gpa_frame, text="Cumulative GPA:", font=("Arial", 14, "bold"), text_color="#333").pack(side="left")
        ctk.CTkLabel(gpa_frame, text="3.80", font=("Arial", 18, "bold"), text_color="#2563EB").pack(side="left", padx=5)

        # Class Row
        class_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        class_frame.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(class_frame, text="Classification:", font=("Arial", 12), text_color="gray").pack(side="left")
        ctk.CTkLabel(class_frame, text="Excellent", font=("Arial", 12, "bold"), text_color="#16A34A").pack(side="left", padx=5)

        # Right Filter
        filter_frame = ctk.CTkFrame(card, fg_color="transparent")
        filter_frame.pack(side="right", padx=20)
        ctk.CTkLabel(filter_frame, text="FILTER BY SEMESTER", font=("Arial", 9, "bold"), text_color="gray").pack(anchor="w", pady=(0, 2))
        
        self.semester_cb = ctk.CTkComboBox(
            filter_frame, 
            values=["All Semesters", "Fall 2024", "Spring 2025"],
            width=150, height=32,
            fg_color="white", text_color="#333",
            button_color="white", button_hover_color="#F3F4F6",
            border_color="#E5E7EB", dropdown_fg_color="white", dropdown_text_color="#333",
            state="readonly"  # <--- THÊM DÒNG NÀY ĐỂ CỐ ĐỊNH (KHÔNG CHO NHẬP TAY)
        )
        self.semester_cb.set("All Semesters")
        self.semester_cb.pack()

    def create_grades_table(self):
        # Container chính
        self.table_container = ctk.CTkFrame(self, fg_color="white")
        self.table_container.pack(fill="both", expand=True, padx=30)
        
        # Cấu hình cột: Cột Tên môn (0) rộng gấp 3 lần các cột điểm
        cols = [3, 1, 1, 1, 1, 1]
        for i, w in enumerate(cols):
            self.table_container.grid_columnconfigure(i, weight=w)

        # --- HEADERS ---
        head_titles = ["COURSE NAME", "ATTENDANCE", "ASSIGNMENTS", "MIDTERM", "FINAL EXAM", "FINAL GRADE"]
        for i, title in enumerate(head_titles):
            # Căn lề trái cho tên môn, căn giữa cho điểm
            sticky = "w" if i == 0 else "ew"
            ctk.CTkLabel(
                self.table_container, 
                text=title, 
                font=("Arial", 10, "bold"), 
                text_color="#9CA3AF"
            ).grid(row=0, column=i, sticky=sticky, pady=(0, 5), padx=5) # Giảm pady header

        # Đường kẻ dưới header
        ctk.CTkFrame(self.table_container, height=1, fg_color="#F3F4F6").grid(row=1, column=0, columnspan=6, sticky="ew", pady=(0, 5))

        # Mock Data (Thay bằng self.controller.view_grades() sau này)
        mock_data = [
            {"name": "Introduction to Programming", "att": "9.5", "ass": "8.0", "mid": "8.5", "final": "9.0", "grade": "8.8"},
            {"name": "Circuit Analysis", "att": "10.0", "ass": "9.0", "mid": "9.5", "final": "9.0", "grade": "9.2"}
        ]

        # Vẽ các hàng
        row_idx = 2
        for item in mock_data:
            self._create_row(row_idx, item)
            row_idx += 2 # +2 vì có dòng kẻ ngang xen giữa

    def _create_row(self, r, data):
        # Pady chung cho hàng -> Giảm xuống 8 để các dòng sát nhau hơn
        common_pady = 8

        # 0: Name
        ctk.CTkLabel(
            self.table_container, text=data['name'], 
            font=("Arial", 12, "bold"), text_color="#333"
        ).grid(row=r, column=0, sticky="w", padx=5, pady=common_pady)

        # 1-4: Component Scores
        keys = ['att', 'ass', 'mid', 'final']
        for i, key in enumerate(keys, start=1):
            ctk.CTkLabel(
                self.table_container, text=data[key], 
                font=("Arial", 12), text_color="gray"
            ).grid(row=r, column=i, sticky="ew", pady=common_pady)

        # 5: Final Grade (Màu xanh Teal đậm)
        ctk.CTkLabel(
            self.table_container, text=data['grade'], 
            font=("Arial", 13, "bold"), text_color="#2A9D8F"
        ).grid(row=r, column=5, sticky="ew", pady=common_pady)

        # Đường kẻ mờ phân cách các hàng
        ctk.CTkFrame(self.table_container, height=1, fg_color="#F3F4F6").grid(row=r+1, column=0, columnspan=6, sticky="ew")