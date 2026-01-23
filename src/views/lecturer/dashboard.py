import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
import traceback

from controllers.lecturer_controller import LecturerController
from controllers.auth_controller import AuthController

# Import các View con (Đã bỏ ProfileView)
from views.lecturer.schedule import LecturerScheduleFrame
from views.lecturer.my_class import LecturerClassesFrame
from views.lecturer.class_manager import LecturerClassManager

class LecturerDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F3F4F6") # Nền xám nhạt
        self.app = app
        self.user = user
        self.auth_controller = AuthController()
        
        # --- COLOR PALETTE ---
        self.COLOR_PRIMARY = "#0F766E"      # Teal đậm
        self.COLOR_ACCENT = "#14B8A6"       # Teal sáng
        self.COLOR_SIDEBAR = "#FFFFFF"      # Trắng
        self.COLOR_TEXT_MAIN = "#111827"    # Đen
        self.COLOR_TEXT_SUB = "#6B7280"     # Xám
        
        self.nav_buttons = {}
        self.user_menu_open = False
        
        try:
            self.controller = LecturerController(user.user_id)
            
            # --- LOAD REAL DATA ---
            self.load_dashboard_data()
            
            # --- LAYOUT SETUP ---
            self.grid_columnconfigure(0, weight=0) # Sidebar
            self.grid_columnconfigure(1, weight=1) # Main
            self.grid_rowconfigure(0, weight=1)

            # 1. Sidebar
            self.create_sidebar()

            # 2. Main Area
            self.main_area = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0)
            self.main_area.grid(row=0, column=1, sticky="nswe")
            self.main_area.grid_rowconfigure(1, weight=1)
            self.main_area.grid_columnconfigure(0, weight=1)

            # 2.1 Header
            self.create_header()

            # 2.2 Content Scroll
            self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
            self.content_scroll.grid(row=1, column=0, sticky="nswe", padx=30, pady=(10, 30))

            # 2.3 Popups
            self.create_user_menu_frame()

            # 2.4 Default Page
            self.show_home()

        except Exception as e:
            print("❌ LỖI KHỞI TẠO DASHBOARD GIẢNG VIÊN:")
            traceback.print_exc()

    def load_dashboard_data(self):
        """Lấy dữ liệu từ DB thông qua Controller"""
        try:
            self.next_class = self.controller.get_upcoming_teaching_class() 
            self.stats = self.controller.get_teaching_stats() 
        except Exception as e:
            print(f"⚠️ Không tải được dữ liệu dashboard: {e}")
            self.next_class = None
            self.stats = {}

    # =========================================================================
    # 1. SIDEBAR (NO PROFILE BUTTON)
    # =========================================================================
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=self.COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(10, weight=1)

        # Branding
        logo_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=20, pady=30, sticky="ew")
        
        ctk.CTkLabel(logo_box, text="LECTURER PORTAL", font=("Arial", 16, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(logo_box, text="Academic System", font=("Arial", 10, "bold"), text_color=self.COLOR_TEXT_SUB).pack(anchor="w")

        # Menu
        ctk.CTkLabel(sidebar, text="MAIN MENU", font=("Arial", 11, "bold"), text_color="#9CA3AF").grid(row=1, column=0, sticky="w", padx=30, pady=(20, 10))

        self._sidebar_btn(sidebar, 2, "Dashboard", "home", self.show_home)
        self._sidebar_btn(sidebar, 3, "Teaching Schedule", "schedule", self.show_schedule)
        self._sidebar_btn(sidebar, 4, "Manage Classes", "classes", self.show_classes)
        # Đã xóa nút Profile ở đây

        # Footer User Info
        footer = ctk.CTkFrame(sidebar, fg_color="#F0FDFA", corner_radius=0, height=60)
        footer.grid(row=11, column=0, sticky="ew")
        
        f_inner = ctk.CTkFrame(footer, fg_color="transparent")
        f_inner.pack(padx=20, pady=15, fill="x")
        ctk.CTkLabel(f_inner, text="Logged in as:", font=("Arial", 10), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(f_inner, text=self.user.full_name, font=("Arial", 12, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w")

    def _sidebar_btn(self, parent, row, text, key, command):
        btn = ctk.CTkButton(
            parent, text=text, 
            fg_color="transparent", text_color="#4B5563", 
            hover_color="#F3F4F6", anchor="w", 
            font=("Arial", 13, "bold"), height=45, corner_radius=5,
            command=lambda: [self.set_active_nav(key), command()]
        )
        btn.grid(row=row, column=0, padx=15, pady=2, sticky="ew")
        self.nav_buttons[key] = btn

    def set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#CCFBF1", text_color=self.COLOR_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color="#4B5563")

    # =========================================================================
    # 2. HEADER
    # =========================================================================
    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 0))
        
        self.page_title = ctk.CTkLabel(header, text="Overview", font=("Arial", 22, "bold"), text_color=self.COLOR_TEXT_MAIN)
        self.page_title.pack(side="left", anchor="c")

        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right", anchor="c")
        
        # Date
        today = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(right_box, text=today, font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=15)

        # Profile Button
        ctk.CTkButton(
            right_box, text=self.user.full_name, width=130, height=32,
            fg_color=self.COLOR_PRIMARY, text_color="white", 
            hover_color=self.COLOR_ACCENT, font=("Arial", 11, "bold"),
            command=self.toggle_user_menu
        ).pack(side="left", padx=5)

    # =========================================================================
    # 3. HOME CONTENT
    # =========================================================================
    def show_home(self):
        self.show_home_view()

    def show_home_view(self):
        self.clear_content()
        self.set_active_nav("home")
        self.page_title.configure(text="Lecturer Dashboard")
        
        # Layout cân bằng 1:1
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=1)

        # LEFT COLUMN
        left = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 20))
        
        self.create_hero_card(left)
        self.create_stats_row(left)

        # RIGHT COLUMN
        right = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nswe")
        
        self.create_quick_actions(right)

    def create_hero_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#0F766E", corner_radius=10)
        card.pack(fill="x", pady=(0, 20))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(inner, text="NEXT TEACHING SESSION", font=("Arial", 10, "bold"), text_color="#CCFBF1").pack(anchor="w")
        
        if self.next_class:
            c_name = self.next_class.get('course_name', 'Unknown')
            c_room = self.next_class.get('room', 'TBA')
            c_time = self.next_class.get('time', 'TBA')
            
            ctk.CTkLabel(inner, text=c_name, font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", pady=(5, 0))
            ctk.CTkLabel(inner, text=f"Room: {c_room}  |  Time: {c_time}", font=("Arial", 13), text_color="#99F6E4").pack(anchor="w", pady=(5, 0))
        else:
            ctk.CTkLabel(inner, text="No classes scheduled for today.", font=("Arial", 18, "bold"), text_color="white").pack(anchor="w", pady=(10, 0))
            ctk.CTkLabel(inner, text="Have a great day!", font=("Arial", 12), text_color="#99F6E4").pack(anchor="w")

    def create_stats_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))
        
        total_students = str(self.stats.get('total_students', 0))
        total_classes = str(self.stats.get('total_classes', 0))
        
        self._stat_box(row, "Active Classes", total_classes, "left")
        self._stat_box(row, "Total Students", total_students, "right")

    def _stat_box(self, parent, title, value, side):
        box = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        box.pack(side=side, fill="x", expand=True, padx=(0, 10) if side=="left" else (10, 0))
        
        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(inner, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(inner, text=value, font=("Arial", 20, "bold"), text_color="#333").pack(anchor="w")

    def create_quick_actions(self, parent):
        container = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        container.pack(fill="x", pady=(0, 20))
        
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(inner, text="Quick Actions", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(0, 15))
        
        # Đã xóa nút Update Profile
        self._action_btn(inner, "Grade Assignments", lambda: [self.set_active_nav("classes"), self.show_classes()])
        self._action_btn(inner, "Check Schedule", lambda: [self.set_active_nav("schedule"), self.show_schedule()])

    def _action_btn(self, parent, txt, cmd):
        btn = ctk.CTkButton(
            parent, text=txt, fg_color="white", text_color="#333", 
            hover_color="#F3F4F6", anchor="w", height=45,
            border_width=1, border_color="#E5E7EB", font=("Arial", 12, "bold"),
            command=cmd
        )
        btn.pack(fill="x", pady=5)

    # =========================================================================
    # 4. USER MENU (NO PROFILE BUTTON)
    # =========================================================================
    def create_user_menu_frame(self):
        self.user_menu = ctk.CTkFrame(self.main_area, width=220, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        
        # Header
        h = ctk.CTkFrame(self.user_menu, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(h, text="ACCOUNT", font=("Arial", 10, "bold"), text_color="#9CA3AF").pack(anchor="w")
        ctk.CTkLabel(h, text=getattr(self.user, 'email', ''), font=("Arial", 12, "bold"), text_color="#333").pack(anchor="w")
        
        ctk.CTkFrame(self.user_menu, height=1, fg_color="#F3F4F6").pack(fill="x", pady=5)
        
        # Đã xóa nút My Profile
        self._menu_btn("Change Password", self.open_change_password)
        
        ctk.CTkFrame(self.user_menu, height=1, fg_color="#F3F4F6").pack(fill="x", pady=5)
        self._menu_btn("Sign Out", self.app.show_login, color="#EF4444")

    def _menu_btn(self, text, cmd, color="#333"):
        ctk.CTkButton(
            self.user_menu, text=text, fg_color="white", text_color=color, 
            hover_color="#F3F4F6", anchor="w", height=40, font=("Arial", 12),
            command=lambda: [self.toggle_user_menu(), cmd()]
        ).pack(fill="x", padx=5, pady=2)

    def toggle_user_menu(self):
        if self.user_menu.winfo_ismapped(): 
            self.user_menu.place_forget()
        else:
            self.user_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-30, y=80)
            self.user_menu.lift()

    def open_change_password(self):
        messagebox.showinfo("Info", "Change Password Feature")

    # =========================================================================
    # 5. NAVIGATION
    # =========================================================================
    def clear_content(self):
        if self.user_menu.winfo_ismapped(): self.user_menu.place_forget()
        for w in self.content_scroll.winfo_children(): w.destroy()

    def show_schedule(self):
        self.clear_content()
        self.set_active_nav("schedule")
        self.page_title.configure(text="Teaching Schedule")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturerScheduleFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_classes(self):
        self.clear_content()
        self.set_active_nav("classes")
        self.page_title.configure(text="Class Management")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturerClassesFrame(self.content_scroll, self, self.user.user_id).pack(fill="both", expand=True)

    def open_class_manager(self, class_data):
        self.clear_content()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturerClassManager(self.content_scroll, self.user.user_id, class_data, on_back_callback=self.show_my_classes).pack(fill="both", expand=True)

    def show_my_classes(self):
        # Alias để nút Back hoạt động đúng
        self.show_classes()