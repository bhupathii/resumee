from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import json
from datetime import datetime
from dotenv import load_dotenv
from services.openrouter_service import OpenRouterService
from services.supabase_service import SupabaseService
from services.linkedin_service import LinkedInService
from services.pdf_service import PDFService
from services.latex_service import LaTeXService
from services.email_service import EmailService
from services.auth_service import AuthService
from utils.validators import validate_email, validate_file
from utils.rate_limiter import RateLimiter
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

openrouter_service = OpenRouterService()
supabase_service = SupabaseService()
linkedin_service = LinkedInService()
pdf_service = PDFService()
latex_service = LaTeXService()
email_service = EmailService()
auth_service = AuthService()
rate_limiter = RateLimiter()

def get_current_user():
    """
    Get current user from session token (if provided)
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        session_token = auth_header.split(' ')[1]
        return auth_service.get_user_by_session(session_token)
    return None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """
    Authenticate user with Google OAuth token
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
            
        google_token = data.get('token')
        
        if not google_token:
            return jsonify({"error": "Google token is required"}), 400
        
        # Check if Google Client ID is configured
        if not auth_service.google_client_id:
            return jsonify({"error": "Google authentication not configured on server"}), 500
        
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # Authenticate user
        auth_result = auth_service.authenticate_user(google_token, client_ip)
        
        if not auth_result:
            return jsonify({"error": "Invalid Google token or authentication failed"}), 401
        
        return jsonify({
            "success": True,
            "user": {
                "id": auth_result['user']['id'],
                "name": auth_result['user']['name'],
                "email": auth_result['user']['email'],
                "profile_picture": auth_result['user']['profile_picture'],
                "is_premium": auth_result['user'].get('is_premium', False),
                "generation_count": auth_result['user'].get('generation_count', 0)
            },
            "session_token": auth_result['session_token'],
            "expires_at": auth_result['expires_at']
        })
        
    except Exception as e:
        print(f"Google auth error: {str(e)}")
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Log out current user
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Session token required"}), 400
        
        session_token = auth_header.split(' ')[1]
        
        if auth_service.logout_user(session_token):
            return jsonify({"success": True, "message": "Logged out successfully"})
        else:
            return jsonify({"error": "Failed to logout"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """
    Get current user information
    """
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get premium status
        premium_status = auth_service.check_premium_status_authenticated(user['id'])
        
        return jsonify({
            "success": True,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "profile_picture": user['profile_picture'],
                "is_premium": premium_status['is_premium'],
                "generation_count": premium_status['generation_count'],
                "last_generated": premium_status.get('last_generated'),
                "upgraded_at": premium_status.get('upgraded_at')
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get user info: {str(e)}"}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # Get current user (if authenticated)
        current_user = get_current_user()
        
        # Check rate limiting (higher limits for authenticated users)
        if current_user:
            # Authenticated users get higher rate limits
            premium_status = auth_service.check_premium_status_authenticated(current_user['id'])
            is_premium = premium_status['is_premium']
            # Use premium rate limiter if premium, otherwise standard authenticated rate
            max_requests = 50 if is_premium else 10
        else:
            # Guest users
            if not rate_limiter.allow_request(client_ip):
                return jsonify({"error": "Too many requests. Please try again later."}), 429
            is_premium = False
        
        linkedin_url = request.form.get('linkedinUrl')
        job_description = request.form.get('jobDescription')
        email = request.form.get('email')
        resume_file = request.files.get('resume')
        
        # Use authenticated user's email if available
        if current_user and not email:
            email = current_user['email']
        
        if not job_description:
            return jsonify({"error": "Job description is required"}), 400
        
        resume_data = None
        
        if linkedin_url:
            try:
                resume_data = linkedin_service.extract_profile_data(linkedin_url)
            except Exception as e:
                return jsonify({"error": f"Failed to extract LinkedIn data: {str(e)}"}), 400
        
        elif resume_file:
            if not validate_file(resume_file):
                return jsonify({"error": "Invalid file format or size"}), 400
            
            try:
                resume_data = pdf_service.extract_text_from_pdf(resume_file)
            except Exception as e:
                return jsonify({"error": f"Failed to extract PDF data: {str(e)}"}), 400
        
        else:
            return jsonify({"error": "Either LinkedIn URL or resume file is required"}), 400
        
        try:
            optimized_resume = openrouter_service.optimize_resume(resume_data, job_description)
        except Exception as e:
            return jsonify({"error": f"Failed to optimize resume: {str(e)}"}), 500
        
        # Determine premium status
        if current_user:
            # For authenticated users, use their premium status
            premium_status = auth_service.check_premium_status_authenticated(current_user['id'])
            is_premium = premium_status['is_premium']
        elif email:
            # For guest users with email, check premium status
            user_status = supabase_service.check_user_premium_status(email, client_ip)
            is_premium = user_status.get('is_premium', False)
        else:
            is_premium = False
        
        try:
            pdf_buffer = latex_service.generate_pdf(optimized_resume, is_premium)
        except Exception as e:
            return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500
        
        temp_filename = f"resume_{uuid.uuid4().hex}.pdf"
        temp_filepath = os.path.join(tempfile.gettempdir(), temp_filename)
        
        with open(temp_filepath, 'wb') as f:
            f.write(pdf_buffer)
        
        try:
            file_url = supabase_service.upload_resume(temp_filepath, temp_filename)
        except Exception as e:
            return jsonify({"error": f"Failed to upload resume: {str(e)}"}), 500
        
        # Log generation with user_id if authenticated
        generation_data = {
            'email': email,
            'ip': client_ip,
            'job_description_snippet': job_description[:100],
            'resume_url': file_url,
            'is_premium': is_premium
        }
        
        if current_user:
            generation_data['user_id'] = current_user['id']
            # Increment generation count for authenticated users
            auth_service.increment_generation_count(current_user['id'])
        
        supabase_service.client.table('generations').insert(generation_data).execute()
        
        if email:
            try:
                email_service.send_resume_email(email, file_url)
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
        
        os.remove(temp_filepath)
        
        return jsonify({
            "success": True,
            "resumeUrl": file_url,
            "isPremium": is_premium,
            "message": "Resume generated successfully",
            "user": {
                "authenticated": current_user is not None,
                "generation_count": premium_status.get('generation_count', 0) if current_user else None
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/payment/upload', methods=['POST'])
def upload_payment_screenshot():
    try:
        email = request.form.get('email')
        screenshot = request.files.get('screenshot')
        timestamp = request.form.get('timestamp')
        
        if not email or not screenshot:
            return jsonify({"error": "Email and screenshot are required"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        if not validate_file(screenshot, allowed_types=['image/png', 'image/jpeg', 'image/jpg']):
            return jsonify({"error": "Invalid file format or size"}), 400
        
        screenshot_filename = f"payment_{uuid.uuid4().hex}_{screenshot.filename}"
        screenshot_path = os.path.join(tempfile.gettempdir(), screenshot_filename)
        screenshot.save(screenshot_path)
        
        try:
            screenshot_url = supabase_service.upload_payment_screenshot(screenshot_path, screenshot_filename)
        except Exception as e:
            return jsonify({"error": f"Failed to upload screenshot: {str(e)}"}), 500
        
        payment_record = {
            "email": email,
            "screenshot_url": screenshot_url,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": "pending"
        }
        
        try:
            supabase_service.create_payment_record(payment_record)
        except Exception as e:
            return jsonify({"error": f"Failed to create payment record: {str(e)}"}), 500
        
        try:
            email_service.send_payment_notification(email, screenshot_url)
        except Exception as e:
            print(f"Failed to send payment notification: {str(e)}")
        
        os.remove(screenshot_path)
        
        return jsonify({
            "success": True,
            "message": "Payment screenshot uploaded successfully. You'll receive confirmation within 24 hours."
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/user/status', methods=['GET'])
def get_user_status():
    try:
        email = request.args.get('email')
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        user_status = supabase_service.check_user_premium_status(email, client_ip)
        
        return jsonify({
            "success": True,
            "isPremium": user_status.get('is_premium', False),
            "generationCount": user_status.get('generation_count', 0),
            "lastGenerated": user_status.get('last_generated')
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG') == 'True')