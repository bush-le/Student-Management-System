import customtkinter as ctk

class NotificationsView(ctk.CTkFrame):
    def __init__(self, parent):
        # parent chính là self.content_scroll của Dashboard
        super().__init__(parent, fg_color="transparent")
        
        # 1. Header lớn
        # Dùng một Frame bao bọc header để dễ căn chỉnh khoảng cách
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Notifications", font=("Arial", 24, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(header_frame, text="Stay updated with academic announcements and system alerts.", font=("Arial", 14), text_color="gray").pack(anchor="w")

        # 2. Danh sách chứa các card (FIX QUAN TRỌNG Ở ĐÂY)
        # Thay vì dùng CTkScrollableFrame, ta dùng CTkFrame thường.
        # Lý do: Parent của view này ở Dashboard đã là ScrollableFrame rồi.
        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        # expand=True và fill="both" giúp nó chiếm toàn bộ diện tích còn lại
        self.list_container.pack(fill="both", expand=True)

        # 3. Dữ liệu mẫu (Nhiều hơn để test scroll)
        notifications = [
            {"title": "Midterm Grades Published", "summary": "Fall 2024 midterm grades have been updated. Please check the Grades section to view your detailed results.", "timestamp": "Oct 25, 2024"},
            {"title": "Course Registration Deadline", "summary": "Reminder: The deadline for course registration is this Friday. Ensure you have selected all required electives.", "timestamp": "Aug 20, 2024"},
            {"title": "Tuition Payment Notice", "summary": "The system has updated your tuition invoices for the next semester. Please pay by Feb 15th to avoid late fees.", "timestamp": "Dec 15, 2024"},
            {"title": "Library Holiday Hours", "summary": "The university library will have adjusted hours during the upcoming holiday break. Check the website for details.", "timestamp": "Dec 10, 2024"},
            {"title": "System Maintenance", "summary": "SMS Portal will undergo scheduled maintenance this Sunday from 2 AM to 4 AM. Services will be unavailable.", "timestamp": "Dec 01, 2024"}
        ]

        for notif in notifications:
            self.create_card(notif)

    def create_card(self, data):
        """Vẽ thẻ thông báo lớn"""
        # Pack vào self.list_container
        card = ctk.CTkFrame(self.list_container, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        card.pack(fill="x", pady=(0, 15), ipady=5) # pady giữa các card

        # Icon tròn giả lập (Màu xanh nhạt)
        icon_box = ctk.CTkFrame(card, width=50, height=50, corner_radius=25, fg_color="#EFF6FF")
        icon_box.pack(side="left", padx=20, anchor="n", pady=15)
        # Kí tự loa
        ctk.CTkLabel(icon_box, text="📢", font=("Arial", 20)).place(relx=0.5, rely=0.5, anchor="center")

        # Nội dung bên phải
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=15, padx=(0, 20))
        
        # Title
        ctk.CTkLabel(content, text=data['title'], font=("Arial", 16, "bold"), text_color="#1F2937").pack(anchor="w")
        
        # Summary (wraplength lớn để tự xuống dòng trên màn hình rộng)
        ctk.CTkLabel(content, text=data['summary'], font=("Arial", 14), text_color="#4B5563", wraplength=600, justify="left").pack(anchor="w", pady=(5, 10))
        
        # Timestamp
        ctk.CTkLabel(content, text=data['timestamp'], font=("Arial", 12, "bold"), text_color="#9CA3AF").pack(anchor="w")