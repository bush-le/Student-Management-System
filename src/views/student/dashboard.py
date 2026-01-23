import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController
from views.student.schedule import ScheduleFrame
from views.student.grades import GradesFrame
from views.student.profile import ProfileView 
from views.student.notifications import NotificationsView
from utils.threading_helper import run_in_background
import traceback

class StudentDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F3F4F6")
        self.app = app
        self.user = user
        self.auth_controller = AuthController()
        
        self.COLOR_PRIMARY = "#0F766E"      # Dark Teal
        self.COLOR_ACCENT = "#14B8A6"       # Light Teal
        self.COLOR_SIDEBAR = "#FFFFFF"      # White
        self.COLOR_TEXT_MAIN = "#111827"    # Black
        self.COLOR_TEXT_SUB = "#6B7280"     # Gray
        
        # State
        self.nav_buttons = {} 
        self.active_view = "home" # Track current active view

        try:
            self.controller = StudentController(user.user_id)
            
            # Initialize default data
            self.next_class = None
            self.stats = {'gpa': 0.0, 'credits': 0, 'semester': 'N/A'}
            self.recent_grades = []
            self.announcements = []
            
            # --- LAYOUT SETUP ---
            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # 1. Sidebar
            self.create_sidebar()

            # 2. Main Area
            self.main_area = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0)
            self.main_area.grid(row=0, column=1, sticky="nswe")
            self.main_area.grid_rowconfigure(1, weight=1)
            self.main_area.grid_columnconfigure(0, weight=1)

            self.create_header()

            self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
            self.content_scroll.grid(row=1, column=0, sticky="nswe", padx=30, pady=(10, 30))

            self.create_user_menu_frame()
            self.create_notif_menu_frame()

            # Load real data from DB in background
            self.load_real_data()

        except Exception as e:
            print("❌ DASHBOARD INITIALIZATION ERROR:")
            traceback.print_exc()

    def load_real_data(self):
        """Loads data from the controller in a background thread"""
        run_in_background(
            self._fetch_dashboard_data,
            on_complete=self._on_data_loaded,
            tk_root=self.winfo_toplevel()
        )

    def _fetch_dashboard_data(self):
        try:
            # Check for method existence before calling to avoid AttributeError
            # This allows the Dashboard to still display other data sections if a method is missing
            
            # OPTIMIZATION: Fetch stats and recent grades in one go
            stats, recent = self.controller.get_dashboard_academic_summary()
            
            data = {
                'next_class': self.controller.get_upcoming_class() if hasattr(self.controller, 'get_upcoming_class') else None,
                'stats': stats,
                'recent_grades': recent,
                'announcements': self.controller.get_latest_announcements(limit=3) if hasattr(self.controller, 'get_latest_announcements') else []
            }
            return data
        except Exception as e:
            print(f"⚠️ Error fetching data: {e}")
            return None

    def _on_data_loaded(self, data):
        # SAFETY CHECK: Ensure widget still exists before updating UI
        if not self.winfo_exists(): return

        if data:
            self.next_class = data['next_class']
            self.stats = data['stats']
            self.recent_grades = data['recent_grades']
            self.announcements = data['announcements']
            
        # UX FIX: Only refresh UI if user is still on the Dashboard Home
        if self.active_view == "home":
            self.show_home()
        self.update_notif_menu()

    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 0))
        
        self.page_title = ctk.CTkLabel(header, text="Dashboard", font=("Arial", 22, "bold"), text_color=self.COLOR_TEXT_MAIN)
        self.page_title.pack(side="left", anchor="c")

        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right", anchor="c")
        
        # Date display
        today = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(right_box, text=today, font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=15)

        # Notifications Button
        ctk.CTkButton(
            right_box, text="Notifications", width=90, height=32, 
            fg_color="white", text_color="#333", border_color="#D1D5DB", border_width=1,
            hover_color="#F3F4F6", font=("Arial", 11, "bold"),
            command=self.toggle_notif_menu
        ).pack(side="left", padx=5)

        # Profile Button
        ctk.CTkButton(
            right_box, text=self.user.full_name, width=120, height=32,
            fg_color=self.COLOR_PRIMARY, text_color="white", 
            hover_color=self.COLOR_ACCENT, font=("Arial", 11, "bold"),
            command=self.toggle_user_menu
        ).pack(side="left", padx=5)

    # =========================================================================
    # 4. USER MENU & NOTIFICATIONS POPUPS
    # =========================================================================
    def create_user_menu_frame(self):
        """Creates a Popup Menu with Account Header and Email"""
        self.user_menu = ctk.CTkFrame(
            self.main_area, 
            width=240, 
            fg_color="white", 
            corner_radius=8, 
            border_width=1, 
            border_color="#E5E7EB"
        )
        
        # --- 1. HEADER SECTION (ACCOUNT INFO) ---
        header_frame = ctk.CTkFrame(self.user_menu, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Small gray "ACCOUNT" label
        ctk.CTkLabel(
            header_frame, 
            text="ACCOUNT", 
            font=("Arial", 10, "bold"), 
            text_color="#9CA3AF"
        ).pack(anchor="w")
        # User Email (Bold, black)
        # Get email from user object, with fallback
        user_email = getattr(self.user, 'email', '')
        ctk.CTkLabel(
            header_frame, 
            text=user_email, 
            font=("Arial", 13, "bold"), 
            text_color="#1F2937"
        ).pack(anchor="w", pady=(2, 0))
        
        # Separator line
        ctk.CTkFrame(self.user_menu, height=1, fg_color="#F3F4F6").pack(fill="x", pady=5)
        
        # --- 2. MENU ITEMS ---
        self._menu_btn(self.user_menu, "My Profile", self.show_profile)
        self._menu_btn(self.user_menu, "Change Password", self.open_change_password_popup)
        
        # Separator line before Sign Out button
        ctk.CTkFrame(self.user_menu, height=1, fg_color="#F3F4F6").pack(fill="x", pady=5)
        
        # --- 3. SIGN OUT (RED) ---
        self._menu_btn(
            self.user_menu, "Sign Out", self.app.show_login, 
            text_color="#EF4444", hover_color="#FEF2F2"
        )

    def create_notif_menu_frame(self):
        self.notif_menu = ctk.CTkFrame(self.main_area, width=300, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        
        # Header
        header = ctk.CTkFrame(self.notif_menu, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(header, text="NOTIFICATIONS", font=("Arial", 11, "bold"), text_color="#9CA3AF").pack(side="left")
        
        ctk.CTkButton(
            header, text="View All", fg_color="transparent", text_color=self.COLOR_PRIMARY, 
            font=("Arial", 11, "bold"), width=60, height=20, hover=False,
            command=lambda: [self.toggle_notif_menu(), self.show_notifications()]
        ).pack(side="right")
        
        ctk.CTkFrame(self.notif_menu, height=1, fg_color="#F3F4F6").pack(fill="x", pady=5)
        
        # List Container
        self.notif_list_frame = ctk.CTkFrame(self.notif_menu, fg_color="transparent")
        self.notif_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def update_notif_menu(self):
        """Updates the content of the notification popup from loaded data"""
        for w in self.notif_list_frame.winfo_children(): w.destroy()
        
        if not self.announcements:
            ctk.CTkLabel(self.notif_list_frame, text="No new notifications", font=("Arial", 12), text_color="gray").pack(pady=20)
            return

        # Display up to 3 latest announcements
        for ann in self.announcements[:3]:
            btn = ctk.CTkButton(
                self.notif_list_frame, 
                text=getattr(ann, 'title', 'No Title'),
                fg_color="white", hover_color="#F3F4F6", text_color="#333", anchor="w",
                font=("Arial", 12), height=35,
                command=lambda: [self.toggle_notif_menu(), self.show_notifications()]
            )
            btn.pack(fill="x", pady=1, padx=5)

    def toggle_user_menu(self, event=None):
        """Shows/Hides the user menu at the correct position"""
        if self.user_menu.winfo_ismapped():
            self.user_menu.place_forget()
        else:
            # Close notification menu if open
            if hasattr(self, 'notif_menu') and self.notif_menu.winfo_ismapped(): 
                self.notif_menu.place_forget()
            # Set position: Directly below the User name button, right-aligned
            self.user_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-30, y=65)
            self.user_menu.lift()

    def toggle_notif_menu(self):
        if self.notif_menu.winfo_ismapped():
            self.notif_menu.place_forget()
        else:
            if self.user_menu.winfo_ismapped(): self.user_menu.place_forget()
            self.notif_menu.place(relx=1.0, rely=0.0, anchor="ne", x=-160, y=65)
            self.notif_menu.lift()

    def _menu_btn(self, parent, text, command, text_color="#374151", hover_color="#F3F4F6"):
        """Helper to create a cleaner button in the menu"""
        btn = ctk.CTkButton(
            parent, 
            text=text, 
            fg_color="transparent", 
            text_color=text_color, 
            hover_color=hover_color, 
            anchor="w", 
            height=40, 
            font=("Arial", 13), # Close menu after click
            command=lambda: [self.toggle_user_menu(), command()]
        )
        btn.pack(fill="x", padx=5, pady=2)

    def open_change_password_popup(self):
        if self.user_menu.winfo_ismapped(): self.user_menu.place_forget()
        
        root = self.winfo_toplevel()
        popup = ctk.CTkToplevel(root)
        popup.title("Change Password")
        popup.geometry("400x480")
        popup.resizable(False, False)
        popup.configure(fg_color="white")
        
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

    def _create_popup_input(self, parent, label): # Helper for popup
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
            
        # Run password change in background
        def _change_pw():
            return self.auth_controller.change_password(self.user.user_id, curr, new_p)
            
        def _on_done(result):
            if not popup.winfo_exists(): return
            success, msg = result
            if success: messagebox.showinfo("Success", msg, parent=popup); popup.destroy()
            else: messagebox.showerror("Error", msg, parent=popup)
            
        run_in_background(_change_pw, _on_done, tk_root=self.winfo_toplevel())

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(10, weight=1)

        # Branding section
        logo_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=20, pady=30, sticky="ew")
        # Logo text
        ctk.CTkLabel(logo_box, text="STUDENT PORTAL", font=("Arial", 16, "bold"), text_color=self.COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(logo_box, text="Academic System", font=("Arial", 10, "bold"), text_color=self.COLOR_TEXT_SUB).pack(anchor="w")

        # Menu Text Only
        ctk.CTkLabel(sidebar, text="MAIN MENU", font=("Arial", 11, "bold"), text_color="#9CA3AF").grid(row=1, column=0, sticky="w", padx=30, pady=(20, 10))

        self._sidebar_btn(sidebar, 2, "Dashboard", "home", self.refresh_home)
        self._sidebar_btn(sidebar, 3, "My Schedule", "schedule", self.show_schedule)
        self._sidebar_btn(sidebar, 4, "Academic Results", "grades", self.show_grades)
        self._sidebar_btn(sidebar, 5, "My Profile", "profile", self.show_profile)

        # Footer with user info
        footer = ctk.CTkFrame(sidebar, fg_color="#F0FDFA", corner_radius=0, height=60)
        footer.grid(row=11, column=0, padx=0, pady=0, sticky="ew")
        
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

    def clear_content(self):
        if hasattr(self, 'user_menu') and self.user_menu.winfo_ismapped(): self.user_menu.place_forget()
        if hasattr(self, 'notif_menu') and self.notif_menu.winfo_ismapped(): self.notif_menu.place_forget()
        for widget in self.content_scroll.winfo_children(): widget.destroy()

    def refresh_home(self):
        """Refreshes data and shows home view to ensure 'Upcoming Class' status is up-to-date"""
        self.show_home()
        self.load_real_data()

    def show_home(self):
        self.clear_content()
        self.set_active_nav("home")
        self.active_view = "home"
        self.page_title.configure(text="Dashboard Overview")
        self.content_scroll.grid_columnconfigure(0, weight=2)
        self.content_scroll.grid_columnconfigure(1, weight=1)

        left_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nswe", padx=(0, 20))
        
        self.create_next_class_card(left_col)
        self.create_stats_row(left_col)
        self.create_recent_grades(left_col)

        right_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nswe")
        
        self.create_announcements_list(right_col)
        self.create_quick_links(right_col)

    def create_next_class_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#0F766E", corner_radius=10)
        card.pack(fill="x", pady=(0, 20))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=20)
        
        if self.next_class:
            # Dynamic Header based on status (Happening Now vs Upcoming)
            status_txt = self.next_class.get('ui_status', 'UPCOMING CLASS')
            status_col = self.next_class.get('ui_color', '#CCFBF1')
            ctk.CTkLabel(inner, text=status_txt, font=("Arial", 11, "bold"), text_color=status_col).pack(anchor="w")

            c_name = self.next_class.get('course_name', 'Unknown')
            c_room = self.next_class.get('room', 'TBA')
            c_time = self.next_class.get('schedule', 'TBA')
            
            ctk.CTkLabel(inner, text=c_name, font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", pady=(5, 0))
            ctk.CTkLabel(inner, text=f"Room: {c_room}  |  Time: {c_time}", font=("Arial", 13), text_color="#99F6E4").pack(anchor="w", pady=(5, 0))
        else:
            ctk.CTkLabel(inner, text="UPCOMING CLASS", font=("Arial", 10, "bold"), text_color="#CCFBF1").pack(anchor="w")
            ctk.CTkLabel(inner, text="No classes scheduled for today.", font=("Arial", 18, "bold"), text_color="white").pack(anchor="w", pady=(10, 0))
            ctk.CTkLabel(inner, text="Enjoy your free time!", font=("Arial", 12), text_color="#99F6E4").pack(anchor="w")

    def create_stats_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))
        
        gpa = f"{self.stats.get('gpa', 0.0):.2f}"
        credits = str(self.stats.get('credits', 0))
        
        self._stat_box(row, "GPA Score", gpa, "left")
        self._stat_box(row, "Credits Earned", credits, "left")
        self._stat_box(row, "Status", "Active", "right")

    def _stat_box(self, parent, title, value, side):
        box = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        box.pack(side=side, fill="x", expand=True, padx=5)
        
        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(inner, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(inner, text=value, font=("Arial", 20, "bold"), text_color="#333").pack(anchor="w")

    def create_recent_grades(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x")
        
        ctk.CTkLabel(card, text="Recent Performance", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        
        if not self.recent_grades:
            ctk.CTkLabel(card, text="No grade records yet.", text_color="gray").pack(padx=20, pady=10)
        else:
            for g in self.recent_grades:
                course_name = getattr(g, 'course_name', 'Unknown')
                total = getattr(g, 'total', None)
                self._grade_row(card, course_name, total)

    def _grade_row(self, parent, name, score):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row, text=name, font=("Arial", 12), text_color="#333").pack(side="left")
        
        # Safely handle score (avoid float(None) errors)
        if score is None:
            col, display_score = "gray", "-"
        else:
            try:
                val = float(score)
                display_score = str(score)
                if val >= 8.5: col = "#16A34A"   # Green (Excellent)
                elif val >= 4.0: col = "#333333" # Black (Passed)
                else: col = "#DC2626"            # Red (Failed)
            except (ValueError, TypeError):
                col, display_score = "#333", str(score)

        ctk.CTkLabel(row, text=display_score, font=("Arial", 12, "bold"), text_color=col).pack(side="right")
        
        ctk.CTkFrame(parent, height=1, fg_color="#F3F4F6").pack(fill="x", padx=20, pady=5)

    def create_announcements_list(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(card, text="Announcements", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        
        if not self.announcements:
            ctk.CTkLabel(card, text="No new announcements.", text_color="gray").pack(padx=20, pady=10)
        else:
            for ann in self.announcements:
                title = getattr(ann, 'title', '')
                content = getattr(ann, 'content', '')
                self._ann_row(card, title, content[:50] + "...")

    def _ann_row(self, parent, title, snippet):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(row, text=title, font=("Arial", 12, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(row, text=snippet, font=("Arial", 11), text_color="gray").pack(anchor="w")
        
        ctk.CTkFrame(parent, height=1, fg_color="#F3F4F6").pack(fill="x", padx=20, pady=(8,0))

    def create_quick_links(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x")
        ctk.CTkLabel(card, text="Quick Links", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=20, pady=15)
        
        self._link_btn(card, "View Schedule", lambda: [self.set_active_nav("schedule"), self.show_schedule()])
        self._link_btn(card, "Check Grades", lambda: [self.set_active_nav("grades"), self.show_grades()])

    def _link_btn(self, parent, txt, cmd):
        ctk.CTkButton(
            parent, text=txt, fg_color="white", text_color="#333", 
            hover_color="#F3F4F6", anchor="w", height=40,
            border_width=1, border_color="#E5E7EB", 
            font=("Arial", 12), command=cmd
        ).pack(fill="x", padx=20, pady=5)

    def show_profile(self):
        self.clear_content()
        self.set_active_nav("profile")
        self.active_view = "profile"
        self.page_title.configure(text="My Profile")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ProfileView(self.content_scroll, self.user, self.controller).pack(fill="both", expand=True)

    def show_schedule(self):
        self.clear_content()
        self.set_active_nav("schedule")
        self.active_view = "schedule"
        self.page_title.configure(text="My Schedule")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ScheduleFrame(self.content_scroll, self.controller).pack(fill="both", expand=True)

    def show_grades(self):
        self.clear_content()
        self.set_active_nav("grades")
        self.active_view = "grades"
        self.page_title.configure(text="Academic Results")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        GradesFrame(self.content_scroll, self.controller).pack(fill="both", expand=True)

    def show_notifications(self):
        self.clear_content()
        self.set_active_nav("none")
        self.active_view = "notifications"
        self.page_title.configure(text="Notifications")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        
        NotificationsView(self.content_scroll, self.controller).pack(fill="both", expand=True)