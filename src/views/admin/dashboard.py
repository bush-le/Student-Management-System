import customtkinter as ctk
from datetime import datetime
from controllers.admin_controller import AdminController
from views.admin.semesters import SemestersFrame
from views.admin.student import StudentsFrame
from views.admin.lecturers import LecturersFrame
from views.admin.courses import CoursesFrame
from views.admin.classes import ClassesFrame
from views.admin.announcements import AnnouncementsFrame, AnnouncementDialog
from utils.threading_helper import run_in_background

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F3F4F6")
        self.app = app
        self.user = user
        self.controller = AdminController(user.user_id)
        self.nav_buttons = {}
        self.user_menu = None # Biến để theo dõi menu dropdown
        
        self.COLOR_PRIMARY = "#0F766E"
        self.COLOR_SIDEBAR = "#FFFFFF"
        self.COLOR_TEXT_MAIN = "#111827"
        self.COLOR_TEXT_SUB = "#6B7280"
        
        # Load stats on background thread with tk_root
        self.stats = {'students': 0, 'lecturers': 0, 'courses': 0, 'classes': 0}
        run_in_background(
            self.controller.get_dashboard_stats,
            on_complete=self._update_stats,
            tk_root=self.winfo_toplevel()
        )
            
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.main_area = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        
        self.create_header()

        self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        self.show_home()

    # =========================================================================
    # 1. SIDEBAR
    # =========================================================================
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(10, weight=1)

        # Logo Header
        logo_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=20, pady=30, sticky="ew")
        
        text_box = ctk.CTkFrame(logo_box, fg_color="transparent")
        text_box.pack(side="left")
        ctk.CTkLabel(text_box, text="SMS ADMIN", font=("Arial", 18, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(text_box, text="Management Portal", font=("Arial", 10, "bold"), text_color=self.COLOR_TEXT_SUB).pack(anchor="w")

        # Menu
        ctk.CTkLabel(sidebar, text="MAIN MENU", font=("Arial", 11, "bold"), text_color="#9CA3AF").grid(row=1, column=0, sticky="w", padx=30, pady=(20, 10))

        self._sidebar_btn(sidebar, 2, "Dashboard", key="Dashboard", command=self.show_home)
        self._sidebar_btn(sidebar, 3, "Semesters", key="Semesters", command=lambda: self.switch_view("Semesters", self.show_semesters))
        self._sidebar_btn(sidebar, 4, "Students", key="Students", command=lambda: self.switch_view("Students", self.show_students))
        self._sidebar_btn(sidebar, 5, "Lecturers", key="Lecturers", command=lambda: self.switch_view("Lecturers", self.show_lecturers))
        self._sidebar_btn(sidebar, 6, "Courses", key="Courses", command=lambda: self.switch_view("Courses", self.show_courses))
        self._sidebar_btn(sidebar, 7, "Classes", key="Classes", command=lambda: self.switch_view("Classes", self.show_classes))
        self._sidebar_btn(sidebar, 8, "Announcements", key="Announcements", command=lambda: self.switch_view("Announcements", self.show_announcements))

        # Footer
        footer = ctk.CTkFrame(sidebar, fg_color="#F0FDFA", corner_radius=12, height=60)
        footer.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(footer, text="Logged in as:", font=("Arial", 10), text_color="gray").place(relx=0.5, rely=0.3, anchor="center")
        ctk.CTkLabel(footer, text=self.user.full_name, font=("Arial", 12, "bold"), text_color=self.COLOR_PRIMARY).place(relx=0.5, rely=0.6, anchor="center")

        # --- ĐÃ XÓA NÚT SIGN OUT Ở ĐÂY ---

    def _sidebar_btn(self, parent, row, text, key=None, command=None):
        btn = ctk.CTkButton(
            parent, text=text, 
            fg_color="transparent", text_color="#4B5563", 
            hover_color="#F3F4F6", anchor="w", 
            font=("Arial", 14, "bold"), height=45, corner_radius=8,
            command=command
        )
        btn.grid(row=row, column=0, padx=15, pady=4, sticky="ew")
        if key: self.nav_buttons[key] = btn

    # =========================================================================
    # 2. HEADER SECTION (CẬP NHẬT: USER MENU DROPDOWN)
    # =========================================================================
    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=70)
        header.pack(fill="x", padx=30, pady=(20, 0))
        
        # Page Title
        self.page_title = ctk.CTkLabel(header, text="Dashboard Overview", font=("Arial", 24, "bold"), text_color=self.COLOR_TEXT_MAIN)
        self.page_title.pack(side="left", anchor="c")

        # Right Actions
        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right", anchor="c")
        
        # Nút Post Announcement
        ctk.CTkButton(
            right_box, text="+ Post Announcement", 
            fg_color="#0F766E", hover_color="#115E59",
            width=160, height=35, font=("Arial", 13, "bold"),
            command=self.open_quick_post
        ).pack(side="left", padx=(0, 20))
        
        # --- USER PROFILE SECTION (Clickable để hiện menu) ---
        user_section = ctk.CTkFrame(right_box, fg_color="transparent", cursor="hand2")
        user_section.pack(side="left")
        # Gán sự kiện click để mở/đóng menu
        user_section.bind("<Button-1>", self.toggle_user_menu)

        user_info = ctk.CTkFrame(user_section, fg_color="transparent")
        user_info.pack(side="left")
        
        lbl_name = ctk.CTkLabel(user_info, text=self.user.full_name, font=("Arial", 13, "bold"), text_color="#333")
        lbl_name.pack(anchor="e")
        lbl_role = ctk.CTkLabel(user_info, text="ADMINISTRATOR", font=("Arial", 10, "bold"), text_color=self.COLOR_PRIMARY)
        lbl_role.pack(anchor="e")

        avatar = ctk.CTkFrame(user_section, width=40, height=40, corner_radius=20, fg_color="#0F766E")
        avatar.pack(side="left", padx=(10, 0))
        lbl_avatar = ctk.CTkLabel(avatar, text=self.user.full_name[:1], font=("Arial", 16, "bold"), text_color="white")
        lbl_avatar.place(relx=0.5, rely=0.5, anchor="center")

        # Gán sự kiện click cho các thành phần con để đảm bảo click hoạt động
        for w in [lbl_name, lbl_role, avatar, lbl_avatar]:
            w.bind("<Button-1>", self.toggle_user_menu)

    # --- CÁC HÀM XỬ LÝ USER MENU ---
    def toggle_user_menu(self, event=None):
        """Hiện hoặc ẩn menu người dùng."""
        if self.user_menu and self.user_menu.winfo_exists():
            self.user_menu.destroy()
            self.user_menu = None
        else:
            self.create_user_menu()

    def create_user_menu(self):
        """Tạo và hiển thị menu dropdown."""
        self.user_menu = ctk.CTkFrame(self.main_area, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB", width=160)
        # Đặt vị trí menu ngay dưới phần thông tin user ở góc phải
        self.user_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-30, y=85) 
        
        # Nút Sign Out trong menu
        ctk.CTkButton(
            self.user_menu, text="Sign Out", 
            fg_color="transparent", text_color="#EF4444", hover_color="#FEF2F2", 
            anchor="w", font=("Arial", 13, "bold"), width=140, height=35,
            command=self.app.show_login
        ).pack(pady=5, padx=5)

    # Hàm mở dialog post nhanh
    def open_quick_post(self):
        def callback():
            for widget in self.content_scroll.winfo_children():
                if isinstance(widget, AnnouncementsFrame):
                    widget.load_data()
                    break

        AnnouncementDialog(self, "New Announcement", self.controller, callback, user_id=self.user.user_id)

    def _update_stats(self, stats):
        """Callback when stats finish loading from background thread"""
        self.stats = stats
        # Refresh dashboard if home is currently displayed
        if hasattr(self, 'page_title') and self.page_title.cget("text") == "Dashboard Overview":
            self.show_home()

    # =========================================================================
    # 3. DASHBOARD HOME
    # =========================================================================
    def show_home(self):
        self.clear_content()
        self.set_active_menu("Dashboard")
        self.page_title.configure(text="Dashboard Overview")

        # Stats
        stats_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(10, 30))
        
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)

        self._draw_stat_card(stats_frame, 0, "TOTAL STUDENTS", self.stats['students'])
        self._draw_stat_card(stats_frame, 1, "TOTAL LECTURERS", self.stats['lecturers'])
        self._draw_stat_card(stats_frame, 2, "ACTIVE COURSES", self.stats['courses'])
        self._draw_stat_card(stats_frame, 3, "TOTAL CLASSES", self.stats['classes'])

        # Quick Actions
        ctk.CTkLabel(self.content_scroll, text="Quick Actions", font=("Arial", 18, "bold"), text_color=self.COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 15))
        
        actions_grid = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        actions_grid.pack(fill="x", anchor="w")
        
        self._draw_action_btn(actions_grid, "Add New Student", "Create a new student profile", lambda: self.switch_view("Students", self.show_students))
        self._draw_action_btn(actions_grid, "Schedule Class", "Assign room & time", lambda: self.switch_view("Classes", self.show_classes))
        self._draw_action_btn(actions_grid, "Manage Semesters", "Set up new terms", lambda: self.switch_view("Semesters", self.show_semesters))

    def _draw_stat_card(self, parent, col, title, value):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=0)
        card.grid(row=0, column=col, sticky="ew", padx=8)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(inner, text=title, font=("Arial", 11, "bold"), text_color="#6B7280").pack(anchor="w")
        ctk.CTkLabel(inner, text=f"{value}", font=("Arial", 28, "bold"), text_color="#111827").pack(anchor="w", pady=(5, 0))

    def _draw_action_btn(self, parent, title, desc, command):
        btn = ctk.CTkButton(
            parent, text="", fg_color="white", hover_color="#F9FAFB",
            height=70, corner_radius=10, width=200,
            command=command
        )
        btn.pack(side="left", padx=(0, 15))
        
        t_lbl = ctk.CTkLabel(btn, text=title, font=("Arial", 13, "bold"), text_color="#333")
        t_lbl.place(relx=0.1, rely=0.3, anchor="w")
        
        d_lbl = ctk.CTkLabel(btn, text=desc, font=("Arial", 10), text_color="gray")
        d_lbl.place(relx=0.1, rely=0.65, anchor="w")

    # =========================================================================
    # 4. UTILS & NAVIGATION
    # =========================================================================
    def clear_content(self):
        # Đóng menu nếu đang mở khi chuyển trang
        if self.user_menu and self.user_menu.winfo_exists():
            self.user_menu.destroy()
            self.user_menu = None
            
        for widget in self.content_scroll.winfo_children():
            widget.destroy()

    def set_active_menu(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#CCFBF1", text_color=self.COLOR_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color="#4B5563")

    def switch_view(self, title, view_func):
        self.clear_content()
        self.set_active_menu(title)
        self.page_title.configure(text=f"Manage {title}")
        view_func()

    def show_semesters(self):
        SemestersFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_students(self):
        StudentsFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_lecturers(self):
        LecturersFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_courses(self):
        CoursesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_classes(self):
        ClassesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_announcements(self):
        AnnouncementsFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)