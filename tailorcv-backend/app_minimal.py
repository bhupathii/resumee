#!/usr/bin/env python3
"""
Minimal TailorCV backend with graceful error handling
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables for services
auth_service = None
latex_service = None
services_loaded = False

def load_services():
    """Load services with graceful error handling"""
    global auth_service, latex_service, services_loaded
    
    try:
        print("Loading services...")
        
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Environment variables loaded")
        except ImportError:
            print("⚠️  python-dotenv not available")
        
        # Load auth service
        try:
            from services.auth_service import AuthService
            auth_service = AuthService()
            print("✅ AuthService loaded")
        except Exception as e:
            print(f"❌ AuthService failed: {e}")
            auth_service = None
        
        # Load LaTeX service
        try:
            from services.latex_service import LaTeXService
            latex_service = LaTeXService()
            print("✅ LaTeXService loaded")
        except Exception as e:
            print(f"❌ LaTeXService failed: {e}")
            latex_service = None
        
        services_loaded = True
        print("✅ Services loading completed")
        
    except Exception as e:
        print(f"❌ Service loading failed: {e}")
        services_loaded = False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "auth_service": auth_service is not None,
                "latex_service": latex_service is not None,
                "services_loaded": services_loaded
            },
            "environment": {
                "port": os.environ.get('PORT', '5000'),
                "debug": os.environ.get('DEBUG', 'False'),
                "google_client_id_set": bool(os.environ.get('GOOGLE_CLIENT_ID')),
                "supabase_url_set": bool(os.environ.get('SUPABASE_URL')),
                "supabase_anon_key_set": bool(os.environ.get('SUPABASE_ANON_KEY')),
                "jwt_secret_set": bool(os.environ.get('JWT_SECRET'))
            }
        }
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Google OAuth authentication"""
    try:
        if not auth_service:
            return jsonify({"error": "Authentication service not available"}), 503
        
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

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """Get current user information"""
    if not auth_service:
        return jsonify({"error": "Authentication service not available"}), 503
    
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Session token required"}), 401
        
        session_token = auth_header.split(' ')[1]
        user = auth_service.get_user_by_session(session_token)
        
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

@app.route('/api/status', methods=['GET'])
def status():
    """Detailed status endpoint"""
    return jsonify({
        "app": "TailorCV Backend",
        "version": "1.0.2",
        "environment": "production" if not os.environ.get('DEBUG') else "development",
        "services_loaded": services_loaded,
        "available_endpoints": [
            "/api/health",
            "/api/status", 
            "/api/auth/google",
            "/api/auth/me"
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Load services on startup
load_services()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting TailorCV Backend on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Services loaded: {services_loaded}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)