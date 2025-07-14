#!/usr/bin/env python3
"""
Simple health check script to test if the app can start
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Basic imports
        from flask import Flask
        print("✅ Flask imported")
        
        from flask_cors import CORS
        print("✅ Flask-CORS imported")
        
        import requests
        print("✅ Requests imported")
        
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported")
        
        # Google auth imports
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        print("✅ Google Auth imported")
        
        # ReportLab import
        from reportlab.lib.pagesizes import letter
        print("✅ ReportLab imported")
        
        # Service imports
        try:
            from services.supabase_service import SupabaseService
            print("✅ SupabaseService imported")
        except Exception as e:
            print(f"❌ SupabaseService import failed: {e}")
            
        try:
            from services.auth_service import AuthService
            print("✅ AuthService imported")
        except Exception as e:
            print(f"❌ AuthService import failed: {e}")
            
        try:
            from services.latex_service import LaTeXService
            print("✅ LaTeXService imported")
        except Exception as e:
            print(f"❌ LaTeXService import failed: {e}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\nTesting environment variables...")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'JWT_SECRET',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY'
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}...")
        else:
            print(f"❌ {var}: Not set")

def test_flask_app():
    """Test if Flask app can be created"""
    try:
        print("\nTesting Flask app creation...")
        
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health')
        def health():
            return {"status": "healthy"}
            
        print("✅ Flask app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def main():
    """Main health check"""
    print("🏥 TailorCV Backend Health Check")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test environment
    test_environment()
    
    # Test Flask app
    if not test_flask_app():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Health check passed!")
        print("The backend should be able to start successfully.")
        sys.exit(0)
    else:
        print("❌ Health check failed!")
        print("There are issues that need to be resolved.")
        sys.exit(1)

if __name__ == "__main__":
    main()