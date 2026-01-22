import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from controllers.lecturer_controller import LecturerController # <--- Import Controller
from views.lecturer.schedule import LecturerScheduleFrame
from views.lecturer.my_class import LecturerClassesFrame
from views.lecturer.class_manager import LecturerClassManager # <--- Import Mới

class LecturerDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F5F7F9")
        self.app = app
        self.user = user
        self.nav_buttons = {}
        
        # --- 1. KHỞI TẠO CONTROLLER & LẤY DỮ LIỆU ---
        self.controller = LecturerController(user.user_id)
        
        # Lấy danh sách lớp dạy (FR-10)
        # Data gồm: class_id, course_name, schedule, room, enrolled_count...
        self.all_classes = self.controller.get_teaching_schedule()
        
        # Lọc lịch dạy HÔM NAY
        self.today_classes = self._filter_today_classes(self.all_classes)

        # --- CẤU HÌNH MÀU SẮC ---
        self.COLOR_TEAL = "#2A9D8F"
        
        # --- GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar & Main Area
        self.create_sidebar()
        self.main_area = ctk.CTkFrame(self, fg_color="#F5F7F9", corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        
        self.create_header()

        self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.content_scroll.grid_columnconfigure(0, weight=3)
        self.content_scroll.grid_columnconfigure(1, weight=1)

        # Widget
        self.show_home()

    def _filter_today_classes(self, classes):
        """Lọc ra các lớp có lịch học trùng với thứ hiện tại (VD: 'Monday')"""
        if not classes: return []
        
        # Lấy tên thứ hiện tại (Monday, Tuesday...)
        today_name = datetime.now().strftime("%A") 
        
        filtered = []
        for cls in classes:
            # Kiểm tra xem chuỗi schedule (VD: "Monday 07:00-09:30") có chứa "Monday" không
            if cls.get('schedule') and today_name in cls['schedule']:
                filtered.append(cls)
        return filtered

    # ... (Giữ nguyên phần Sidebar và Header như cũ) ...
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="white")
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(10, weight=1) # Spacer đẩy footer xuống

        # 1. Logo
        ctk.CTkLabel(sidebar, text="🎓 SMS Portal", font=("Arial", 22, "bold"), text_color=self.COLOR_TEAL).grid(row=0, column=0, pady=30, padx=20)

        # 2. MENU Label (Thêm mới cho giống thiết kế)
        ctk.CTkLabel(sidebar, text="MENU", font=("Arial", 11, "bold"), text_color="#9CA3AF").grid(row=1, column=0, sticky="w", padx=30, pady=(10, 5))

        # 3. Menu Items (Chỉ giữ lại 3 mục)
        self._sidebar_btn(sidebar, 2, "Dashboard", "🏠", key="home", command=self.show_home)
        self._sidebar_btn(sidebar, 3, "Teaching Schedule", "📅", key="schedule", command=self.show_schedule)
        self._sidebar_btn(sidebar, 4, "My Classes", "📖", key="classes", command=self.show_my_classes)

        # 4. Footer (Giữ nguyên)
        footer = ctk.CTkFrame(sidebar, fg_color="#E0F2F1", corner_radius=10)
        footer.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(footer, text="Lecturer System v1.0", font=("Arial", 10, "bold"), text_color=self.COLOR_TEAL).pack(pady=10)

        # 5. Sign Out
        ctk.CTkButton(sidebar, text="🚪 Sign Out", fg_color="transparent", text_color="#E76F51", hover_color="#FEF2F2", anchor="w", font=("Arial", 14), command=self.app.show_login).grid(row=12, column=0, padx=20, pady=20, sticky="ew")

    def _sidebar_btn(self, parent, row, text, icon, key=None, command=None):
        btn = ctk.CTkButton(parent, text=f"  {icon}   {text}", fg_color="transparent", text_color="#555", hover_color="#E0F2F1", anchor="w", font=("Arial", 14), height=45, command=lambda: [self.set_active_nav(key), command()] if command else None)
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        if key: self.nav_buttons[key] = btn

    def set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            active = (k == key)
            color = "#E0F2F1" if active else "transparent"
            fg = self.COLOR_TEAL if active else "#555"
            font_w = "bold" if active else "normal"
            btn.configure(fg_color=color, text_color=fg, font=("Arial", 14, font_w))

    def create_header(self):
        # (Code Header giữ nguyên)
        header = ctk.CTkFrame(self.main_area, fg_color="white", height=60, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="UNIVERSITY TRAINING MANAGEMENT", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=30, pady=15)
        profile = ctk.CTkFrame(header, fg_color="transparent")
        profile.pack(side="right", padx=30)
        ctk.CTkLabel(profile, text="👨‍🏫", font=("Arial", 24)).pack(side="left", padx=10)
        info = ctk.CTkFrame(profile, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text=self.user.full_name, font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(info, text="LECTURER", font=("Arial", 10, "bold"), text_color=self.COLOR_TEAL).pack(anchor="w")

    def create_welcome_section(self):
        frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 20))
        ctk.CTkLabel(frame, text="Lecturer Portal", font=("Arial", 24, "bold"), text_color="#333").pack(side="left")
        ctk.CTkLabel(frame, text="Overview of your teaching activities.", font=("Arial", 14), text_color="gray").pack(side="left", padx=10, pady=(8,0))
        
        date_bg = ctk.CTkFrame(frame, fg_color="white", corner_radius=6)
        date_bg.pack(side="right")
        ctk.CTkLabel(date_bg, text=datetime.now().strftime("📅 %A, %B %d"), font=("Arial", 12, "bold"), text_color="#333").pack(padx=15, pady=8)

    # --- 2. STATS CARDS (DÙNG DATA THẬT) ---
    def create_stats_cards(self):
        container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        container.grid(row=1, column=0, sticky="ew", padx=(0, 20))
        
        # Tính toán số liệu thực tế
        active_classes_count = len(self.all_classes)
        
        # Tính tổng sinh viên (cộng dồn enrolled_count của các lớp)
        total_students = sum(cls['enrolled_count'] for cls in self.all_classes) if self.all_classes else 0
        
        classes_today_count = len(self.today_classes)

        self._draw_stat_card(container, 0, "Active Classes", str(active_classes_count), "👨‍🏫")
        self._draw_stat_card(container, 1, "Total Students", str(total_students), "🎓")
        self._draw_stat_card(container, 2, "Classes Today", str(classes_today_count), "🕒")

    def _draw_stat_card(self, parent, col, title, value, icon):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.grid(row=0, column=col, sticky="ew", padx=5 if col==1 else 0, pady=0)
        parent.grid_columnconfigure(col, weight=1)
        
        icon_bg = ctk.CTkFrame(card, width=50, height=50, corner_radius=25, fg_color="#F0FDF4")
        icon_bg.pack(pady=(20, 5))
        ctk.CTkLabel(icon_bg, text=icon, font=("Arial", 20)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=value, font=("Arial", 28, "bold"), text_color="#333").pack()
        ctk.CTkLabel(card, text=title.upper(), font=("Arial", 10, "bold"), text_color="gray").pack(pady=(0, 20))

    # --- 3. TODAY'S SCHEDULE (DÙNG DATA THẬT) ---
    def create_todays_schedule(self):
        ctk.CTkLabel(self.content_scroll, text="🕒 Today's Schedule", font=("Arial", 16, "bold"), text_color="#333").grid(row=2, column=0, sticky="w", pady=(30, 10))

        list_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        list_frame.grid(row=3, column=0, sticky="ew", padx=(0, 20))

        if not self.today_classes:
            ctk.CTkLabel(list_frame, text="No classes scheduled for today.", text_color="gray", font=("Arial", 12, "italic")).pack(anchor="w", pady=10)
        else:
            for cls in self.today_classes:
                # Controller trả về dictionary key: class_id, course_name, schedule, room...
                self._draw_schedule_item(list_frame, cls)

    def _draw_schedule_item(self, parent, data):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=8)

        decor = ctk.CTkFrame(card, width=6, fg_color=self.COLOR_TEAL, corner_radius=0)
        decor.pack(side="left", fill="y")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Xử lý chuỗi giờ học (Tách "Monday 07:00-09:30" lấy phần giờ)
        full_sched = data.get('schedule', '')
        time_only = full_sched.split(' ', 1)[1] if ' ' in full_sched else full_sched

        tags = ctk.CTkFrame(content, fg_color="transparent")
        tags.pack(anchor="w", pady=(0, 5))
        self._tag(tags, time_only)
        self._tag(tags, data.get('room', 'N/A'), color="#DBEAFE", text_color="#1E40AF")

        ctk.CTkLabel(content, text=data.get('course_name', 'Unknown Course'), font=("Arial", 16, "bold"), text_color="#333").pack(anchor="w")
        # Dùng Class ID làm mã lớp vì query hiện tại không select course_code
        class_code = f"Class ID: {data.get('class_id')}" 
        ctk.CTkLabel(content, text=class_code, font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")

        btn = ctk.CTkButton(
            card, text="Manage Class", 
            fg_color=self.COLOR_TEAL, hover_color="#238b7e",
            font=("Arial", 12, "bold"), width=120, height=35,
            command=lambda: self.open_class_manager(data)
        )
        btn.pack(side="right", padx=20)

    def _tag(self, parent, text, color="#F3F4F6", text_color="#374151"):
        lbl = ctk.CTkLabel(parent, text=f" {text} ", fg_color=color, text_color=text_color, font=("Arial", 10, "bold"), corner_radius=4)
        lbl.pack(side="left", padx=(0, 10))

    def create_quick_links(self):
        # (Giữ nguyên Quick Links)
        right_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        right_col.grid(row=1, column=1, rowspan=10, sticky="nsw")

        ctk.CTkLabel(right_col, text="QUICK LINKS", font=("Arial", 12, "bold"), text_color=self.COLOR_TEAL).pack(anchor="w", pady=(0, 15))
        card = ctk.CTkFrame(right_col, fg_color="white", corner_radius=10)
        card.pack(fill="x", ipadx=10, ipady=10)

        self._quick_link_item(card, "📅", "Teaching Schedule", "View weekly timetable")
        ctk.CTkFrame(card, height=1, fg_color="#F3F4F6").pack(fill="x", padx=10, pady=5)
        self._quick_link_item(card, "📖", "Class Management", "Grades, attendance, roster")

    def _quick_link_item(self, parent, icon, title, desc):
        btn = ctk.CTkButton(parent, text="", fg_color="transparent", hover_color="#F9FAFB", height=60, width=220, command=lambda: print(f"Clicked {title}"))
        btn.pack(pady=2)
        icon_box = ctk.CTkFrame(btn, width=40, height=40, fg_color="#F3F4F6", corner_radius=8)
        icon_box.place(relx=0.15, rely=0.5, anchor="center")
        ctk.CTkLabel(icon_box, text=icon, font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(btn, text=title, font=("Arial", 12, "bold"), text_color="#333").place(relx=0.3, rely=0.35, anchor="w")
        ctk.CTkLabel(btn, text=desc, font=("Arial", 10), text_color="gray").place(relx=0.3, rely=0.65, anchor="w")

    # --- NAVIGATION METHODS ---
    def clear_content(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()

    def show_home(self):
        self.clear_content()
        self.set_active_nav("home")
        self.content_scroll.grid_columnconfigure(0, weight=3)
        self.content_scroll.grid_columnconfigure(1, weight=1)
        
        self.create_welcome_section()
        self.create_stats_cards()
        self.create_todays_schedule()
        self.create_quick_links()

    def show_schedule(self):
        self.clear_content()
        self.set_active_nav("schedule")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturerScheduleFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_my_classes(self):
        self.clear_content()
        self.set_active_nav("classes")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturerClassesFrame(self.content_scroll, self, self.user.user_id).pack(fill="both", expand=True)

    def open_class_manager(self, class_data):
        """Hàm này được gọi khi bấm nút Manage Class"""
        # 1. Xóa nội dung cũ
        for widget in self.content_scroll.winfo_children(): widget.destroy()
        
        # 2. Reset Grid (Manager cần full chiều rộng)
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)

        # 3. Hiển thị Class Manager Frame
        # Truyền callback self.show_my_classes để nút Back hoạt động
        manager = LecturerClassManager(
            self.content_scroll, 
            self.user.user_id, 
            class_data, 
            on_back_callback=self.show_my_classes
        )
        manager.pack(fill="both", expand=True)