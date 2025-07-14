#!/usr/bin/env python3
"""
Google OAuth Configuration Test Script for TailorCV

This script helps verify that Google OAuth is properly configured
for both development and production environments.
"""

import os
import sys
import requests
import json
from urllib.parse import urlparse

def test_environment_variables():
    """Test if required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    # Backend variables
    backend_vars = {
        'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
        'JWT_SECRET': os.environ.get('JWT_SECRET'),
        'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
        'SUPABASE_KEY': os.environ.get('SUPABASE_KEY'),
    }
    
    # Frontend variables (simulated)
    frontend_vars = {
        'REACT_APP_GOOGLE_CLIENT_ID': os.environ.get('REACT_APP_GOOGLE_CLIENT_ID'),
        'REACT_APP_API_URL': os.environ.get('REACT_APP_API_URL'),
    }
    
    print("\n📦 Backend Environment Variables:")
    for var, value in backend_vars.items():
        status = "✅" if value else "❌"
        display_value = value[:20] + "..." if value and len(value) > 20 else value or "Not set"
        print(f"  {status} {var}: {display_value}")
    
    print("\n🌐 Frontend Environment Variables:")
    for var, value in frontend_vars.items():
        status = "✅" if value else "❌"
        display_value = value[:50] + "..." if value and len(value) > 50 else value or "Not set"
        print(f"  {status} {var}: {display_value}")
    
    # Check if Google Client IDs match
    backend_client_id = backend_vars['GOOGLE_CLIENT_ID']
    frontend_client_id = frontend_vars['REACT_APP_GOOGLE_CLIENT_ID']
    
    if backend_client_id and frontend_client_id:
        if backend_client_id == frontend_client_id:
            print("✅ Google Client IDs match between frontend and backend")
        else:
            print("❌ Google Client IDs do NOT match between frontend and backend")
    
    return all(backend_vars.values())

def test_backend_health(api_url):
    """Test if backend is responding"""
    print(f"\n🏥 Testing Backend Health at {api_url}...")
    
    try:
        response = requests.get(f"{api_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach backend: {e}")
        return False

def test_auth_endpoints(api_url):
    """Test authentication endpoints"""
    print(f"\n🔐 Testing Auth Endpoints at {api_url}...")
    
    # Test Google auth endpoint (without token)
    try:
        response = requests.post(f"{api_url}/api/auth/google", 
                               json={}, 
                               timeout=10)
        if response.status_code == 400:
            data = response.json()
            if "token is required" in data.get('error', '').lower():
                print("✅ Google auth endpoint responds correctly to missing token")
            else:
                print(f"⚠️  Unexpected error message: {data.get('error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach auth endpoint: {e}")
    
    # Test auth/me endpoint (without token)
    try:
        response = requests.get(f"{api_url}/api/auth/me", timeout=10)
        if response.status_code == 401:
            data = response.json()
            print("✅ Auth/me endpoint correctly rejects unauthenticated requests")
        else:
            print(f"❌ Unexpected response from auth/me: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach auth/me endpoint: {e}")

def check_google_client_id_format(client_id):
    """Check if Google Client ID has correct format"""
    if not client_id:
        return False, "Not set"
    
    if not client_id.endswith('.googleusercontent.com'):
        return False, "Should end with .googleusercontent.com"
    
    if len(client_id) < 50:
        return False, "Seems too short for a valid Google Client ID"
    
    return True, "Format looks correct"

def test_google_client_id():
    """Test Google Client ID format and configuration"""
    print("\n🔑 Testing Google Client ID Configuration...")
    
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    is_valid, message = check_google_client_id_format(client_id)
    
    status = "✅" if is_valid else "❌"
    print(f"  {status} Google Client ID format: {message}")
    
    return is_valid

def main():
    """Main test function"""
    print("🧪 TailorCV Google OAuth Configuration Test")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test Google Client ID format
    client_id_ok = test_google_client_id()
    
    # Test backend if API URL is provided
    api_url = os.environ.get('REACT_APP_API_URL') or input("\nEnter your backend API URL (or press Enter to skip): ").strip()
    
    if api_url:
        # Clean up URL
        if not api_url.startswith(('http://', 'https://')):
            api_url = 'https://' + api_url
        
        backend_ok = test_backend_health(api_url)
        if backend_ok:
            test_auth_endpoints(api_url)
    else:
        print("\n⏭️  Skipping backend tests (no API URL provided)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    if env_ok and client_id_ok:
        print("✅ Configuration looks good!")
        print("\n🎯 Next Steps:")
        print("1. Deploy your backend with the environment variables")
        print("2. Deploy your frontend with the environment variables") 
        print("3. Set up Google Cloud Console OAuth credentials")
        print("4. Test the Google Sign-In on your deployed frontend")
        print("\n📖 See GOOGLE_AUTH_SETUP.md for detailed setup instructions")
    else:
        print("❌ Configuration issues found!")
        print("\n🔧 Required Actions:")
        if not env_ok:
            print("- Set missing environment variables")
        if not client_id_ok:
            print("- Configure valid Google Client ID")
        print("- See GOOGLE_AUTH_SETUP.md for detailed setup instructions")

if __name__ == "__main__":
    main() 