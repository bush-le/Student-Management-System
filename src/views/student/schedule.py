import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.student_controller import StudentController

class ScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = StudentController(user_id)
        
        # --- COLOR CONFIG ---
        self.COLOR_TEAL = "#0F766E"      # Header
        self.COLOR_HEADER_BG = "#E5E7EB" # Nền header bảng
        self.COLOR_GRID_LINE = "#D1D5DB" 
        self.COLOR_SLOT_BG = "white"
        self.COLOR_CARD_BG = "#E0F2FE"   # Nền thẻ môn học
        self.COLOR_CARD_BORDER = "#7DD3FC"

        # Dictionary lưu tham chiếu grid để điền data
        # Key: (day_index, slot_index) -> Value: CTkFrame widget
        self.cells = {} 

        # 1. Header (Tuần hiện tại)
        self.create_header()

        # 2. Main Schedule Grid
        self.create_schedule_grid()

        # 3. Load Data
        self.load_schedule_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Title
        ctk.CTkLabel(header, text="Weekly Schedule", font=("Arial", 20, "bold"), text_color="#111827").pack(side="left")
        
        # Week Navigation
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right")
        
        # Tính tuần hiện tại
        today = datetime.now()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        week_str = f"{start_week.strftime('%d %b')} - {end_week.strftime('%d %b %Y')}"

        ctk.CTkButton(nav, text="<", width=30, fg_color="white", text_color="#333", hover_color="#F3F4F6").pack(side="left")
        ctk.CTkLabel(nav, text=week_str, font=("Arial", 12, "bold"), text_color="#333").pack(side="left", padx=15)
        ctk.CTkButton(nav, text=">", width=30, fg_color="white", text_color="#333", hover_color="#F3F4F6").pack(side="left")

    def create_schedule_grid(self):
        # Container chính có viền
        self.grid_frame = ctk.CTkFrame(self, fg_color="#D1D5DB", border_width=1, corner_radius=0)
        self.grid_frame.pack(fill="both", expand=True)

        # Cấu hình 8 cột (1 cột giờ + 7 ngày)
        for i in range(8):
            weight = 0 if i == 0 else 1 # Cột giờ nhỏ, cột ngày giãn đều
            self.grid_frame.grid_columnconfigure(i, weight=weight)
        
        # Cấu hình 13 hàng (1 Header + 12 Tiết học)
        # Giả sử trường học từ Tiết 1 (7h) đến Tiết 12 (18h)
        for r in range(13):
            self.grid_frame.grid_rowconfigure(r, weight=1)

        # --- HEADER ROW (Thứ) ---
        days = ["TIME", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for c, day in enumerate(days):
            bg = self.COLOR_TEAL if c > 0 else "#374151" # Cột Time màu xám đậm
            lbl = ctk.CTkLabel(
                self.grid_frame, text=day, 
                font=("Arial", 12, "bold"), text_color="white",
                fg_color=bg, height=40
            )
            lbl.grid(row=0, column=c, sticky="nsew", padx=1, pady=1)

        # --- TIME COLUMN (Tiết 1 -> 12) ---
        # Map tiết học sang giờ (Ví dụ)
        time_slots = [
            (1, "07:00"), (2, "07:50"), (3, "09:00"), (4, "09:50"),
            (5, "10:40"), (6, "13:00"), (7, "13:50"), (8, "14:40"),
            (9, "15:40"), (10, "16:30")
        ]
        
        # Chỉ vẽ 10 tiết demo cho gọn
        for r, (slot, time) in enumerate(time_slots, start=1):
            frame = ctk.CTkFrame(self.grid_frame, fg_color="#F3F4F6", corner_radius=0)
            frame.grid(row=r, column=0, sticky="nsew", padx=1, pady=1)
            
            ctk.CTkLabel(frame, text=f"Slot {slot}", font=("Arial", 10, "bold"), text_color="#333").pack(pady=(5,0))
            ctk.CTkLabel(frame, text=time, font=("Arial", 9), text_color="gray").pack()

        # --- EMPTY CELLS ---
        for r in range(1, 11): # 10 tiết
            for c in range(1, 8): # 7 ngày
                cell = ctk.CTkFrame(self.grid_frame, fg_color="white", corner_radius=0)
                cell.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                
                # Lưu tham chiếu: Key = (day_index_0_6, slot_1_10)
                # c-1 để chuyển MON (c=1) thành index 0
                self.cells[(c-1, r)] = cell

    def load_schedule_data(self):
        try:
            # Lấy dữ liệu thật từ DB
            schedule_data = self.controller.view_schedule()
            # Dữ liệu trả về: [{'course_name': '...', 'room': '...', 'schedule': 'Monday 07:00-09:30', ...}]
            
            if not schedule_data: return

            days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

            for item in schedule_data:
                raw_sched = item.get('schedule', '').lower()
                # Parse: "Monday 07:00-09:30"
                
                # 1. Tìm ngày
                day_idx = -1
                for i, d in enumerate(days_map):
                    if d in raw_sched:
                        day_idx = i
                        break
                
                if day_idx == -1: continue

                # 2. Tìm Tiết bắt đầu (dựa vào giờ)
                # Simple parsing: tìm giờ bắt đầu (VD: 07:00 -> 7)
                try:
                    time_part = raw_sched.split(days_map[day_idx])[1].strip() # "07:00-09:30"
                    start_str = time_part.split('-')[0].strip() # "07:00"
                    start_hour = int(start_str.split(':')[0])
                    
                    # Map giờ sang Slot (Logic tương đối của UTH)
                    start_slot = self._hour_to_slot(start_hour)
                    duration = 3 # Giả định mỗi môn học 3 tiết (hoặc tính toán từ end_time)
                    
                    # 3. Vẽ Card đè lên các ô
                    if start_slot > 0:
                        self._render_class_card(day_idx, start_slot, duration, item)
                        
                except Exception as e:
                    print(f"Skipping invalid schedule format: {raw_sched} - {e}")
                    continue

        except Exception as e:
            print(f"Error loading schedule: {e}")

    def _hour_to_slot(self, hour):
        """Map giờ bắt đầu sang tiết học"""
        if 6 <= hour < 8: return 1   # 7h -> Slot 1
        if 8 <= hour < 9: return 2   # 8h -> Slot 2
        if 9 <= hour < 10: return 3  # 9h -> Slot 3
        if 10 <= hour < 11: return 4 # 10h -> Slot 4
        if 11 <= hour < 12: return 5 # 11h -> Slot 5
        if 12 <= hour < 14: return 6 # 13h -> Slot 6
        if 14 <= hour < 15: return 7
        if 15 <= hour < 16: return 8
        if 16 <= hour < 17: return 9
        return 1

    def _render_class_card(self, day_idx, start_slot, duration, data):
        """
        Vẽ thẻ môn học trải dài qua nhiều ô (rowspan).
        Kỹ thuật: Vẽ đè lên Grid frame tại vị trí row/col tương ứng.
        """
        # Xác định vị trí lưới
        # row = start_slot (vì row 0 là header)
        # column = day_idx + 1 (vì col 0 là cột giờ)
        
        # Màu sắc ngẫu nhiên hoặc cố định
        bg_color = "#E0F2FE" # Xanh nhạt
        border_col = "#0284C7" # Xanh đậm
        text_col = "#0369A1"

        card = ctk.CTkFrame(
            self.grid_frame, 
            fg_color=bg_color, 
            corner_radius=4,
            border_width=0 # Card phẳng
        )
        
        # Grid span: rowspan = số tiết
        card.grid(
            row=start_slot, 
            column=day_idx + 1, 
            rowspan=duration, 
            sticky="nsew", 
            padx=2, pady=2
        )
        
        # Border trái làm điểm nhấn
        border = ctk.CTkFrame(card, width=4, fg_color=border_col)
        border.pack(side="left", fill="y")
        
        # Nội dung
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(content, text=data['course_name'], font=("Arial", 10, "bold"), text_color=text_col, wraplength=100, justify="left").pack(anchor="w")
        ctk.CTkLabel(content, text=f"Phòng: {data['room']}", font=("Arial", 9), text_color="#475569").pack(anchor="w")
        
        # Hiển thị giảng viên nếu có
        lec = data.get('lecturer_name', '')
        if lec:
            ctk.CTkLabel(content, text=f"GV: {lec}", font=("Arial", 9, "italic"), text_color="#64748B").pack(anchor="w")