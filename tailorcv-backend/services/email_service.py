import os
import requests
from typing import Dict, Any
from datetime import datetime

class EmailService:
    def __init__(self):
        self.formsubmit_endpoint = "https://formsubmit.co/ajax"
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'admin@tailorcv.com')
        
    def send_resume_email(self, user_email: str, resume_url: str) -> bool:
        """
        Send resume download link to user via FormSubmit
        """
        try:
            subject = "Your TailorCV Resume is Ready!"
            
            message = f"""
Hi there!

Your personalized resume has been generated successfully and is ready for download.

📄 Download your resume: {resume_url}

This resume has been optimized for ATS (Applicant Tracking Systems) and tailored to match your job description.

Tips for using your resume:
• Download the PDF and save it with a clear filename
• Review the content before submitting applications
• Consider upgrading to Premium for watermark-free resumes

Need help or have questions? Reply to this email and we'll get back to you soon.

Best of luck with your job search!

The TailorCV Team
"""
            
            return self._send_email(user_email, subject, message)
            
        except Exception as e:
            print(f"Failed to send resume email: {str(e)}")
            return False
    
    def send_payment_notification(self, user_email: str, screenshot_url: str) -> bool:
        """
        Send payment notification to admin
        """
        try:
            subject = "New UPI Payment Screenshot Uploaded - TailorCV"
            
            message = f"""
A new UPI payment screenshot has been uploaded for verification.

User Email: {user_email}
Screenshot URL: {screenshot_url}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review the payment and update the user's premium status accordingly.

To approve the payment:
1. Review the screenshot
2. Log into Supabase dashboard
3. Update the payment status to 'approved'
4. The user will automatically get premium access

Admin Dashboard: [Your admin dashboard URL]
"""
            
            return self._send_email(self.admin_email, subject, message)
            
        except Exception as e:
            print(f"Failed to send payment notification: {str(e)}")
            return False
    
    def send_premium_confirmation(self, user_email: str) -> bool:
        """
        Send premium upgrade confirmation to user
        """
        try:
            subject = "Welcome to TailorCV Premium! 🎉"
            
            message = f"""
Congratulations! Your payment has been verified and you now have Premium access.

🌟 Premium Features Unlocked:
• Watermark-free resumes
• Access to premium LaTeX templates
• Priority processing
• Advanced customization options
• Email delivery of resumes
• Unlimited resume generations
• Priority customer support

You can now generate unlimited professional resumes at: https://tailorcv.com/generate

Thank you for upgrading to Premium! We're excited to help you land your dream job.

Best regards,
The TailorCV Team
"""
            
            return self._send_email(user_email, subject, message)
            
        except Exception as e:
            print(f"Failed to send premium confirmation: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str) -> bool:
        """
        Send welcome email to new users
        """
        try:
            subject = "Welcome to TailorCV - Your AI Resume Generator!"
            
            message = f"""
Welcome to TailorCV!

Thank you for choosing TailorCV to help with your job search. We're here to help you create professional, ATS-friendly resumes that get noticed.

🚀 Getting Started:
1. Visit https://tailorcv.com/generate
2. Upload your LinkedIn profile or resume
3. Paste the job description you're applying for
4. Get your tailored resume in minutes!

💡 Tips for Success:
• Use specific job descriptions for best results
• Review and customize the generated content
• Consider upgrading to Premium for additional features

Need help? Reply to this email or visit our help center.

Happy job hunting!

The TailorCV Team
"""
            
            return self._send_email(user_email, subject, message)
            
        except Exception as e:
            print(f"Failed to send welcome email: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, message: str) -> bool:
        """
        Send email using FormSubmit service
        """
        try:
            # Prepare form data
            form_data = {
                'email': to_email,
                'subject': subject,
                'message': message,
                '_captcha': 'false',
                '_template': 'basic'
            }
            
            # Send POST request to FormSubmit
            response = requests.post(
                f"{self.formsubmit_endpoint}/{self.admin_email}",
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"FormSubmit error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Network error sending email: {str(e)}")
            return False
    
    def send_feedback_notification(self, user_email: str, feedback: str, rating: int) -> bool:
        """
        Send feedback notification to admin
        """
        try:
            subject = f"New Feedback from TailorCV User - {rating}/5 stars"
            
            message = f"""
New feedback received from a TailorCV user.

User Email: {user_email}
Rating: {rating}/5 stars
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Feedback:
{feedback}

Please review and consider for product improvements.
"""
            
            return self._send_email(self.admin_email, subject, message)
            
        except Exception as e:
            print(f"Failed to send feedback notification: {str(e)}")
            return False
    
    def send_error_notification(self, error_type: str, error_message: str, user_context: Dict[str, Any]) -> bool:
        """
        Send error notification to admin for monitoring
        """
        try:
            subject = f"TailorCV Error: {error_type}"
            
            message = f"""
An error occurred in the TailorCV application.

Error Type: {error_type}
Error Message: {error_message}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Context:
Email: {user_context.get('email', 'Not provided')}
IP Address: {user_context.get('ip', 'Unknown')}
User Agent: {user_context.get('user_agent', 'Unknown')}

Please investigate and fix if necessary.
"""
            
            return self._send_email(self.admin_email, subject, message)
            
        except Exception as e:
            print(f"Failed to send error notification: {str(e)}")
            return False
    
    def test_email_service(self) -> bool:
        """
        Test if email service is working
        """
        try:
            return self._send_email(
                self.admin_email,
                "TailorCV Email Service Test",
                "This is a test email to verify the email service is working correctly."
            )
        except Exception as e:
            print(f"Email service test failed: {str(e)}")
            return False