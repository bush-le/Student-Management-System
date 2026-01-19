import customtkinter as ctk
from datetime import datetime
from controllers.student_controller import StudentController
from views.student.schedule import ScheduleFrame
from views.student.grades import GradesFrame
import traceback 

class StudentDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F5F7F9")
        self.app = app
        self.user = user
        self.profile_menu_open = False # Trạng thái menu
        
        try:
            self.controller = StudentController(user.user_id)

            self.next_class = {
                'name': 'Data Structures & Algorithms',
                'code': 'CS201',
                'time': '13:00 - 14:30',
                'room': 'B203',
                'lecturer': 'Phan Gia Kiệt'
            }
            
            # Cấu hình Grid
            self.grid_columnconfigure(0, weight=0) 
            self.grid_columnconfigure(1, weight=1) 
            self.grid_rowconfigure(0, weight=1)

            # 1. Sidebar
            self.create_sidebar()

            # 2. Main Area
            self.main_area = ctk.CTkFrame(self, fg_color="#F5F7F9", corner_radius=0)
            self.main_area.grid(row=0, column=1, sticky="nswe")
            
            self.main_area.grid_rowconfigure(1, weight=1)
            self.main_area.grid_columnconfigure(0, weight=1)

            # 2.1 Header (Đã chỉnh sửa để có nút Profile)
            self.create_header()

            # 2.2 Scrollable Content
            self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
            self.content_scroll.grid(row=1, column=0, sticky="nswe", padx=20, pady=10)
            
            self.content_scroll.grid_columnconfigure(0, weight=2)
            self.content_scroll.grid_columnconfigure(1, weight=1)

            # 2.3 Profile Dropdown Menu (Khởi tạo ẩn)
            self.create_profile_dropdown()

            self.show_home()

        except Exception as e:
            print("❌ LỖI KHỞI TẠO DASHBOARD:")
            traceback.print_exc()
            error_lbl = ctk.CTkLabel(self, text=f"Error loading dashboard: {e}", text_color="red")
            error_lbl.grid(row=0, column=0, columnspan=2, pady=50)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="white")
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self.sidebar, text="🎓 SMS Portal", font=("Arial", 22, "bold"), text_color="#2A9D8F").grid(row=0, column=0, pady=30, padx=20)

        self.create_nav_btn("Dashboard", 1, self.show_home, "🏠", True)
        self.create_nav_btn("My Schedule", 2, self.show_schedule, "📅")
        self.create_nav_btn("Academic Results", 3, self.show_grades, "📊")

        ctk.CTkButton(
            self.sidebar, text="🚪 Sign Out", fg_color="transparent", 
            text_color="#E76F51", hover_color="#FEF2F2", anchor="w", 
            font=("Arial", 14), height=50, command=self.app.show_login
        ).grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    def create_nav_btn(self, text, row, cmd, icon, is_active=False):
        color = "#E0F2F1" if is_active else "transparent"
        text_col = "#2A9D8F" if is_active else "#555"
        btn = ctk.CTkButton(
            self.sidebar, text=f"  {icon}   {text}", fg_color=color, text_color=text_col, 
            hover_color="#E0F2F1", anchor="w", font=("Arial", 14, "bold" if is_active else "normal"), 
            height=50, command=cmd
        )
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")

    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        # Left: Date & Welcome
        left_box = ctk.CTkFrame(header, fg_color="transparent")
        left_box.pack(side="left")
        
        date_str = datetime.now().strftime("%A, %B %d").upper()
        ctk.CTkLabel(left_box, text=date_str, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        
        wel = ctk.CTkFrame(left_box, fg_color="transparent")
        wel.pack(anchor="w")
        ctk.CTkLabel(wel, text="Welcome back, ", font=("Arial", 24), text_color="#333").pack(side="left")
        ctk.CTkLabel(wel, text=self.user.full_name, font=("Arial", 24, "bold"), text_color="#2A9D8F").pack(side="left")

        # Right: User Profile Button (Trigger Menu)
        # Tạo nút bấm nhìn giống Avatar + Tên
        self.profile_btn = ctk.CTkButton(
            header, 
            text=f"  👤  {self.user.full_name}  ⌄", 
            fg_color="white", 
            text_color="#333",
            font=("Arial", 13, "bold"),
            hover_color="#F0F2F5",
            corner_radius=20,
            border_width=1,
            border_color="#E5E7EB",
            height=40,
            command=self.toggle_profile_menu # Bấm vào gọi hàm toggle
        )
        self.profile_btn.pack(side="right", anchor="center")
        
        # Nút thông báo
        ctk.CTkButton(header, text="🔔", fg_color="transparent", text_color="gray", width=40, font=("Arial", 18), hover_color="#F0F2F5").pack(side="right", padx=10)

    # --- POPUP MENU LOGIC ---
    def create_profile_dropdown(self):
        """Tạo Frame Menu nhưng chưa hiện lên (place quên)"""
        self.profile_menu = ctk.CTkFrame(self.main_area, width=250, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        
        # Ngăn sự kiện click xuyên qua menu
        self.profile_menu.bind("<Button-1>", lambda e: "break")

        # 1. Account Info Section
        info_frame = ctk.CTkFrame(self.profile_menu, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(info_frame, text="ACCOUNT", font=("Arial", 10, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=self.user.email, font=("Arial", 12, "bold"), text_color="#333").pack(anchor="w")

        # 2. Menu Items
        self._menu_item("👤  My Profile", lambda: print("Go to Profile"))
        self._menu_item("🔒  Change Password", lambda: print("Change Pass"))

        # Separator
        ctk.CTkFrame(self.profile_menu, height=1, fg_color="#F3F4F6").pack(fill="x", padx=10, pady=5)

        # 3. Sign Out (Red)
        signout_btn = ctk.CTkButton(
            self.profile_menu, 
            text="🚪  Sign Out", 
            fg_color="white", 
            text_color="#E76F51", # Màu đỏ cam
            hover_color="#FEF2F2", 
            anchor="w", 
            font=("Arial", 13, "bold"),
            height=40,
            command=self.app.show_login
        )
        signout_btn.pack(fill="x", padx=10, pady=(5, 10))

    def _menu_item(self, text, cmd):
        btn = ctk.CTkButton(
            self.profile_menu, 
            text=text, 
            fg_color="white", 
            text_color="#333", 
            hover_color="#F3F4F6", 
            anchor="w", 
            font=("Arial", 13),
            height=40,
            command=cmd
        )
        btn.pack(fill="x", padx=10, pady=2)

    def toggle_profile_menu(self):
        if self.profile_menu_open:
            self.profile_menu.place_forget() # Ẩn đi
            self.profile_menu_open = False
        else:
            # Hiện lên ở góc phải trên (dưới nút Profile)
            self.profile_menu.place(relx=0.97, rely=0.12, anchor="ne")
            self.profile_menu.lift() # Đảm bảo nằm trên cùng
            self.profile_menu_open = True

    # -------------------------

    def show_home(self):
        self.clear_content()
        
        left_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nswe", padx=(0, 20))
        
        self.create_hero_card(left_col)
        self.create_stats_row(left_col)
        self.create_recent_performance(left_col)

        right_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nswe")
        
        self.create_notifications_panel(right_col)
        self.create_quick_links(right_col)

    def create_hero_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#2A9D8F", corner_radius=15)
        card.pack(fill="x", pady=(0, 20))
        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(top, text="NEXT CLASS", font=("Arial", 10, "bold"), text_color="white", 
                     fg_color="#57B6AB", corner_radius=5).pack(side="left")
        ctk.CTkLabel(top, text="🕒", font=("Arial", 20), text_color="#D1ECE9").pack(side="right")

        ctk.CTkLabel(card, text=self.next_class['name'], font=("Arial", 24, "bold"), text_color="white").pack(anchor="w", padx=25)
        ctk.CTkLabel(card, text=self.next_class['code'], font=("Arial", 14), text_color="#E0F2F1").pack(anchor="w", padx=25, pady=(0, 20))

        bot = ctk.CTkFrame(card, fg_color="#42ACA1", corner_radius=10)
        bot.pack(fill="x", padx=25, pady=(0, 25))
        
        self._hero_item(bot, "TIME", self.next_class['time'], "left")
        self._hero_item(bot, "LOCATION", f"Room {self.next_class['room']}", "left")

    def _hero_item(self, parent, title, val, side):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, padx=20, pady=10, expand=True, fill="x")
        ctk.CTkLabel(f, text=title, font=("Arial", 9, "bold"), text_color="#B2DFDB").pack(anchor="w")
        ctk.CTkLabel(f, text=val, font=("Arial", 13, "bold"), text_color="white").pack(anchor="w")

    def create_stats_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))
        self._stat_card(row, "📊", "GPA", "3.65", "#2563EB")
        self._stat_card(row, "📖", "CREDITS", "45", "#9333EA")
        self._stat_card(row, "📅", "SEMESTER", "5th", "#16A34A")

    def _stat_card(self, parent, icon, title, val, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(card, text=icon, font=("Arial", 20), text_color=col).pack(side="left", padx=15, pady=15)
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(side="left", pady=15)
        ctk.CTkLabel(box, text=title, font=("Arial", 10, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(box, text=val, font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w")

    def create_recent_performance(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x")
        ctk.CTkLabel(card, text="Recent Performance", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        self._perf_row(card, "Intro to Programming", "Final", 8.8, "#16A34A")
        self._perf_row(card, "Circuit Analysis", "Final", 9.2, "#16A34A")

    def _perf_row(self, parent, name, type_, grade, col):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row, text=name, font=("Arial", 12, "bold"), text_color="#333").pack(side="left")
        ctk.CTkLabel(row, text=str(grade), font=("Arial", 12, "bold"), text_color=col).pack(side="right")
        ctk.CTkFrame(parent, height=1, fg_color="#F3F4F6").pack(fill="x", padx=20, pady=5)

    def create_notifications_panel(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(card, text="Announcements", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        self._notif_item(card, "Midterm Grades", "Updated for Fall 2024.", "#2563EB")
        self._notif_item(card, "Tuition Notice", "Pay by Feb 15th.", "#DC2626")

    def _notif_item(self, parent, title, msg, col):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row, text="●", text_color=col, font=("Arial", 10)).pack(side="left", anchor="n", pady=3)
        box = ctk.CTkFrame(row, fg_color="transparent")
        box.pack(side="left", padx=10)
        ctk.CTkLabel(box, text=title, font=("Arial", 12, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(box, text=msg, font=("Arial", 11), text_color="gray").pack(anchor="w")

    def create_quick_links(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x")
        ctk.CTkLabel(card, text="Quick Links", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        self._link_btn(card, "📅 My Schedule", self.show_schedule)
        self._link_btn(card, "📊 Academic Results", self.show_grades)

    def _link_btn(self, parent, txt, cmd):
        ctk.CTkButton(parent, text=txt, fg_color="white", text_color="#333", hover_color="#F3F4F6", 
                      anchor="w", border_width=1, border_color="#E5E7EB", command=cmd).pack(fill="x", padx=20, pady=5)

    def clear_content(self):
        for widget in self.content_scroll.winfo_children():
            widget.destroy()

    def show_schedule(self):
        self.clear_content()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ScheduleFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_grades(self):
        self.clear_content()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        GradesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)