import customtkinter as ctk
from controllers.student_controller import StudentController
from datetime import datetime
from utils.threading_helper import run_in_background

class NotificationsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # parent is the content_scroll of the Dashboard
        super().__init__(parent, fg_color="transparent")
        
        self.controller = controller

        # --- HEADER ---
        self.create_header()

        # --- LIST CONTAINER ---
        # Use a regular Frame because the parent is already scrollable
        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True)

        # --- LOAD DATA ---
        self.load_data_async()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        
        # Title
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Notifications Center", font=("Arial", 24, "bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Latest updates from the university administration.", font=("Arial", 14), text_color="#6B7280").pack(anchor="w")

        # Refresh Button (Text only)
        ctk.CTkButton(
            header_frame, text="Refresh List", 
            fg_color="white", text_color="#0F766E", 
            hover_color="#F0FDFA", border_width=1, border_color="#CCFBF1",
            font=("Arial", 12, "bold"), width=100, height=35,
            command=self.load_data_async
        ).pack(side="right", anchor="c")

    def load_data_async(self):
        # Clear old widgets
        for w in self.list_container.winfo_children():
            w.destroy()
        
        # Show Loading
        self.loading_lbl = ctk.CTkLabel(self.list_container, text="Checking for updates...", text_color="gray")
        self.loading_lbl.pack(pady=20)

        run_in_background(
            self._fetch_notifications,
            self._render_notifications,
            tk_root=self.winfo_toplevel()
        )

    def _fetch_notifications(self):
        try:
            if self.controller and hasattr(self.controller, 'get_latest_announcements'):
                return self.controller.get_latest_announcements(limit=20)
            else:
                return []
        except Exception as e:
            print(f"Error loading notifications: {e}")
            return None

    def _render_notifications(self, notifications):
        if not self.winfo_exists(): return
        if hasattr(self, 'loading_lbl'): self.loading_lbl.destroy()
        
        if notifications is None:
             ctk.CTkLabel(self.list_container, text="Could not load notifications.", text_color="#EF4444").pack(pady=20)
             return

        if not notifications:
            self.show_empty_state()
        else:
            for notif in notifications:
                self.create_card(notif)

    def show_empty_state(self):
        frame = ctk.CTkFrame(self.list_container, fg_color="white", corner_radius=10)
        frame.pack(fill="x", pady=10, ipady=30)
        ctk.CTkLabel(frame, text="You're all caught up!", font=("Arial", 13), text_color="gray").pack()

    def create_card(self, data):
        """
        data is the Announcement object returned from the DB
        """
        # Card Container
        card = ctk.CTkFrame(self.list_container, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.pack(fill="x", pady=(0, 15))

        # 1. Color Strip (Left color bar instead of an icon)
        # Dark Teal color creates a brand accent
        strip = ctk.CTkFrame(card, width=6, fg_color="#0F766E", corner_radius=0)
        strip.pack(side="left", fill="y")
        
        # 2. Content Area
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # Row 1: Badge + Date
        meta_row = ctk.CTkFrame(content, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 5))
        
        # Badge "SYSTEM" or "ANNOUNCEMENT"
        badge = ctk.CTkLabel(
            meta_row, text="ANNOUNCEMENT", 
            font=("Arial", 10, "bold"), text_color="#0F766E", 
            fg_color="#F0FDFA", corner_radius=6
        )
        badge.pack(side="left", ipadx=8, ipady=2)
        
        # Date (Formatted nicely)
        raw_date = getattr(data, 'created_date', '')
        if isinstance(raw_date, str):
            display_date = raw_date
        else:
            display_date = raw_date.strftime("%d %b %Y, %H:%M")
        ctk.CTkLabel(meta_row, text=display_date, font=("Arial", 11), text_color="#9CA3AF").pack(side="right") # Example: 25 Oct 2024, 14:30

        # Row 2: Title
        ctk.CTkLabel(
            content, text=getattr(data, 'title', 'No Title'), 
            font=("Arial", 16, "bold"), text_color="#111827"
        ).pack(anchor="w", pady=(0, 5))

        # Row 3: Summary/Content
        full_text = getattr(data, 'content', '')
        # Truncate if too long for preview (optional)
        # display_text = full_text[:300] + "..." if len(full_text) > 300 else full_text
        
        ctk.CTkLabel(
            content, text=full_text, 
            font=("Arial", 13), text_color="#4B5563", 
            wraplength=650, justify="left"
        ).pack(anchor="w")