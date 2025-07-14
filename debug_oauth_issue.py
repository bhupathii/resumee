#!/usr/bin/env python3
"""
Debug Google OAuth authentication issues
"""
import os
import sys
import json
import requests
from datetime import datetime

def check_environment_setup():
    """Check if environment variables are properly configured"""
    print("🔍 Checking Environment Setup...")
    
    issues = []
    
    # Check backend .env
    backend_env = os.path.join('tailorcv-backend', '.env')
    if os.path.exists(backend_env):
        with open(backend_env, 'r') as f:
            content = f.read()
            
        # Extract Google Client ID
        google_client_id = None
        for line in content.split('\n'):
            if line.startswith('GOOGLE_CLIENT_ID='):
                google_client_id = line.split('=', 1)[1].strip()
                break
        
        if google_client_id and google_client_id != 'your_google_client_id_here.googleusercontent.com':
            if google_client_id.endswith('.googleusercontent.com'):
                print(f"✅ Backend Google Client ID: {google_client_id[:20]}...")
            else:
                print("❌ Backend Google Client ID format is invalid")
                issues.append("Google Client ID should end with .googleusercontent.com")
        else:
            print("❌ Backend Google Client ID not configured")
            issues.append("Set GOOGLE_CLIENT_ID in tailorcv-backend/.env")
            
        # Check JWT Secret
        jwt_secret = None
        for line in content.split('\n'):
            if line.startswith('JWT_SECRET='):
                jwt_secret = line.split('=', 1)[1].strip()
                break
                
        if jwt_secret and len(jwt_secret) >= 32:
            print("✅ JWT Secret is configured and long enough")
        else:
            print("❌ JWT Secret is missing or too short")
            issues.append("Set JWT_SECRET (at least 32 characters) in tailorcv-backend/.env")
            
        # Check Supabase config
        supabase_url = None
        supabase_key = None
        for line in content.split('\n'):
            if line.startswith('SUPABASE_URL='):
                supabase_url = line.split('=', 1)[1].strip()
            elif line.startswith('SUPABASE_ANON_KEY=') or line.startswith('SUPABASE_KEY='):
                supabase_key = line.split('=', 1)[1].strip()
                
        if supabase_url and supabase_url.startswith('https://'):
            print("✅ Supabase URL is configured")
        else:
            print("❌ Supabase URL is missing or invalid")
            issues.append("Set SUPABASE_URL in tailorcv-backend/.env")
            
        if supabase_key and len(supabase_key) > 50:
            print("✅ Supabase key is configured")
        else:
            print("❌ Supabase key is missing")
            issues.append("Set SUPABASE_ANON_KEY in tailorcv-backend/.env")
            
    else:
        print("❌ Backend .env file missing")
        issues.append("Create tailorcv-backend/.env file")
    
    # Check frontend .env
    frontend_env = os.path.join('tailorcv-frontend', '.env')
    if os.path.exists(frontend_env):
        with open(frontend_env, 'r') as f:
            content = f.read()
            
        # Check if frontend has matching Google Client ID
        if 'REACT_APP_GOOGLE_CLIENT_ID=' in content:
            print("✅ Frontend Google Client ID is configured")
        else:
            print("❌ Frontend Google Client ID missing")
            issues.append("Set REACT_APP_GOOGLE_CLIENT_ID in tailorcv-frontend/.env")
            
        # Check API URL
        if 'REACT_APP_API_URL=' in content:
            print("✅ Frontend API URL is configured")
        else:
            print("❌ Frontend API URL missing")
            issues.append("Set REACT_APP_API_URL in tailorcv-frontend/.env")
            
    else:
        print("❌ Frontend .env file missing")
        issues.append("Create tailorcv-frontend/.env file")
    
    return issues

