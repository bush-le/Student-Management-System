import resend
from config import Config

class EmailService:
    """
    Class handling email sending via Resend API.
    """

    @staticmethod
    def send_recovery_email(to_email, reset_code):
        """
        FR-04: Send password recovery code.
        """
        if not Config.RESEND_API_KEY:
            print("⚠️ Error: RESEND_API_KEY is missing.")
            return False

        resend.api_key = Config.RESEND_API_KEY

        # Nội dung HTML (Giữ nguyên như bạn đã viết, rất đẹp rồi)
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px;">
            <h2 style="color: #2c3e50; text-align: center;">Password Recovery Request</h2>
            <p>Hello,</p>
            <p>You recently requested to reset your password for the <strong>Student Management System</strong>.</p>
            <div style="background-color: #f4f4f4; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <h1 style="color: #27ae60; margin: 0; letter-spacing: 5px; font-size: 32px;">{reset_code}</h1>
            </div>
            <p>This code is valid for <strong>15 minutes</strong>.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin-top: 20px;" />
            <p style="font-size: 12px; color: #95a5a6; text-align: center;">Group 01 - UTH</p>
        </div>
        """

        # Lưu ý: Nếu chưa add domain vào Resend, "from" bắt buộc là onboarding@resend.dev
        # Và "to" bắt buộc là email bạn dùng đăng ký tài khoản Resend.
        params = {
            "from": "Student Management System <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "Reset Your Password - SMS",
            "html": html_content
        }

        try:
            email_response = resend.Emails.send(params)
            
            # Kiểm tra ID trả về
            if email_response and ('id' in email_response or hasattr(email_response, 'id')):
                # Resend phiên bản mới có thể trả về object thay vì dict
                print(f"✅ Email sent to {to_email}")
                return True
            else:
                print(f"❌ Resend API Error: {email_response}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False