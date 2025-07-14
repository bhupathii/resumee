#!/usr/bin/env python3
"""
Ultra-minimal TailorCV backend for Docker debugging
Starts immediately without loading any services
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime

print("🐳 Docker: Starting ultra-minimal TailorCV backend...")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🌐 Environment PORT: {os.environ.get('PORT', 'not set')}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

print("✅ Flask app initialized")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Ultra-simple health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Ultra-minimal backend is running",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "port": os.environ.get('PORT', '5000'),
        "environment_vars": {
            "PORT": os.environ.get('PORT'),
            "DEBUG": os.environ.get('DEBUG'),
            "PYTHONPATH": os.environ.get('PYTHONPATH')
        }
    }), 200

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "message": "Test endpoint working",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "TailorCV Backend is running",
        "health": "/api/health",
        "test": "/api/test",
        "auth": "/api/auth/google"
    }), 200

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Google OAuth authentication - Ultra-minimal version"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
            
        google_token = data.get('token')
        if not google_token:
            return jsonify({"error": "Google token is required"}), 400
        
        # Ultra-minimal response - no actual authentication
        # This is for testing the connection only
        return jsonify({
            "error": "Google authentication not configured in ultra-minimal mode",
            "message": "Backend is running but auth services are not loaded",
            "received_token": bool(google_token),
            "timestamp": datetime.now().isoformat()
        }), 503
        
    except Exception as e:
        return jsonify({
            "error": f"Authentication failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user - Ultra-minimal version"""
    return jsonify({
        "error": "Authentication service not available in ultra-minimal mode",
        "message": "Backend is running but auth services are not loaded",
        "timestamp": datetime.now().isoformat()
    }), 503

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout - Ultra-minimal version"""
    return jsonify({
        "message": "Logout endpoint reached",
        "note": "No actual logout in ultra-minimal mode",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🚀 Starting Flask server on {host}:{port}")
    print(f"🔗 Health check: http://{host}:{port}/api/health")
    
    try:
        app.run(host=host, port=port, debug=False)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1) 