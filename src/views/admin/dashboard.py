import customtkinter as ctk
from datetime import datetime
from controllers.admin_controller import AdminController
from views.admin.semesters import SemestersFrame
from views.admin.student import StudentsFrame
from views.admin.lecturers import LecturersFrame
from views.admin.courses import CoursesFrame
from views.admin.classes import ClassesFrame
from views.admin.announcements import AnnouncementsFrame

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F5F7F9")
        self.app = app
        self.user = user
        self.controller = AdminController(user.user_id)
        self.nav_buttons = {}
        
        # --- COLOR PALETTE (Theo hình ảnh) ---
        self.COLOR_PRIMARY = "#0F766E"     # Teal đậm
        self.COLOR_ACCENT = "#10B981"      # Emerald
        
        # --- DATA FETCHING ---
        try:
            self.stats = self.controller.get_dashboard_stats()
        except:
            self.stats = {'students': 0, 'lecturers': 0, 'courses': 0}
            
        # --- LAYOUT SETUP ---
        self.grid_columnconfigure(0, weight=0) # Sidebar cố định
        self.grid_columnconfigure(1, weight=1) # Content giãn
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        self.create_sidebar()

        # 2. MAIN CONTENT AREA
        self.main_area = ctk.CTkFrame(self, fg_color="#F5F7F9", corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        
        # Header (Tiêu đề + Nút Post)
        self.create_header()

        # Scrollable Content Body
        self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        # Layout nội dung: 1 cột duy nhất
        self.content_scroll.grid_columnconfigure(0, weight=1)

        # Stats Row
        self.create_stats_row()
        
        # Quick Management Grid
        self.create_quick_management()

    # =========================================================================
    # 1. SIDEBAR SECTION
    # =========================================================================
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="white")
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(10, weight=1)

        # Logo Header
        logo_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=20, pady=30, sticky="w")
        
        icon_bg = ctk.CTkFrame(logo_box, width=35, height=35, fg_color="#E0F2F1", corner_radius=8)
        icon_bg.pack(side="left")
        ctk.CTkLabel(icon_bg, text="🎓", font=("Arial", 20)).place(relx=0.5, rely=0.5, anchor="center")
        
        text_box = ctk.CTkFrame(logo_box, fg_color="transparent")
        text_box.pack(side="left", padx=10)
        ctk.CTkLabel(text_box, text="SMS", font=("Arial", 16, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(text_box, text="PORTAL", font=("Arial", 10, "bold"), text_color="gray").pack(anchor="w")

        # Menu Label
        ctk.CTkLabel(sidebar, text="MENU", font=("Arial", 11, "bold"), text_color="#9CA3AF").grid(row=1, column=0, sticky="w", padx=30, pady=(10, 5))

        # Menu Items
        self._sidebar_btn(sidebar, 2, "Dashboard", "🏠", active=True, key="Dashboard")
        self._sidebar_btn(sidebar, 3, "Semesters", "🕒", key="Semesters", 
                          command=lambda: [self.set_active_menu("Semesters"), self.show_semesters()])
        self._sidebar_btn(sidebar, 4, "Students", "👨‍🎓", key="Students", 
            command=lambda: [self.set_active_menu("Students"), self.show_students()]
        )
        self._sidebar_btn(sidebar, 5, "Lecturers", "👨‍🏫", key="Lecturers",
            command=lambda: [self.set_active_menu("Lecturers"), self.show_lecturers()]
        )
        self._sidebar_btn(sidebar, 6, "Courses", "📖", key="Courses",
            command=lambda: [self.set_active_menu("Courses"), self.show_courses()]
        )
        self._sidebar_btn(sidebar, 7, "Classes", "🏫", key="Classes",
            command=lambda: [self.set_active_menu("Classes"), self.show_classes()]
        )
        self._sidebar_btn(sidebar, 8, "Grades", "📊", key="Grades")
        self._sidebar_btn(sidebar, 9, "Announcements", "📢", key="Announcements",
            command=lambda: [self.set_active_menu("Announcements"), self.show_announcements()]
        )

        # Footer
        footer = ctk.CTkFrame(sidebar, fg_color="#E0F2F1", corner_radius=10, height=50)
        footer.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(footer, text="Student System v1.0", font=("Arial", 11, "bold"), text_color="#047857").place(relx=0.5, rely=0.35, anchor="center")
        ctk.CTkLabel(footer, text="© 2026 University", font=("Arial", 9), text_color="#065F46").place(relx=0.5, rely=0.75, anchor="center")

        # Sign Out Btn
        ctk.CTkButton(sidebar, text="🚪 Sign Out", fg_color="transparent", text_color="#E76F51", hover_color="#FEF2F2", anchor="w", font=("Arial", 14), command=self.app.show_login).grid(row=12, column=0, padx=20, pady=20, sticky="ew")

    def _sidebar_btn(self, parent, row, text, icon, active=False, command=None, key=None):
        color = self.COLOR_PRIMARY if active else "transparent"
        text_col = "white" if active else "#4B5563"
        hover = self.COLOR_PRIMARY if active else "#F3F4F6"
        
        if command is None:
            command = lambda: print(f"Nav to {text}")

        btn = ctk.CTkButton(
            parent, text=f"  {icon}    {text}", 
            fg_color=color, text_color=text_col, hover_color=hover, 
            anchor="w", font=("Arial", 13, "bold"), height=45, corner_radius=8,
            command=command
        )
        btn.grid(row=row, column=0, padx=15, pady=4, sticky="ew")
        
        if key:
            self.nav_buttons[key] = btn

    # =========================================================================
    # 2. HEADER SECTION
    # =========================================================================
    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=80)
        header.pack(fill="x", padx=30, pady=(20, 0))
        
        ctk.CTkLabel(header, text="Admin Control Center", font=("Arial", 24, "bold"), text_color="#111827").pack(side="left")

        btn = ctk.CTkButton(
            header, text="📢  Post Announcement", 
            fg_color=self.COLOR_PRIMARY, hover_color="#115E59", 
            font=("Arial", 13, "bold"), height=40, width=180
        )
        btn.pack(side="right")

    # =========================================================================
    # 3. STATS CARDS
    # =========================================================================
    def create_stats_row(self):
        container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        # Grid layout cho 3 card, chiếm toàn bộ chiều ngang
        container.pack(fill="x", pady=(20, 30))
        
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=1)

        s_count = self.stats.get('students', 0)
        l_count = self.stats.get('lecturers', 0)
        c_count = self.stats.get('courses', 0)

        self._draw_stat_card(container, 0, "STUDENTS", s_count, "👨‍🎓", "#DBEAFE", "#2563EB")
        self._draw_stat_card(container, 1, "LECTURERS", l_count, "👨‍🏫", "#F3E8FF", "#9333EA")
        self._draw_stat_card(container, 2, "COURSES", c_count, "📖", "#FFEDD5", "#EA580C")

    def _draw_stat_card(self, parent, col, title, value, icon, bg_color, icon_color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=0)
        # padx 10 giữa các card
        card.grid(row=0, column=col, sticky="ew", padx=10)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=25)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left")
        
        ctk.CTkLabel(left, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(left, text=str(value), font=("Arial", 32, "bold"), text_color="#1F2937").pack(anchor="w", pady=(5, 0))
        
        badge = ctk.CTkFrame(left, fg_color="transparent")
        badge.pack(anchor="w", pady=(5, 0))
        ctk.CTkLabel(badge, text="+2%", font=("Arial", 11, "bold"), text_color="#10B981").pack(side="left")
        ctk.CTkLabel(badge, text=" from last month", font=("Arial", 11), text_color="gray").pack(side="left", padx=2)

        icon_box = ctk.CTkFrame(inner, width=55, height=55, corner_radius=12, fg_color=bg_color)
        icon_box.pack(side="right", anchor="ne")
        ctk.CTkLabel(icon_box, text=icon, font=("Arial", 24), text_color=icon_color).place(relx=0.5, rely=0.5, anchor="center")

    # =========================================================================
    # 4. QUICK MANAGEMENT GRID
    # =========================================================================
    def create_quick_management(self):
        container = ctk.CTkFrame(self.content_scroll, fg_color="white", corner_radius=12)
        # Giờ đây Quick Management chiếm toàn bộ chiều ngang
        container.pack(fill="both", expand=True) 
        
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=20)
        ctk.CTkLabel(header, text="QUICK MANAGEMENT", font=("Arial", 13, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkFrame(header, height=2, fg_color="#F3F4F6").pack(fill="x", pady=(10, 0))

        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Grid 3 cột
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)

        items = [
            ("Semesters", "🕒", "#FEE2E2", "#EF4444"),  
            ("Students", "👨‍🎓", "#DBEAFE", "#3B82F6"),  
            ("Lecturers", "👨‍🏫", "#F3E8FF", "#8B5CF6"), 
            ("Courses", "📖", "#FFEDD5", "#F59E0B"),    
            ("Classes", "🏫", "#D1FAE5", "#10B981"),    
            ("Announcements", "📢", "#F3F4F6", "#4B5563")
        ]

        for i, (text, icon, bg, fg) in enumerate(items):
            r, c = divmod(i, 3)
            self._draw_mgmt_btn(grid, r, c, text, icon, bg, fg)

    def _draw_mgmt_btn(self, parent, r, c, text, icon, bg, fg):
        btn = ctk.CTkButton(
            parent, text="", fg_color="white", border_width=1, border_color="#E5E7EB",
            hover_color="#F9FAFB", height=100, corner_radius=10,
            command=lambda: print(f"Manage {text}")
        )
        btn.grid(row=r, column=c, sticky="ew", padx=10, pady=10)
        
        icon_f = ctk.CTkFrame(btn, width=40, height=40, corner_radius=20, fg_color=bg)
        icon_f.place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(icon_f, text=icon, text_color=fg, font=("Arial", 18)).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(btn, text=text, font=("Arial", 12, "bold"), text_color="#374151").place(relx=0.5, rely=0.75, anchor="center")

    def set_active_menu(self, key):
        for k, btn in self.nav_buttons.items():
            is_active = (k == key)
            color = self.COLOR_PRIMARY if is_active else "transparent"
            text_col = "white" if is_active else "#4B5563"
            btn.configure(fg_color=color, text_color=text_col)

    def show_semesters(self):
        # 1. Clear content
        for widget in self.content_scroll.winfo_children(): widget.destroy()

        # 2. Reset grid (1 column full width)
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)

        # 3. Show Frame
        SemestersFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_students(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        StudentsFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_lecturers(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturersFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_courses(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        CoursesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_classes(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ClassesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_announcements(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        AnnouncementsFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)