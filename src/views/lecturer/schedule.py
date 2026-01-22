import customtkinter as ctk
from datetime import datetime
from controllers.lecturer_controller import LecturerController

class LecturerScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = LecturerController(user_id)
        
        # --- CẤU HÌNH MÀU SẮC (THEO THIẾT KẾ) ---
        self.COLOR_TEAL = "#2A9D8F"       # Màu chủ đạo Header
        self.COLOR_WEEKEND = "#FFFBEB"    # Màu nền T7, CN (Vàng nhạt)
        self.COLOR_CLASS_BG = "#ECFDF5"   # Nền thẻ lớp dạy (Xanh lá nhạt)
        self.COLOR_CLASS_BORDER = "#A7F3D0" # Viền thẻ
        self.COLOR_TEXT_MAIN = "#065F46"  # Chữ xanh đậm

        # Dictionary lưu tham chiếu các ô grid
        self.cells = {} 

        # 1. Header (Điều hướng tuần)
        self.create_header()

        # 2. Grid Lịch
        self.create_grid_structure()

        # 3. Chú thích (Legend)
        self.create_legend()

        # 4. Đổ dữ liệu
        self.populate_schedule()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="white", height=60)
        header.pack(fill="x", pady=(0, 10))
        
        # Date Picker (Giả lập)
        date_btn = ctk.CTkButton(
            header, text="05/01/2026 ⌄", 
            fg_color="white", text_color="#333", 
            border_width=1, border_color="#E5E7EB",
            width=120, height=35, font=("Arial", 12)
        )
        date_btn.pack(side="left", padx=20)

        # Navigation
        nav_box = ctk.CTkFrame(header, fg_color="transparent")
        nav_box.pack(side="right", padx=20)
        
        self._btn_nav(nav_box, "←")
        ctk.CTkButton(nav_box, text="TODAY", fg_color=self.COLOR_TEAL, width=80, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self._btn_nav(nav_box, "→")

    def _btn_nav(self, parent, txt):
        ctk.CTkButton(parent, text=txt, width=35, height=30, fg_color=self.COLOR_TEAL, font=("Arial", 12, "bold")).pack(side="left")

    def create_grid_structure(self):
        # Container chính có viền
        self.grid_container = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#E5E7EB")
        self.grid_container.pack(fill="both", expand=True, padx=20)

        # Cấu hình 8 cột (Session + 7 ngày)
        for i in range(8):
            self.grid_container.grid_columnconfigure(i, weight=1 if i > 0 else 0)

        # --- HEADER ROW ---
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        # Giả lập ngày hiển thị
        dates = ["05/01/2026", "06/01/2026", "07/01/2026", "08/01/2026", "09/01/2026", "10/01/2026", "11/01/2026"]

        # Ô Session
        self._create_header_cell(0, 0, "Session", width=90)

        # Ô Ngày
        for i, day in enumerate(days):
            bg = "#F59E0B" if i >= 5 else self.COLOR_TEAL # Cuối tuần màu cam
            text = f"{day}\n{dates[i]}"
            self._create_header_cell(0, i+1, text, bg_color=bg)

        # --- SESSION LABELS ---
        self._create_session_label(1, "Morning")   # Slot 1, 2
        self._create_session_label(3, "Afternoon") # Slot 3, 4

        # --- SLOTS GRID ---
        for r in range(1, 5): 
            for c in range(1, 8):
                # Màu nền: Cuối tuần vàng nhạt
                bg = self.COLOR_WEEKEND if c >= 6 else "white"
                
                cell = ctk.CTkFrame(self.grid_container, fg_color=bg, corner_radius=0, border_width=1, border_color="#F3F4F6")
                cell.grid(row=r, column=c, sticky="nsew")
                
                # Label Slot nhỏ
                ctk.CTkLabel(cell, text=f"Slot {r}", font=("Arial", 9), text_color="#D1D5DB").pack(anchor="nw", padx=5, pady=2)
                
                # Lưu tham chiếu (c-1 vì data index ngày từ 0)
                self.cells[(c-1, r)] = cell

    def create_legend(self):
        """Chú thích màu sắc ở dưới cùng"""
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(pady=10)

        self._legend_item(legend, "Weekend Slot", self.COLOR_WEEKEND, "#D1D5DB")
        ctk.CTkFrame(legend, width=20, fg_color="transparent").pack(side="left") # Spacer
        self._legend_item(legend, "Teaching Class", self.COLOR_CLASS_BG, self.COLOR_CLASS_BORDER)

    def _legend_item(self, parent, text, bg, border):
        box = ctk.CTkFrame(parent, width=15, height=15, fg_color=bg, border_width=1, border_color=border, corner_radius=2)
        box.pack(side="left")
        ctk.CTkLabel(parent, text=text, font=("Arial", 11), text_color="gray").pack(side="left", padx=(5, 0))

    def populate_schedule(self):
        try:
            # Lấy dữ liệu từ Controller
            data = self.controller.get_teaching_schedule()
        except Exception:
            data = []

        days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for cls in data:
            raw_sched = cls.get('schedule', '') 
            day_idx, slot_idx = self._parse_schedule(raw_sched, days_map)
            
            if (day_idx, slot_idx) in self.cells:
                self._render_card(self.cells[(day_idx, slot_idx)], cls)

    def _render_card(self, parent, data):
        """Vẽ thẻ lớp dạy (Màu xanh lá)"""
        # Xóa widget cũ
        for w in parent.winfo_children():
            if isinstance(w, ctk.CTkLabel) and "Slot" in w.cget("text"): continue
            w.destroy()

        # Card container
        card = ctk.CTkFrame(parent, fg_color=self.COLOR_CLASS_BG, corner_radius=4, border_width=1, border_color=self.COLOR_CLASS_BORDER)
        card.pack(fill="both", expand=True, padx=4, pady=(18, 4)) 

        # Decor line (Xanh đậm bên trái)
        ctk.CTkFrame(card, width=3, fg_color="#10B981", corner_radius=0).pack(side="left", fill="y")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Tên môn
        ctk.CTkLabel(content, text=data['course_name'], font=("Arial", 10, "bold"), text_color=self.COLOR_TEXT_MAIN, wraplength=100, justify="left").pack(anchor="w")
        
        # Mã lớp (CS101)
        # Vì controller trả về data join, ta giả sử có course_code hoặc dùng class_id
        code = f"ID: {data['class_id']}" 
        ctk.CTkLabel(content, text=code, font=("Arial", 9, "bold"), text_color="#047857").pack(anchor="w", pady=(2,0))

        # Thời gian
        time_only = data['schedule'].split(' ', 1)[1] if ' ' in data['schedule'] else ""
        ctk.CTkLabel(content, text=f"🕒 {time_only}", font=("Arial", 9), text_color="gray").pack(anchor="w", pady=(5,0))
        
        # Phòng
        ctk.CTkLabel(content, text=f"📍 {data['room']}", font=("Arial", 9), text_color="gray").pack(anchor="w")

        # Số lượng sinh viên (Điểm khác biệt so với SV)
        count = data.get('enrolled_count', 0)
        ctk.CTkLabel(content, text=f"👥 {count} Students", font=("Arial", 9, "bold"), text_color="#059669").pack(anchor="w", pady=(5,0))

    # --- HELPER FUNCTIONS ---
    def _parse_schedule(self, sched_str, days_map):
        try:
            parts = sched_str.split()
            day_str = parts[0]
            start_hour = int(parts[1].split('-')[0].split(':')[0])
            
            day_idx = -1
            for i, d in enumerate(days_map):
                if d in day_str: day_idx = i; break
            
            slot_idx = -1
            if 6 <= start_hour < 9: slot_idx = 1
            elif 9 <= start_hour < 12: slot_idx = 2
            elif 12 <= start_hour < 15: slot_idx = 3
            elif 15 <= start_hour < 18: slot_idx = 4
            
            return day_idx, slot_idx
        except: return -1, -1

    def _create_header_cell(self, r, c, txt, bg_color=None, width=None):
        if bg_color is None: bg_color = self.COLOR_TEAL
        if width:
            f = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, height=45, width=width)
            f.grid_propagate(False)
        else:
            f = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, height=45)
        f.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        ctk.CTkLabel(f, text=txt, text_color="white", font=("Arial", 10, "bold")).place(relx=0.5, rely=0.5, anchor="center")

    def _create_session_label(self, start_row, txt):
        lbl = ctk.CTkLabel(self.grid_container, text=txt, fg_color=self.COLOR_TEAL, text_color="white", font=("Arial", 11, "bold"))
        lbl.grid(row=start_row, column=0, rowspan=2, sticky="nswe", padx=1, pady=1)