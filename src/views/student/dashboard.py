import customtkinter as ctk
from datetime import datetime
from controllers.student_controller import StudentController
from views.student.schedule import ScheduleFrame
from views.student.grades import GradesFrame
import traceback

class StudentDashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#F5F7F9") # Light gray background
        self.app = app
        self.user = user
        
        # --- Wrap in Try-Catch to catch silent errors ---
        try:
            self.controller = StudentController(user.user_id)
            self.student_profile = self.controller.view_profile()
            self.grades_data = self.controller.view_grades()

            # --- MAIN GRID CONFIG (Sidebar vs Main Content) ---
            # Column 0: Sidebar (Fixed, no expand) -> weight=0
            # Column 1: Main Content (Expands fully) -> weight=1
            self.grid_columnconfigure(1, weight=1) 
            self.grid_rowconfigure(0, weight=1)

            # ================== 1. SIDEBAR (LEFT) ==================
            self.create_sidebar()

            # ================== 2. MAIN AREA (RIGHT) ==================
            self.main_area = ctk.CTkFrame(self, fg_color="#F5F7F9", corner_radius=0)
            self.main_area.grid(row=0, column=1, sticky="nswe")
            
            self.main_area.grid_rowconfigure(1, weight=1) # Row 1 (Content) expands
            self.main_area.grid_columnconfigure(0, weight=1)

            # 2.1 Header
            self.create_header()

            # 2.2 Scrollable Content
            self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
            self.content_scroll.grid(row=1, column=0, sticky="nswe", padx=20, pady=10)

            # Render Dashboard Home content
            self.show_home()

        except Exception as e:
            print("❌ ERROR INITIALIZING DASHBOARD:")
            traceback.print_exc()
            # Display error on screen for easier debugging
            ctk.CTkLabel(self, text=f"Error loading dashboard: {e}", text_color="red").pack(pady=50)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="white")
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(5, weight=1) # Push Logout button to the bottom

        # Logo
        ctk.CTkLabel(self.sidebar, text="🎓 SMS Portal", font=("Arial", 22, "bold"), text_color="#2A9D8F").grid(row=0, column=0, pady=30, padx=20)

        # Menu Buttons
        self.nav_buttons = {}
        self.create_nav_btn("Dashboard", 1, self.show_home, "🏠")
        self.create_nav_btn("My Schedule", 2, self.show_schedule, "📅")
        self.create_nav_btn("Academic Results", 3, self.show_grades, "📊")
        self.create_nav_btn("Profile", 4, self.show_profile, "👤")

        # Logout
        ctk.CTkButton(
            self.sidebar, text="🚪 Sign Out", fg_color="transparent", 
            text_color="#E76F51", hover_color="#FEF2F2", anchor="w", 
            font=("Arial", 14), height=50, command=self.app.show_login
        ).grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    def create_nav_btn(self, text, row, cmd, icon):
        btn = ctk.CTkButton(
            self.sidebar, text=f"  {icon}   {text}", fg_color="transparent", text_color="#555", 
            hover_color="#E0F2F1", anchor="w", font=("Arial", 14, "normal"), 
            height=50, command=cmd
        )
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        self.nav_buttons[text] = btn

    def update_nav_state(self, active_button_name):
        """Updates the visual state of the navigation buttons."""
        for name, btn in self.nav_buttons.items():
            is_active = (name == active_button_name)
            color = "#E0F2F1" if is_active else "transparent"
            text_col = "#2A9D8F" if is_active else "#555"
            font_weight = "bold" if is_active else "normal"
            btn.configure(fg_color=color, text_color=text_col, font=("Arial", 14, font_weight))

    def create_header(self):
        header = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        date_str = datetime.now().strftime("%A, %B %d").upper()
        
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text=date_str, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        
        wel = ctk.CTkFrame(info, fg_color="transparent")
        wel.pack(anchor="w")
        ctk.CTkLabel(wel, text="Welcome back, ", font=("Arial", 24), text_color="#333").pack(side="left")
        ctk.CTkLabel(wel, text=self.user.full_name, font=("Arial", 24, "bold"), text_color="#2A9D8F").pack(side="left")

        ctk.CTkButton(header, text="View Full Schedule →", fg_color="transparent", text_color="#2A9D8F", 
                      font=("Arial", 13, "bold"), command=self.show_schedule).pack(side="right", anchor="s")

    def show_home(self):
        self.update_nav_state("Dashboard")
        self.clear_content()
        
        # --- Configure grid for Home view (2 columns) ---
        self.content_scroll.grid_columnconfigure(0, weight=2)
        self.content_scroll.grid_columnconfigure(1, weight=1)

        # --- LEFT COLUMN (Hero + Stats) ---
        left_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nswe", padx=(0, 20))
        
        self.create_hero_card(left_col)
        self.create_stats_row(left_col)
        self.create_recent_performance(left_col)

        # --- RIGHT COLUMN (Notif + Links) ---
        right_col = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nswe")
        
        self.create_notifications_panel(right_col)
        self.create_quick_links(right_col)

    # --- UI Drawing Helper Functions ---
    def create_hero_card(self, parent):
        # NOTE: This is a static demonstration card. Real logic to find the "next" class is complex.
        card = ctk.CTkFrame(parent, fg_color="#2A9D8F", corner_radius=15)
        card.pack(fill="x", pady=(0, 20))
        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20, 10))
        ctk.CTkLabel(top, text="NEXT CLASS", font=("Arial", 10, "bold"), text_color="white", fg_color="rgba(255,255,255,0.2)", corner_radius=5).pack(side="left")
        ctk.CTkLabel(top, text="🕒", font=("Arial", 20)).pack(side="right")

        ctk.CTkLabel(card, text="Data Structures & Algorithms", font=("Arial", 24, "bold"), text_color="white").pack(anchor="w", padx=25)
        ctk.CTkLabel(card, text="CS201", font=("Arial", 14), text_color="#E0F2F1").pack(anchor="w", padx=25, pady=(0, 20))

        bot = ctk.CTkFrame(card, fg_color="rgba(255,255,255,0.1)", corner_radius=10)
        bot.pack(fill="x", padx=25, pady=(0, 25))
        
        self._hero_item(bot, "TIME", "13:00 - 14:30", "left")
        self._hero_item(bot, "LOCATION", "Room B203", "left")

    def _hero_item(self, parent, title, val, side):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side=side, padx=20, pady=10, expand=True, fill="x")
        ctk.CTkLabel(f, text=title, font=("Arial", 9, "bold"), text_color="#B2DFDB").pack(anchor="w")
        ctk.CTkLabel(f, text=val, font=("Arial", 13, "bold"), text_color="white").pack(anchor="w")

    def create_stats_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))

        gpa = self.student_profile.gpa if self.student_profile else "N/A"
        semester = self.student_profile.academic_year if self.student_profile else "N/A"
        total_credits = sum(g['credits'] for g in self.grades_data) if self.grades_data else 0

        self._stat_card(row, "📊", "GPA", str(gpa), "#2563EB")
        self._stat_card(row, "📖", "CREDITS", str(total_credits), "#9333EA")
        self._stat_card(row, "📅", "SEMESTER", str(semester), "#16A34A")

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
        
        # Dynamic Rows
        if self.grades_data:
            # Show the first 2 grades. NOTE: The controller query doesn't order by date.
            for grade in self.grades_data[:2]:
                self._perf_row(card, grade['course_name'], "Final", grade['total'], "#16A34A")
        else:
            ctk.CTkLabel(card, text="No recent performance data available.").pack(pady=10)

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

    # --- Navigation ---
    def clear_content(self):
        for widget in self.content_scroll.winfo_children():
            widget.destroy()

    def show_schedule(self):
        self.update_nav_state("My Schedule")
        self.clear_content()
        # Reset grid to 1 column for this view
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        ScheduleFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_grades(self):
        self.update_nav_state("Academic Results")
        self.clear_content()
        # Reset grid to 1 column for this view
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=0)
        GradesFrame(self.content_scroll, self.user.user_id).pack(fill="both", expand=True)

    def show_profile(self):
        self.update_nav_state("Profile")
        self.clear_content()
        # Placeholder for profile view
        ctk.CTkLabel(self.content_scroll, text="Profile Management Page - Under Construction", font=("Arial", 18)).pack(pady=20)