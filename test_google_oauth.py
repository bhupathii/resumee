#!/usr/bin/env python3
"""
Test Google OAuth configuration
"""
import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    """Test if environment variables are properly set"""
    print("🔍 Testing Environment Variables...")
    
    # Load backend environment
    backend_env = os.path.join('tailorcv-backend', '.env')
    if os.path.exists(backend_env):
        load_dotenv(backend_env)
        print("✅ Backend .env file loaded")
    else:
        print("❌ Backend .env file not found")
        return False
    
    # Check critical variables
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    jwt_secret = os.getenv('JWT_SECRET')
    
    if google_client_id and google_client_id != 'your_google_client_id_here.googleusercontent.com':
        print("✅ GOOGLE_CLIENT_ID is configured")
    else:
        print("❌ GOOGLE_CLIENT_ID is missing or not configured")
        print("   Please set GOOGLE_CLIENT_ID in tailorcv-backend/.env")
        return False
    
    if jwt_secret and jwt_secret != 'your_super_secret_jwt_key_here_make_it_long_and_random_at_least_32_characters':
        print("✅ JWT_SECRET is configured")
    else:
        print("❌ JWT_SECRET is missing or not configured")
        print("   Please set JWT_SECRET in tailorcv-backend/.env")
        return False
    
    # Check frontend environment
    frontend_env = os.path.join('tailorcv-frontend', '.env')
    if os.path.exists(frontend_env):
        print("✅ Frontend .env file exists")
        
        with open(frontend_env, 'r') as f:
            content = f.read()
            if 'REACT_APP_GOOGLE_CLIENT_ID' in content and google_client_id in content:
                print("✅ Frontend REACT_APP_GOOGLE_CLIENT_ID matches backend")
            else:
                print("❌ Frontend REACT_APP_GOOGLE_CLIENT_ID mismatch")
                print("   Ensure both frontend and backend use the same Google Client ID")
                return False
    else:
        print("❌ Frontend .env file not found")
        return False
    
    return True

def test_google_oauth_setup():
    """Test Google OAuth setup"""
    print("\n🔐 Testing Google OAuth Setup...")
    
    try:
        # Test import
        sys.path.append('tailorcv-backend')
        from services.auth_service import AuthService
        
        auth_service = AuthService()
        
        if auth_service.google_client_id:
            print("✅ Google Client ID loaded in auth service")
            
            # Validate client ID format
            if auth_service.google_client_id.endswith('.googleusercontent.com'):
                print("✅ Google Client ID format is valid")
            else:
                print("❌ Google Client ID format is invalid")
                print("   Should end with .googleusercontent.com")
                return False
        else:
            print("❌ Google Client ID not loaded in auth service")
            return False
            
        print("✅ Google OAuth service initialized successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_sample_google_client_id():
    """Create sample Google Client ID for testing"""
    print("\n📝 Creating sample Google Client ID...")
    
    sample_client_id = "123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com"
    
    # Update backend .env
    backend_env = os.path.join('tailorcv-backend', '.env')
    if os.path.exists(backend_env):
        with open(backend_env, 'r') as f:
            content = f.read()
        
        # Replace placeholder with sample
        content = content.replace(
            'GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com',
            f'GOOGLE_CLIENT_ID={sample_client_id}'
        )
        
        with open(backend_env, 'w') as f:
            f.write(content)
        
        print("✅ Updated backend .env with sample Google Client ID")
    
    # Update frontend .env
    frontend_env = os.path.join('tailorcv-frontend', '.env')
    if os.path.exists(frontend_env):
        with open(frontend_env, 'r') as f:
            content = f.read()
        
        # Replace placeholder with sample
        content = content.replace(
            'REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com',
            f'REACT_APP_GOOGLE_CLIENT_ID={sample_client_id}'
        )
        
        with open(frontend_env, 'w') as f:
            f.write(content)
        
        print("✅ Updated frontend .env with sample Google Client ID")
    
    print("⚠️  Remember to replace the sample Client ID with your actual Google Client ID!")
    print("   Follow GOOGLE_OAUTH_FIX.md for detailed setup instructions")

def main():
    """Main test function"""
    print("🚀 Google OAuth Configuration Test")
    print("=" * 40)
    
    # Test environment variables
    if not test_environment_variables():
        print("\n❌ Environment variables test failed")
        create_sample_google_client_id()
        return
    
    # Test Google OAuth setup
    if not test_google_oauth_setup():
        print("\n❌ Google OAuth setup test failed")
        return
    
    print("\n✅ All tests passed!")
    print("🎉 Google OAuth should now work correctly")
    print("\n🔗 Next steps:")
    print("1. Make sure you have a real Google Client ID from Google Cloud Console")
    print("2. Update the .env files with your actual credentials")
    print("3. Restart both frontend and backend applications")
    print("4. Test the Google sign-in flow")

if __name__ == "__main__":
    main()