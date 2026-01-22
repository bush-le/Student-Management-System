import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController
from views.student.schedule import ScheduleFrame
from views.student.grades import GradesFrame
from views.student.profile import ProfileView 
from views.student.notifications import NotificationsView
import traceback 

class StudentDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F5F7F9")
        self.app = app
        self.user = user
        self.auth_controller = AuthController()
        
        # Trạng thái các Menu
        self.profile_menu_open = False
        self.notification_menu_open = False  # <--- QUAN TRỌNG
        self.nav_buttons = {} 

        try:
            self.controller = StudentController(user.user_id)
            self.next_class = { 'name': 'Data Structures & Algorithms', 'code': 'CS201', 'time': '13:00 - 14:30', 'room': 'B203', 'lecturer': 'Phan Gia Kiệt' }
            
            # --- LAYOUT SETUP ---
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

            # 2.1 Header
            self.create_header()

            # 2.2 Content Scroll
            self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
            self.content_scroll.grid(row=1, column=0, sticky="nswe", padx=20, pady=10)

            # 2.3 KHỞI TẠO CÁC POPUP ẨN (QUAN TRỌNG)
            self.create_profile_dropdown()
            self.create_notification_dropdown() # <--- BẮT BUỘC PHẢI GỌI HÀM NÀY

            # 2.4 Mặc định hiện Home
            self.show_home()

        except Exception as e:
            print("❌ LỖI DASHBOARD:")
            traceback.print_exc()

    # --- HEADER & BELL BUTTON ---
    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        # Info
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text=datetime.now().strftime("%A, %B %d").upper(), font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Welcome back, {self.user.full_name}", font=("Arial", 20, "bold"), text_color="#2A9D8F").pack(anchor="w")

        # Profile Button
        self.profile_btn = ctk.CTkButton(
            header, text=f"  👤  {self.user.full_name}  ⌄", 
            fg_color="white", text_color="#333", font=("Arial", 13, "bold"),
            hover_color="#F0F2F5", corner_radius=20, border_width=1, border_color="#E5E7EB", height=40,
            command=self.toggle_profile_menu
        )
        self.profile_btn.pack(side="right")
        
        # Notification Bell Button
        self.notif_btn = ctk.CTkButton(
            header, text="🔔", 
            fg_color="transparent", text_color="gray", 
            width=40, height=40,
            font=("Arial", 18), hover_color="#F0F2F5",
            command=self.toggle_notification_menu # <--- GẮN SỰ KIỆN Ở ĐÂY
        )
        self.notif_btn.pack(side="right", padx=10)

    # --- NOTIFICATION LOGIC ---
    def create_notification_dropdown(self):
        # Tạo Frame ẩn chứa thông báo
        self.notif_menu = ctk.CTkFrame(self.main_area, width=320, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        
        # Header Container
        header = ctk.CTkFrame(self.notif_menu, fg_color="transparent", height=40)
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Tiêu đề trái
        ctk.CTkLabel(header, text="NOTIFICATIONS", font=("Arial", 11, "bold"), text_color="#555").pack(side="left")
        
        # Nút VIEW ALL bên phải (Màu xanh, Click chuyển màn hình)
        view_all_btn = ctk.CTkButton(
            header, 
            text="VIEW ALL", 
            fg_color="transparent", 
            text_color="#2A9D8F", 
            font=("Arial", 11, "bold"), 
            width=60, 
            hover_color="#E0F2F1",
            command=lambda: [self.toggle_notification_menu(), self.show_notifications()] # <--- LOGIC CHUYỂN TRANG
        )
        view_all_btn.pack(side="right")

        # Separator
        ctk.CTkFrame(self.notif_menu, height=1, fg_color="#F3F4F6").pack(fill="x")

        # List Container
        list_container = ctk.CTkFrame(self.notif_menu, fg_color="white")
        list_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Mock Data ngắn gọn cho Popup
        notifications = [
            {"title": "Midterm Grades Published", "summary": "Fall 2024 midterm grades updated.", "timestamp": "10/25/2024"},
            {"title": "Course Registration", "summary": "Deadline is this Friday.", "timestamp": "08/20/2024"},
            {"title": "Tuition Notice", "summary": "Pay by Feb 15th.", "timestamp": "12/15/2024"}
        ]

        for notif in notifications:
            self._create_notif_item(list_container, notif)

    def _create_notif_item(self, parent, data):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=0)
        
        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(content, text=data['title'], font=("Arial", 13, "bold"), text_color="#1F2937").pack(anchor="w")
        ctk.CTkLabel(content, text=data['summary'], font=("Arial", 12), text_color="#6B7280", wraplength=260, justify="left").pack(anchor="w", pady=(2, 5))
        ctk.CTkLabel(content, text=data['timestamp'], font=("Arial", 10), text_color="#9CA3AF").pack(anchor="w")

        ctk.CTkFrame(parent, height=1, fg_color="#F3F4F6").pack(fill="x", padx=15)

    def toggle_notification_menu(self):
        # Đóng Profile menu nếu đang mở
        if self.profile_menu_open:
            self.toggle_profile_menu()

        if self.notification_menu_open:
            self.notif_menu.place_forget()
            self.notification_menu_open = False
        else:
            # Hiển thị popup bên dưới nút chuông
            self.notif_menu.place(relx=0.88, rely=0.12, anchor="ne") 
            self.notif_menu.lift()
            self.notification_menu_open = True

    def show_notifications(self):
        self.clear_content()
        
        # Reset cấu hình cột về 1 cột duy nhất để nội dung giãn ra
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        
        self.set_active_nav("none") 
        
        # QUAN TRỌNG: pack(fill="both", expand=True) để View con chiếm hết chỗ của content_scroll
        NotificationsView(self.content_scroll).pack(fill="both", expand=True)

    # --- PROFILE MENU LOGIC ---
    def create_profile_dropdown(self):
        self.profile_menu = ctk.CTkFrame(self.main_area, width=220, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        ctk.CTkLabel(self.profile_menu, text=self.user.email, font=("Arial", 12, "bold"), text_color="#555").pack(pady=(15, 10), padx=15, anchor="w")
        ctk.CTkFrame(self.profile_menu, height=1, fg_color="#F3F4F6").pack(fill="x")
        
        self._menu_item("👤  My Profile", lambda: [self.toggle_profile_menu(), self.set_active_nav("profile"), self.show_profile()])
        self._menu_item("🔒  Change Password", self.open_change_password_popup)
        ctk.CTkFrame(self.profile_menu, height=1, fg_color="#F3F4F6").pack(fill="x")
        self._menu_item("🚪  Sign Out", self.app.show_login, color="#E76F51")

    def _menu_item(self, text, cmd, color="#333"):
        ctk.CTkButton(self.profile_menu, text=text, fg_color="white", text_color=color, hover_color="#F3F4F6", anchor="w", height=40, command=cmd).pack(fill="x", padx=5, pady=2)

    def toggle_profile_menu(self):
        if self.notification_menu_open:
            self.toggle_notification_menu() # Đóng notif nếu đang mở

        if self.profile_menu_open:
            self.profile_menu.place_forget()
            self.profile_menu_open = False
        else:
            self.profile_menu.place(relx=0.97, rely=0.12, anchor="ne")
            self.profile_menu.lift()
            self.profile_menu_open = True

    # --- CHANGE PASSWORD POPUP (BẢN FIX TRẮNG) ---
    def open_change_password_popup(self):
        if self.profile_menu_open: self.toggle_profile_menu()
        
        root = self.winfo_toplevel()
        popup = ctk.CTkToplevel(root)
        popup.title("Change Password")
        popup.geometry("400x480")
        popup.resizable(False, False)
        
        bg = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
        bg.pack(fill="both", expand=True)
        popup.transient(root)
        
        # Center popup
        popup.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 240
        popup.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(bg, text="Change Password", font=("Arial", 22, "bold"), text_color="#1F2937").pack(pady=(30, 20))
        
        popup.curr = self._create_popup_input(bg, "Current Password")
        popup.new = self._create_popup_input(bg, "New Password")
        popup.conf = self._create_popup_input(bg, "Confirm New Password")
        
        ctk.CTkButton(bg, text="Update Password", fg_color="#2A9D8F", height=45, font=("Arial", 14, "bold"), 
                      command=lambda: self.handle_popup_submit(popup)).pack(pady=30, padx=40, fill="x")
        
        popup.lift()
        popup.focus_force()
        popup.grab_set()

    def _create_popup_input(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(10, 5))
        entry = ctk.CTkEntry(parent, show="•", height=40, border_color="#E5E7EB", fg_color="#F9FAFB", text_color="black")
        entry.pack(padx=40, fill="x")
        return entry

    def handle_popup_submit(self, popup):
        curr, new_p, conf_p = popup.curr.get(), popup.new.get(), popup.conf.get()
        if not curr or not new_p: 
            messagebox.showerror("Error", "Empty fields", parent=popup); return
        if new_p != conf_p: 
            messagebox.showerror("Error", "Mismatch", parent=popup); return
            
        success, msg = self.auth_controller.change_password(self.user.user_id, curr, new_p)
        if success: messagebox.showinfo("Success", msg, parent=popup); popup.destroy()
        else: messagebox.showerror("Error", msg, parent=popup)

    # --- SIDEBAR & NAV ---
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="white")
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.sidebar, text="🎓 SMS Portal", font=("Arial", 22, "bold"), text_color="#2A9D8F").grid(row=0, column=0, pady=30, padx=20)

        self.create_nav_btn("Dashboard", 1, self.show_home, "🏠", "home")
        self.create_nav_btn("My Schedule", 2, self.show_schedule, "📅", "schedule")
        self.create_nav_btn("Academic Results", 3, self.show_grades, "📊", "grades")
        self.create_nav_btn("My Profile", 4, self.show_profile, "👤", "profile")

        ctk.CTkButton(self.sidebar, text="🚪 Sign Out", fg_color="transparent", text_color="#E76F51", hover_color="#FEF2F2", anchor="w", font=("Arial", 14), height=50, command=self.app.show_login).grid(row=7, column=0, padx=20, pady=20, sticky="ew")

    def create_nav_btn(self, text, row, cmd, icon, key):
        btn = ctk.CTkButton(self.sidebar, text=f"  {icon}   {text}", fg_color="transparent", text_color="#555", hover_color="#E0F2F1", anchor="w", font=("Arial", 14), height=50, command=lambda: [self.set_active_nav(key), cmd()])
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        self.nav_buttons[key] = btn

    def set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            color = "#E0F2F1" if k == key else "transparent"
            t_col = "#2A9D8F" if k == key else "#555"
            font_w = "bold" if k == key else "normal"
            btn.configure(fg_color=color, text_color=t_col, font=("Arial", 14, font_w))

    # --- SHOW CONTENT PAGES ---
    def clear_content(self):
        for widget in self.content_scroll.winfo_children(): widget.destroy()

    def show_profile(self):
        self.clear_content()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ProfileView(self.content_scroll, self.user).pack(fill="both", expand=True)

    def show_schedule(self):
        self.clear_content()
        # Reset cấu hình cột về 1 cột duy nhất để nội dung giãn ra toàn màn hình
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ScheduleFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_grades(self):
        self.clear_content()
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        GradesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_home(self):
        self.clear_content()
        self.set_active_nav("home")
        self.content_scroll.grid_columnconfigure(0, weight=2)
        self.content_scroll.grid_columnconfigure(1, weight=1)

        left_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nswe", padx=(0, 20))
        self.create_hero_card(left_col)
        self.create_stats_row(left_col)
        self.create_recent_performance(left_col)

        right_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nswe")
        self.create_notifications_panel(right_col)
        self.create_quick_links(right_col)

    # --- HOME WIDGETS ---
    def create_hero_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#2A9D8F", corner_radius=15)
        card.pack(fill="x", pady=(0, 20))
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20, 10))
        ctk.CTkLabel(top, text="NEXT CLASS", font=("Arial", 10, "bold"), text_color="white", fg_color="#57B6AB", corner_radius=5).pack(side="left")
        ctk.CTkLabel(top, text="🕒", font=("Arial", 20), text_color="#D1ECE9").pack(side="right")
        ctk.CTkLabel(card, text=self.next_class['name'], font=("Arial", 24, "bold"), text_color="white").pack(anchor="w", padx=25)
        ctk.CTkLabel(card, text=self.next_class['code'], font=("Arial", 14), text_color="#E0F2F1").pack(anchor="w", padx=25, pady=(0, 20))
        bot = ctk.CTkFrame(card, fg_color="#42ACA1", corner_radius=10)
        bot.pack(fill="x", padx=25, pady=(0, 25))
        ctk.CTkLabel(bot, text="TIME", font=("Arial", 9, "bold"), text_color="#B2DFDB").pack(side="left", padx=(20, 0), pady=10)
        ctk.CTkLabel(bot, text=self.next_class['time'], font=("Arial", 13, "bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(bot, text="LOCATION", font=("Arial", 9, "bold"), text_color="#B2DFDB").pack(side="left", padx=(20, 0))
        ctk.CTkLabel(bot, text=self.next_class['room'], font=("Arial", 13, "bold"), text_color="white").pack(side="left", padx=5)

    def create_stats_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))
        for icon, title, val, col in [("📊","GPA","3.65","#2563EB"), ("📖","CREDITS","45","#9333EA"), ("📅","SEMESTER","5th","#16A34A")]:
            card = ctk.CTkFrame(row, fg_color="white", corner_radius=10)
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
        for name, grade in [("Intro to Programming", 8.8), ("Circuit Analysis", 9.2)]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row, text=name, font=("Arial", 12, "bold"), text_color="#333").pack(side="left")
            ctk.CTkLabel(row, text=str(grade), font=("Arial", 12, "bold"), text_color="#16A34A").pack(side="right")
            ctk.CTkFrame(card, height=1, fg_color="#F3F4F6").pack(fill="x", padx=20, pady=5)

    def create_notifications_panel(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(card, text="Announcements", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        for title, msg, col in [("Midterm Grades", "Updated for Fall 2024.", "#2563EB"), ("Tuition Notice", "Pay by Feb 15th.", "#DC2626")]:
            row = ctk.CTkFrame(card, fg_color="transparent")
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
        self._link_btn(card, "📅 My Schedule", lambda: [self.set_active_nav("schedule"), self.show_schedule()])
        self._link_btn(card, "📊 Academic Results", lambda: [self.set_active_nav("grades"), self.show_grades()])
        self._link_btn(card, "👤 Update Profile", lambda: [self.set_active_nav("profile"), self.show_profile()])

    def _link_btn(self, parent, txt, cmd):
        ctk.CTkButton(parent, text=txt, fg_color="white", text_color="#333", hover_color="#F3F4F6", anchor="w", border_width=1, border_color="#E5E7EB", command=cmd).pack(fill="x", padx=20, pady=5)