import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class AnnouncementsFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent") # Nền trong suốt để hòa vào Dashboard
        self.controller = AdminController(user_id)
        self.user_id = user_id 
        
        # --- COLORS (Đồng bộ với Dashboard) ---
        self.COLOR_PRIMARY = "#0F766E"  # Teal đậm
        self.COLOR_HOVER = "#115E59"
        self.COLOR_EDIT = "#3B82F6"     # Blue
        self.COLOR_DELETE = "#EF4444"   # Red

        # 1. Header
        self.create_header()

        # 2. List Container
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.scroll_area.pack(fill="both", expand=True, pady=(0, 20))

        # 3. Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=0, pady=(0, 15))
        
        # Title
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="ANNOUNCEMENTS", font=("Arial", 20, "bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Manage system-wide notifications", font=("Arial", 12), text_color="gray").pack(anchor="w")
        
        # Add Button
        ctk.CTkButton(
            header, text="+ New Announcement", 
            fg_color=self.COLOR_PRIMARY, hover_color=self.COLOR_HOVER, 
            width=160, height=40, font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        ).pack(side="right")

    def load_data(self):
        for w in self.scroll_area.winfo_children(): w.destroy()
        
        data = self.controller.get_all_announcements()
        
        if not data:
            f = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
            f.pack(pady=40)
            ctk.CTkLabel(f, text="No announcements yet.", font=("Arial", 14), text_color="gray").pack()
            return

        for item in data:
            self.create_card(item)

    def create_card(self, data):
        # Card Container
        card = ctk.CTkFrame(self.scroll_area, fg_color="#F9FAFB", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.pack(fill="x", pady=8, padx=10, ipady=5)

        # Row 1: Title + Date + Actions
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(15, 5))
        
        # Title
        ctk.CTkLabel(header_row, text=data.title, font=("Arial", 14, "bold"), text_color="#111827").pack(side="left")

        # Actions (Right aligned)
        actions = ctk.CTkFrame(header_row, fg_color="transparent")
        actions.pack(side="right")
        
        # Date Badge
        date_str = str(data.created_date).split()[0] # Lấy YYYY-MM-DD
        ctk.CTkLabel(actions, text=f"📅 {date_str}", font=("Arial", 11), text_color="gray").pack(side="left", padx=(0, 15))

        # Edit/Delete Buttons (Text only)
        self._action_btn(actions, "Edit", self.COLOR_EDIT, lambda: self.open_edit_dialog(data))
        ctk.CTkLabel(actions, text="|", text_color="#E5E7EB").pack(side="left", padx=5) # Separator
        self._action_btn(actions, "Delete", self.COLOR_DELETE, lambda: self.delete_item(data.announcement_id))

        # Row 2: Content (Separator line)
        ctk.CTkFrame(card, height=1, fg_color="#E5E7EB").pack(fill="x", padx=20, pady=5)

        # Content Text
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        # Cắt ngắn nội dung nếu quá dài
        display_text = data.content
        if len(display_text) > 200:
            display_text = display_text[:200] + "..."
            
        ctk.CTkLabel(
            content_frame, text=display_text, 
            font=("Arial", 12), text_color="#4B5563", 
            anchor="w", justify="left", wraplength=800
        ).pack(fill="x")

    def _action_btn(self, parent, text, color, cmd):
        ctk.CTkButton(
            parent, text=text, width=50, height=24, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left")

    def delete_item(self, ann_id):
        if messagebox.askyesno("Confirm", "Delete this announcement?"):
            success, msg = self.controller.delete_announcement(ann_id)
            if success: self.load_data()
            else: messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        AnnouncementDialog(self, "New Announcement", self.controller, self.load_data, user_id=self.user_id)

    def open_edit_dialog(self, data):
        AnnouncementDialog(self, "Edit Announcement", self.controller, self.load_data, data=data, user_id=self.user_id)


# ==========================================
# POPUP FORM (Improved Layout)
# ==========================================
class AnnouncementDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None, user_id=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.user_id = user_id
        
        self.title(title)
        self.geometry("600x480")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        # Title Header
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=(25, 20), anchor="w", padx=40)

        # Form Container
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)

        # 1. Subject / Title
        ctk.CTkLabel(form, text="Subject / Title", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(5, 5))
        self.ent_title = ctk.CTkEntry(form, placeholder_text="e.g. Final Exam Schedule", height=40, border_color="#E5E7EB")
        self.ent_title.pack(fill="x")

        # 2. Content
        ctk.CTkLabel(form, text="Content Details", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(20, 5))
        self.txt_content = ctk.CTkTextbox(form, height=150, border_width=1, border_color="#E5E7EB", fg_color="white", text_color="black")
        self.txt_content.pack(fill="x")

        # 3. Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=30, side="bottom")

        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
            text_color="black", hover_color="#F3F4F6", width=100, height=40,
            command=self.destroy
        ).pack(side="left")
        
        btn_text = "Save Changes" if data else "Post Now"
        ctk.CTkButton(
            btn_frame, text=btn_text, fg_color="#0F766E", hover_color="#115E59", 
            width=140, height=40, font=("Arial", 13, "bold"),
            command=self.save
        ).pack(side="right")

        # Fill Data
        if data:
            self.ent_title.insert(0, data.title)
            self.txt_content.insert("0.0", data.content)

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def save(self):
        title = self.ent_title.get()
        content = self.txt_content.get("0.0", "end").strip()

        if not title or not content:
            messagebox.showwarning("Required", "Please fill in Title and Content", parent=self)
            return

        if self.data: # Update
            success, msg = self.controller.update_announcement(self.data.announcement_id, title, content)
        else: # Create
            success, msg = self.controller.create_announcement(title, content, self.user_id)

        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)