def test_backend_connection():
    """Test if backend is running and responding"""
    print("\n🔍 Testing Backend Connection...")
    
    try:
        # Try to connect to local backend
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend is running and responding")
            data = response.json()
            print(f"   Health check: {data}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend at http://localhost:5000")
        print("   Make sure backend is running: cd tailorcv-backend && python app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend connection timed out")
        return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_google_oauth_endpoint():
    """Test the Google OAuth endpoint with a dummy token"""
    print("\n🔍 Testing Google OAuth Endpoint...")
    
    try:
        # Test with invalid token to see the exact error
        test_data = {
            "token": "dummy_invalid_token"
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/google',
            json=test_data,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 500 and "Google authentication not configured" in data.get('error', ''):
            print("❌ Google Client ID is not configured on backend")
            return "missing_client_id"
        elif response.status_code == 401 and "Invalid Google token" in data.get('error', ''):
            print("✅ Google OAuth endpoint is working (expected error with dummy token)")
            return "working"
        elif response.status_code == 500 and "Authentication failed" in data.get('error', ''):
            print(f"❌ Backend error: {data.get('error')}")
            return "backend_error"
        else:
            print(f"❌ Unexpected response: {response.status_code} - {data}")
            return "unexpected_error"
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        return "no_backend"
    except Exception as e:
        print(f"❌ Error testing OAuth endpoint: {e}")
        return "test_error"

def check_database_schema():
    """Check if database tables exist"""
    print("\n🔍 Checking Database Schema...")
    
    # This would require database connection, so we'll check if schema files exist
    schema_files = [
        'tailorcv-backend/database/auth_schema.sql',
        'tailorcv-backend/database/schema.sql'
    ]
    
    missing_files = []
    for file_path in schema_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Database schema files are missing")
        print("   Make sure to run the SQL scripts on your Supabase database")
    else:
        print("✅ Database schema files are present")
        print("⚠️  Make sure you've run these SQL scripts on your Supabase database")
    
    return len(missing_files) == 0

def create_fix_recommendations(issues, backend_status, oauth_status, db_status):
    """Create specific fix recommendations based on test results"""
    print("\n🔧 Fix Recommendations...")
    
    if issues:
        print("\n❌ Environment Issues:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    if not backend_status:
        print("\n❌ Backend Issues:")
        print("   1. Start the backend: cd tailorcv-backend && python app.py")
        print("   2. Make sure all dependencies are installed: pip install -r requirements.txt")
    
    if oauth_status == "missing_client_id":
        print("\n❌ Google OAuth Issues:")
        print("   1. Copy your Google Client ID from Google Cloud Console")
        print("   2. Update GOOGLE_CLIENT_ID in tailorcv-backend/.env")
        print("   3. Update REACT_APP_GOOGLE_CLIENT_ID in tailorcv-frontend/.env")
        print("   4. Restart both applications")
    
    if not db_status:
        print("\n❌ Database Issues:")
        print("   1. Run auth_schema.sql on your Supabase database")
        print("   2. Make sure SUPABASE_URL and SUPABASE_ANON_KEY are correct")
    
    # Most likely fix for the specific error
    print("\n🎯 Most Likely Fix for 'Invalid Google token or authentication failed':")
    print("   1. Your Google Client ID is missing or incorrect")
    print("   2. Copy the EXACT Client ID from Google Cloud Console")
    print("   3. It should end with .googleusercontent.com")
    print("   4. Update both frontend and backend .env files")
    print("   5. Restart both applications")

def main():
    """Main debugging function"""
    print("🚀 Google OAuth Authentication Debugger")
    print("=" * 50)
    
    # Run all checks
    issues = check_environment_setup()
    backend_status = test_backend_connection()
    oauth_status = test_google_oauth_endpoint() if backend_status else "no_backend"
    db_status = check_database_schema()
    
    # Create recommendations
    create_fix_recommendations(issues, backend_status, oauth_status, db_status)
    
    print("\n" + "=" * 50)
    print("📋 Debug Summary:")
    print(f"   Environment: {'✅ OK' if not issues else '❌ Issues found'}")
    print(f"   Backend: {'✅ Running' if backend_status else '❌ Not running'}")
    print(f"   OAuth Endpoint: {'✅ Working' if oauth_status == 'working' else '❌ Issues'}")
    print(f"   Database Schema: {'✅ Files present' if db_status else '❌ Files missing'}")

if __name__ == "__main__":
    main()