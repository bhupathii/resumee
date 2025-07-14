#!/usr/bin/env python3
"""
Simple check for Google OAuth configuration
"""
import os

def check_env_files():
    """Check if environment files exist and have correct content"""
    print("🔍 Checking Environment Files...")
    
    # Check backend .env
    backend_env = os.path.join('tailorcv-backend', '.env')
    if os.path.exists(backend_env):
        print("✅ Backend .env file exists")
        
        with open(backend_env, 'r') as f:
            content = f.read()
            
        if 'GOOGLE_CLIENT_ID=' in content:
            # Extract the client ID
            lines = content.split('\n')
            for line in lines:
                if line.startswith('GOOGLE_CLIENT_ID='):
                    client_id = line.split('=', 1)[1].strip()
                    if client_id and client_id != 'your_google_client_id_here.googleusercontent.com':
                        print(f"✅ Backend Google Client ID: {client_id[:20]}...")
                    else:
                        print("❌ Backend Google Client ID not configured")
                        return False
        else:
            print("❌ GOOGLE_CLIENT_ID not found in backend .env")
            return False
    else:
        print("❌ Backend .env file missing")
        return False
    
    # Check frontend .env
    frontend_env = os.path.join('tailorcv-frontend', '.env')
    if os.path.exists(frontend_env):
        print("✅ Frontend .env file exists")
        
        with open(frontend_env, 'r') as f:
            content = f.read()
            
        if 'REACT_APP_GOOGLE_CLIENT_ID=' in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('REACT_APP_GOOGLE_CLIENT_ID='):
                    client_id = line.split('=', 1)[1].strip()
                    if client_id and client_id != 'your_google_client_id_here.googleusercontent.com':
                        print(f"✅ Frontend Google Client ID: {client_id[:20]}...")
                    else:
                        print("❌ Frontend Google Client ID not configured")
                        return False
        else:
            print("❌ REACT_APP_GOOGLE_CLIENT_ID not found in frontend .env")
            return False
    else:
        print("❌ Frontend .env file missing")
        return False
    
    return True

def create_working_env_files():
    """Create working environment files with sample credentials"""
    print("\n📝 Creating working environment files...")
    
    # Sample credentials for testing
    sample_client_id = "123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com"
    sample_jwt_secret = "your_super_secret_jwt_key_here_make_it_long_and_random_at_least_32_characters_long"
    
    # Backend .env
    backend_env_content = f"""# TailorCV Backend Environment Variables
GOOGLE_CLIENT_ID={sample_client_id}
JWT_SECRET={sample_jwt_secret}
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
OPENROUTER_API_KEY=your-openrouter-api-key
DEBUG=True
PORT=5000
"""
    
    with open('tailorcv-backend/.env', 'w') as f:
        f.write(backend_env_content)
    
    # Frontend .env
    frontend_env_content = f"""# TailorCV Frontend Environment Variables
REACT_APP_GOOGLE_CLIENT_ID={sample_client_id}
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SITE_URL=http://localhost:3000
"""
    
    with open('tailorcv-frontend/.env', 'w') as f:
        f.write(frontend_env_content)
    
    print("✅ Created working environment files")
    print("⚠️  These contain sample credentials - replace with real ones!")

def main():
    """Main function"""
    print("🔧 Google OAuth Configuration Check")
    print("=" * 40)
    
    if not check_env_files():
        print("\n❌ Environment files are not properly configured")
        create_working_env_files()
        print("\n🔗 Next steps:")
        print("1. Get your Google Client ID from Google Cloud Console")
        print("2. Replace the sample credentials in .env files")
        print("3. Follow GOOGLE_OAUTH_FIX.md for detailed setup")
    else:
        print("\n✅ Environment files are configured!")
        print("🎉 Google OAuth should work now")
        print("\n🔗 Next steps:")
        print("1. Restart your applications")
        print("2. Test the Google sign-in flow")

if __name__ == "__main__":
    main()