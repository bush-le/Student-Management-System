import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.student_controller import StudentController

class ScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = StudentController(user_id)
        
        # --- CẤU HÌNH MÀU SẮC ---
        self.COLOR_TEAL = "#4A8B88"      # Màu chủ đạo
        self.COLOR_WEEKEND = "#FFFBEB"   # Màu nền T7, CN
        self.COLOR_CARD_BG = "#E0F2FE"   # Nền thẻ môn học
        self.COLOR_CARD_BORDER = "#BAE6FD"

        # Dictionary lưu tham chiếu các ô grid để điền dữ liệu sau
        # Key: (day_index, slot_index) -> Value: CTkFrame widget
        self.cells = {} 

        # 1. Vẽ Header (Nút chọn ngày)
        self.create_header()

        # 2. Vẽ Khung Lưới (Grid rỗng)
        self.create_grid_structure()

        # 3. Đổ dữ liệu từ Controller vào Lưới
        self.populate_schedule()

    def create_header(self):
        """Tạo thanh tiêu đề và nút điều hướng"""
        header = ctk.CTkFrame(self, fg_color="white", height=60)
        header.pack(fill="x", pady=(0, 10))
        
        # Tiêu đề trái
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(title_box, text="Weekly Schedule", font=("Arial", 20, "bold"), text_color=self.COLOR_TEAL).pack(anchor="w")
        
        # Điều hướng phải
        nav_box = ctk.CTkFrame(header, fg_color="transparent")
        nav_box.pack(side="right", padx=20, pady=10)
        
        self._btn_nav(nav_box, "←")
        ctk.CTkButton(nav_box, text="CURRENT WEEK", fg_color=self.COLOR_TEAL, width=120, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self._btn_nav(nav_box, "→")

    def _btn_nav(self, parent, txt):
        ctk.CTkButton(parent, text=txt, width=35, height=30, fg_color=self.COLOR_TEAL, font=("Arial", 14, "bold")).pack(side="left")

    def create_grid_structure(self):
        """Vẽ khung lưới 8 cột (Session + 7 ngày) x 5 hàng (Header + 4 Slots)"""
        self.grid_container = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#E5E7EB")
        self.grid_container.pack(fill="both", expand=True)

        # Cấu hình tỷ lệ cột
        for i in range(8):
            self.grid_container.grid_columnconfigure(i, weight=1 if i > 0 else 0)

        # --- DÒNG 0: HEADER THỨ ---
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        
        # Ô góc trái trên (Session)
        self._create_header_cell(0, 0, "Session", width=80)

        # Các ô thứ
        for i, day in enumerate(days):
            bg = "#F59E0B" if i >= 5 else self.COLOR_TEAL # Cuối tuần màu cam
            self._create_header_cell(0, i+1, day, bg_color=bg)

        # --- CỘT 0: SESSION LABELS (Morning/Afternoon) ---
        # Gộp dòng (rowspan) để tạo label dọc
        self._create_session_label(1, "Morning")   # Slot 1, 2
        self._create_session_label(3, "Afternoon") # Slot 3, 4

        # --- TẠO CÁC Ô TRỐNG (SLOTS) ---
        # Row 1-4 tương ứng Slot 1-4
        # Col 1-7 tương ứng T2-CN
        for r in range(1, 5): 
            for c in range(1, 8):
                bg = self.COLOR_WEEKEND if c >= 6 else "white"
                
                # Frame ô chứa
                cell = ctk.CTkFrame(self.grid_container, fg_color=bg, corner_radius=0, border_width=1, border_color="#F3F4F6")
                cell.grid(row=r, column=c, sticky="nsew")
                
                # Label số Slot nhỏ mờ
                ctk.CTkLabel(cell, text=f"Slot {r}", font=("Arial", 9), text_color="#D1D5DB").pack(anchor="nw", padx=5, pady=2)
                
                # Lưu tham chiếu: Key là (thứ_index_0_6, slot_1_4)
                # c-1 vì col chạy từ 1, index ngày chạy từ 0
                self.cells[(c-1, r)] = cell

    def populate_schedule(self):
        """Lấy dữ liệu từ Controller và điền vào ô tương ứng"""
        try:
            data = self.controller.view_schedule() 
        except Exception:
            data = []

        if not data:
            # --- MOCK DATA ĐỂ TEST GIAO DIỆN ---
            data = [
                {'course_name': 'Advanced Python Programming', 'room': 'Lab 02', 'schedule': 'Monday 07:00-09:30'},
                {'course_name': 'Database Management Systems', 'room': 'B204', 'schedule': 'Tuesday 09:30-12:00'},
                {'course_name': 'Computer Networks', 'room': 'A105', 'schedule': 'Wednesday 13:00-15:30'},
                {'course_name': 'Artificial Intelligence', 'room': 'C301', 'schedule': 'Thursday 07:00-09:30'},
                {'course_name': 'Software Testing & QA', 'room': 'Lab 01', 'schedule': 'Friday 15:30-18:00'},
            ]

        days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for class_info in data:
            raw_sched = class_info.get('schedule', '') # VD: "Monday 07:00-09:30"
            
            # 1. Parse chuỗi để tìm vị trí (Thứ, Slot)
            day_idx, slot_idx = self._parse_schedule_string(raw_sched, days_map)
            
            # 2. Nếu vị trí hợp lệ, vẽ thẻ môn học
            if (day_idx, slot_idx) in self.cells:
                target_cell = self.cells[(day_idx, slot_idx)]
                self._render_card(target_cell, class_info)

    def _parse_schedule_string(self, sched_str, days_map):
        """Chuyển 'Monday 07:00...' thành (0, 1) tức (Thứ 2, Slot 1)"""
        try:
            parts = sched_str.split() # ['Monday', '07:00-09:30']
            day_str = parts[0]
            time_range = parts[1]
            start_time = time_range.split('-')[0] # '07:00'
            start_hour = int(start_time.split(':')[0])

            # Tìm index ngày
            day_idx = -1
            for i, d in enumerate(days_map):
                if d.lower() in day_str.lower():
                    day_idx = i
                    break
            
            # Map giờ sang Slot (Logic tương đối)
            slot_idx = -1
            if 6 <= start_hour < 9: slot_idx = 1
            elif 9 <= start_hour < 12: slot_idx = 2
            elif 12 <= start_hour < 15: slot_idx = 3
            elif 15 <= start_hour < 18: slot_idx = 4

            return day_idx, slot_idx
        except:
            return -1, -1

    def _render_card(self, parent, data):
        """Vẽ thẻ môn học đẹp trong ô"""
        # Xóa các widget cũ trong ô (trừ label Slot)
        for w in parent.winfo_children():
            if isinstance(w, ctk.CTkLabel) and "Slot" in w.cget("text"): continue
            w.destroy()

        # Card container
        card = ctk.CTkFrame(parent, fg_color=self.COLOR_CARD_BG, corner_radius=6, border_width=1, border_color=self.COLOR_CARD_BORDER)
        card.pack(fill="both", expand=True, padx=4, pady=(15, 4)) # pady top để né chữ Slot

        # Tên môn
        ctk.CTkLabel(card, text=data['course_name'], font=("Arial", 11, "bold"), text_color="#0369A1", wraplength=110).pack(anchor="w", padx=5, pady=(5,0))
        # Phòng
        ctk.CTkLabel(card, text=f"📍 {data['room']}", font=("Arial", 10), text_color="#475569").pack(anchor="w", padx=5)
        # Giờ
        time_only = data['schedule'].split(' ', 1)[1] if ' ' in data['schedule'] else ""
        ctk.CTkLabel(card, text=f"🕒 {time_only}", font=("Arial", 9), text_color="#64748B").pack(anchor="w", padx=5, pady=(0,5))

    # --- CÁC HÀM UI PHỤ TRỢ ---
    def _create_header_cell(self, r, c, txt, bg_color=None, width=None):
        if bg_color is None: bg_color = self.COLOR_TEAL
        
        # FIX LỖI CRASH Ở ĐÂY:
        # Nếu width có giá trị (ví dụ 80), truyền vào CTkFrame.
        # Nếu width là None, KHÔNG truyền tham số width (để CTk tự tính).
        if width:
            frame = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, height=45, width=width)
            frame.grid_propagate(False) # Cố định kích thước nếu có width
        else:
            frame = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, height=45)
            
        frame.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        
        ctk.CTkLabel(frame, text=txt, text_color="white", font=("Arial", 11, "bold")).place(relx=0.5, rely=0.5, anchor="center")

    def _create_session_label(self, start_row, txt):
        lbl = ctk.CTkLabel(self.grid_container, text=txt, fg_color=self.COLOR_TEAL, text_color="white", font=("Arial", 12, "bold"))
        lbl.grid(row=start_row, column=0, rowspan=2, sticky="nswe", padx=1, pady=1)