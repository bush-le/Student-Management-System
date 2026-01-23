import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
import traceback

from controllers.lecturer_controller import LecturerController
from controllers.auth_controller import AuthController
from utils.threading_helper import run_in_background

# Import child Views (ProfileView removed)
from views.lecturer.schedule import LecturerScheduleFrame
from views.lecturer.my_class import LecturerClassesFrame
from views.lecturer.class_manager import LecturerClassManager

class LecturerDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F3F4F6") # Light gray background
        self.app = app
        self.user = user
        self.auth_controller = AuthController()
        
        # --- COLOR PALETTE ---
        self.COLOR_PRIMARY = "#0F766E"      # Dark Teal
        self.COLOR_ACCENT = "#14B8A6"       # Light Teal
        self.COLOR_SIDEBAR = "#FFFFFF"      # White
        self.COLOR_TEXT_MAIN = "#111827"    # Black
        self.COLOR_TEXT_SUB = "#6B7280"     # Gray
        
        self.nav_buttons = {}
        self.user_menu_open = False
        self.active_view = "home" # Track current active view
        
        try:
            self.controller = LecturerController(user.user_id)
            
            # Initialize default data
            self.next_class = None
            self.stats = {}
            # --- LOAD REAL DATA (Async) ---
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
            print("❌ LECTURER DASHBOARD INITIALIZATION ERROR:")
            traceback.print_exc()

    def load_dashboard_data(self):
        """Fetch data from DB via Controller"""
        run_in_background(
            self._fetch_data,
            self._on_data_loaded,
            tk_root=self.winfo_toplevel()
        )

    def _fetch_data(self):
        try:
            # OPTIMIZATION: Use combined method to reduce DB calls
            upcoming, stats = self.controller.get_dashboard_summary()
            return {
                'next_class': upcoming,
                'stats': stats
            }
        except Exception as e:
            return None

    def _on_data_loaded(self, data):
        if not self.winfo_exists(): return
        if data:
            self.next_class = data.get('next_class')
            self.stats = data.get('stats', {})
            # Refresh Home UI if currently displayed
            if self.active_view == "home":
                self.show_home()

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

        self._sidebar_btn(sidebar, 2, "Dashboard", "home", self.refresh_home)
        self._sidebar_btn(sidebar, 3, "Teaching Schedule", "schedule", self.show_schedule)
        self._sidebar_btn(sidebar, 4, "Manage Classes", "classes", self.show_my_classes)
        # Profile button removed here

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
    def refresh_home(self):
        """Refreshes data and shows home view"""
        self.show_home()
        self.load_dashboard_data()

    def show_home(self):
        self.show_home_view()

    def show_home_view(self):
        self.clear_content()
        self.set_active_nav("home")
        self.active_view = "home"
        self.page_title.configure(text="Lecturer Dashboard")
        
        # Balanced 1:1 Layout
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
        
        if self.next_class:
            status_txt = self.next_class.get('ui_status', 'NEXT TEACHING SESSION')
            status_col = self.next_class.get('ui_color', '#CCFBF1')
            ctk.CTkLabel(inner, text=status_txt, font=("Arial", 10, "bold"), text_color=status_col).pack(anchor="w")

            c_name = self.next_class.get('course_name', 'Unknown')
            c_room = self.next_class.get('room', 'TBA')
            c_time = self.next_class.get('schedule', 'TBA')
            
            ctk.CTkLabel(inner, text=c_name, font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", pady=(5, 0))
            ctk.CTkLabel(inner, text=f"Room: {c_room}  |  Time: {c_time}", font=("Arial", 13), text_color="#99F6E4").pack(anchor="w", pady=(5, 0))
        else:
            ctk.CTkLabel(inner, text="NEXT TEACHING SESSION", font=("Arial", 10, "bold"), text_color="#CCFBF1").pack(anchor="w")
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
        
        # Update Profile button removed
        self._action_btn(inner, "Grade Assignments", lambda: [self.set_active_nav("classes"), self.show_my_classes()])
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
        # My Profile button removed
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
        
        ctk.CTkLabel(bg, text="Change Password", font=("Arial", 22, "bold"), text_color="#111827").pack(pady=(30, 20))
        
        popup.curr = self._create_popup_input(bg, "Current Password")
        popup.new = self._create_popup_input(bg, "New Password")
        popup.conf = self._create_popup_input(bg, "Confirm New Password")
        
        ctk.CTkButton(bg, text="Update Password", fg_color=self.COLOR_PRIMARY, height=45, font=("Arial", 14, "bold"), 
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

    # =========================================================================
    # 5. NAVIGATION
    # =========================================================================
    def clear_content(self):
        if self.user_menu.winfo_ismapped(): self.user_menu.place_forget()
        for w in self.content_scroll.winfo_children(): w.destroy()

    def show_schedule(self):
        self.clear_content()
        self.set_active_nav("schedule")
        self.active_view = "schedule"
        self.page_title.configure(text="Teaching Schedule")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        LecturerScheduleFrame(self.content_scroll, self.controller).pack(fill="both", expand=True)

    def show_my_classes(self):
        """Display class list (View 1)"""
        self.clear_content()
        self.set_active_nav("classes")
        self.active_view = "classes"
        self.page_title.configure(text="Class Management")
        
        # Grid configuration
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        
        # Pass self (dashboard) so child Frame can call back
        LecturerClassesFrame(self.content_scroll, self, self.controller).pack(fill="both", expand=True)

    def open_class_manager(self, class_data):
        """Display detailed class management interface (View 2). This function is called from LecturerClassesFrame."""
        self.clear_content()
        self.active_view = "class_manager"
        # Reset Grid for full-screen management view
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        # Initialize Class Manager
        # on_back_callback=self.show_my_classes: So the Back button returns to the class list
        LecturerClassManager(self.content_scroll, self.controller, class_data, on_back_callback=self.show_my_classes).pack(fill="both", expand=True)