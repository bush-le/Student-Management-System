import resend
from config import Config

class EmailService:
    """
    Class handling email sending via Resend API.
    Acts as the 'Email System' Actor in system design.
    """

    @staticmethod
    def send_recovery_email(to_email, reset_code):
        """
        [cite_start]FR-04: Send password recovery code [cite: 53-54].
        This function sends an HTML email containing the OTP code to the user.
        """
        # Check if API Key is configured in config.py
        if not Config.RESEND_API_KEY:
            print("⚠️ Error: RESEND_API_KEY is not configured in .env or config.py")
            return False

        # Set API Key for resend library
        resend.api_key = Config.RESEND_API_KEY

        # Professional HTML email content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px;">
            <h2 style="color: #2c3e50; text-align: center;">Password Recovery Request</h2>
            <p>Hello,</p>
            <p>You recently requested to reset your password for the <strong>Student Management System</strong>.</p>
            <p>Use the following code to complete your password reset process:</p>
            
            <div style="background-color: #f4f4f4; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <h1 style="color: #27ae60; margin: 0; letter-spacing: 5px; font-size: 32px;">{reset_code}</h1>
            </div>
            
            <p>This code is valid for <strong>15 minutes</strong>.</p>
            <p style="color: #7f8c8d; font-size: 14px;">If you did not request a password reset, please ignore this email.</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin-top: 20px;" />
            <p style="font-size: 12px; color: #95a5a6; text-align: center;">Group 01 - University of Transport Ho Chi Minh City</p>
        </div>
        """

        # Configure sending parameters
        # IMPORTANT NOTE:
        # With a free Resend account (domain not added), you are only allowed to:
        # 1. Send FROM: "onboarding@resend.dev"
        # 2. Send TO: Only the email you used to register for the Resend account.
        params = {
            "from": "Student Management System <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "Reset Your Password - Student Management System",
            "html": html_content
        }

        try:
            # Execute email sending
            email_response = resend.Emails.send(params)
            
            # Check response (Resend returns a dict with key 'id' if successful)
            if email_response and 'id' in email_response:
                print(f"✅ Email sent successfully to {to_email}. ID: {email_response['id']}")
                return True
            else:
                print(f"❌ Resend API did not return an ID: {email_response}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send email via Resend: {str(e)}")
            return False