import os
import sys
from datetime import datetime

# --- Startup Logging ---
print("--- Starting TailorCV Backend ---")
print(f"Python Version: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
# Log key environment variables to check if they are being passed correctly
print(f"PORT from env: {os.environ.get('PORT', 'Not Set')}")
print(f"GOOGLE_CLIENT_ID from env: {'Present' if os.environ.get('GOOGLE_CLIENT_ID') else 'MISSING'}")
print(f"SUPABASE_URL from env: {'Present' if os.environ.get('SUPABASE_URL') else 'MISSING'}")
print("-----------------------------")


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import json
from dotenv import load_dotenv
from services.openrouter_service import OpenRouterService
from services.supabase_service import SupabaseService
from services.linkedin_service import LinkedInService
from services.pdf_service import PDFService
from services.latex_service import LaTeXService
from services.email_service import EmailService
from services.auth_service import AuthService
from utils.validators import validate_email, validate_file
from utils.rate_limiter import standard_limiter, premium_limiter
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Graceful Service Initialization ---
service_status = {}

def initialize_service(service_name, service_class):
    try:
        service_instance = service_class()
        service_status[service_name] = "✅ Loaded"
        return service_instance
    except Exception as e:
        error_message = f"❌ Failed to load {service_name}: {e}"
        print(error_message)
        service_status[service_name] = error_message
        return None

openrouter_service = initialize_service('OpenRouter', OpenRouterService)
supabase_service = initialize_service('Supabase', SupabaseService)
linkedin_service = initialize_service('LinkedIn', LinkedInService)
pdf_service = initialize_service('PDF', PDFService)
latex_service = initialize_service('LaTeX', LaTeXService)
email_service = initialize_service('Email', EmailService)
auth_service = initialize_service('Auth', AuthService)


def get_current_user():
    """
    Get current user from session token (if provided)
    """
    if not auth_service:
        return None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        session_token = auth_header.split(' ')[1]
        return auth_service.get_user_by_session(session_token)
    return None

@app.route('/api/health', methods=['GET'])
def health_check():
    # The service is "healthy" if it can respond to requests.
    # It's "fully_functional" only if core services are loaded.
    core_services_loaded = supabase_service is not None and auth_service is not None
    status_code = 200 if core_services_loaded else 503  # 503 Service Unavailable

    return jsonify({
        "status": "healthy" if core_services_loaded else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": service_status
    }), status_code

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """
    Authenticate user with Google OAuth token
    """
    if not auth_service:
        return jsonify({"error": "Authentication service is not available. Check the backend deployment logs."}), 503

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
        
        # Authenticate user. This will now propagate the detailed exception.
        auth_result = auth_service.authenticate_user(google_token, client_ip)
        
        # This part will now only be reached on success.
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

    except ValueError as e:
        # Catch the specific error from token verification and return it as a clear 401 Unauthorized error.
        return jsonify({"error": f"Google token validation failed: {str(e)}"}), 401
        
    except Exception as e:
        # Catch other potential errors during user creation or session handling.
        print(f"Google auth error: {str(e)}")
        # Check for Supabase RLS error specifically
        if "violates row-level security policy" in str(e):
             return jsonify({"error": "Database security policy is blocking user creation. Please check your Supabase RLS policies for the 'users' table."}), 500
        return jsonify({"error": f"An unexpected authentication error occurred: {str(e)}"}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Log out current user
    """
    if not auth_service:
        return jsonify({"error": "Authentication service is not available."}), 503

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Session token required"}), 400
        
        session_token = auth_header.split(' ')[1]
        
        if auth_service.logout_user(session_token):
            return jsonify({"success": True, "message": "Logged out successfully"})
        else:
            return jsonify({"success": False, "message": "Logout failed"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """
    Get current user's profile and status
    """
    if not auth_service:
        return jsonify({"error": "Authentication service is not available."}), 503

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Not authenticated or session token missing"}), 401
            
        session_token = auth_header.split(' ')[1]
        user_data = auth_service.get_user_by_session(session_token)
        
        if not user_data:
            return jsonify({"error": "Invalid session or session expired"}), 401
            
        user = user_data
        
        # Check premium status
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
        print(f"Error fetching user info: {e}")
        return jsonify({"error": "Failed to retrieve user information"}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generates a resume from LinkedIn profile or uploaded resume
    """
    if not openrouter_service or not latex_service or not supabase_service:
        return jsonify({"error": "One or more services required for resume generation are unavailable."}), 503

    try:
        # Check rate limit
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user = get_current_user()
        
        is_premium = False
        if user:
            premium_status = auth_service.check_premium_status_authenticated(user['id'])
            is_premium = premium_status['is_premium']
        
        # Use the appropriate rate limiter based on premium status
        if is_premium:
            limiter = premium_limiter
        else:
            limiter = standard_limiter
            
        # The key for the rate limiter is the user's ID if they are logged in, otherwise their IP.
        limiter_key = user['id'] if user else client_ip

        if not limiter.allow_request(limiter_key):
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

        data = request.form
        job_description = data.get('job_description')
        linkedin_profile_url = data.get('linkedin_url')
        uploaded_resume = request.files.get('resume')
        template_name = data.get('template', 'jakes_resume')

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400
        
        if not linkedin_profile_url and not uploaded_resume:
            return jsonify({"error": "Either LinkedIn URL or a resume file is required"}), 400

        if template_name not in ['free_resume', 'premium_resume', 'jakes_resume']:
            return jsonify({"error": "Invalid template name"}), 400

        # Process input
        if linkedin_profile_url:
            print(f"Fetching LinkedIn profile: {linkedin_profile_url}")
            profile_data = linkedin_service.get_profile(linkedin_profile_url)
            if not profile_data:
                return jsonify({"error": "Failed to fetch LinkedIn profile"}), 500
            
            # Use the full profile text for analysis
            resume_text = json.dumps(profile_data)

        elif uploaded_resume:
            if not validate_file(uploaded_resume):
                return jsonify({"error": "Invalid file type or size"}), 400

            print(f"Processing uploaded resume: {uploaded_resume.filename}")
            resume_text = pdf_service.extract_text(uploaded_resume.stream)
        
        # Use OpenRouter to tailor the resume
        print("Generating tailored content with OpenRouter...")
        tailored_content_str = openrouter_service.generate_resume_content(resume_text, job_description)
        
        try:
            tailored_content = json.loads(tailored_content_str)
        except json.JSONDecodeError:
            print("Failed to parse JSON from OpenRouter, using raw string.")
            # Fallback for non-JSON content
            tailored_content = {"summary": tailored_content_str, "experiences": [], "skills": ""}

        # Generate LaTeX PDF
        print(f"Generating PDF with template: {template_name}.tex")
        pdf_bytes = latex_service.generate_pdf(template_name, tailored_content, is_premium)

        if not pdf_bytes:
            return jsonify({"error": "Failed to generate PDF: LaTeX compilation failed"}), 500

        # Save generation record to Supabase
        if user:
            auth_service.increment_generation_count(user['id'])
            supabase_service.save_generation(user_id=user['id'], job_description=job_description)

        # Return the generated PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(pdf_bytes)
        temp_file.close()
        
        return send_file(temp_file.name, as_attachment=True, download_name='Tailored_Resume.pdf')

    except Exception as e:
        print(f"Error in generate_resume: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during resume generation."}), 500


@app.route('/api/payment/upload', methods=['POST'])
def upload_payment_screenshot():
    """
    Handles payment screenshot uploads
    """
    if not supabase_service or not email_service:
        return jsonify({"error": "Payment processing services are unavailable."}), 503

    try:
        email = request.form.get('email')
        screenshot = request.files.get('screenshot')

        if not email or not validate_email(email):
            return jsonify({"error": "A valid email is required"}), 400
        
        if not screenshot or not validate_file(screenshot, content_types=['image/jpeg', 'image/png']):
            return jsonify({"error": "A valid screenshot (JPG/PNG) is required"}), 400

        # Upload to Supabase Storage
        file_path = f"payment_screenshots/{uuid.uuid4()}{os.path.splitext(screenshot.filename)[1]}"
        supabase_service.upload_file(file_path, screenshot.stream.read(), screenshot.content_type)
        
        public_url = supabase_service.get_public_url(file_path)

        # Save payment record
        supabase_service.save_payment(email, public_url)

        # Send notification email
        email_service.send_payment_notification(email, public_url)

        return jsonify({"success": True, "message": "Payment proof uploaded. We will review it shortly."})

    except Exception as e:
        print(f"Payment upload error: {str(e)}")
        return jsonify({"error": "Failed to process payment upload."}), 500


@app.route('/api/user/status', methods=['GET'])
def get_user_status():
    """
    Get user status (premium, generation count)
    """
    if not auth_service:
        return jsonify({"error": "Authentication service is not available."}), 503
        
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Not authenticated"}), 401
            
        premium_status = auth_service.check_premium_status_authenticated(user['id'])
        
        return jsonify({
            "is_premium": premium_status['is_premium'],
            "generation_count": premium_status['generation_count']
        })
        
    except Exception as e:
        return jsonify({"error": "Failed to get user status"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG') == 'True')