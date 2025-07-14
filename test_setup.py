#!/usr/bin/env python3
"""
Test script to verify TailorCV setup and functionality
"""
import os
import sys
import subprocess
import json

def test_environment():
    """Test environment variables and configuration"""
    print("🔍 Testing Environment Configuration...")
    
    # Check if we're in the right directory
    required_files = [
        'tailorcv-backend/app.py', 
        'tailorcv-frontend/package.json',
        'GOOGLE_AUTH_SETUP.md'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return False
        print(f"✅ Found: {file}")
    
    return True

def test_backend_dependencies():
    """Test backend Python dependencies"""
    print("\n📦 Testing Backend Dependencies...")
    
    try:
        # Change to backend directory
        os.chdir('tailorcv-backend')
        
        # Test critical imports
        test_imports = [
            'flask',
            'flask_cors',
            'google.oauth2.id_token',
            'google.auth.transport.requests',
            'services.auth_service',
            'services.latex_service',
            'services.pdf_fallback_service',
            'reportlab.lib.pagesizes'
        ]
        
        for module in test_imports:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError as e:
                print(f"❌ {module} - {e}")
                if module == 'reportlab.lib.pagesizes':
                    print("   Try: pip install reportlab")
                elif 'services.' in module:
                    print(f"   Custom module - check if file exists")
        
        # Test PDF generation
        try:
            from services.latex_service import LaTeXService
            from services.pdf_fallback_service import PDFFallbackService
            
            latex_service = LaTeXService()
            latex_available = latex_service.validate_latex_installation()
            
            print(f"📄 LaTeX Available: {'✅ Yes' if latex_available else '❌ No (will use fallback)'}")
            
            # Test fallback service
            fallback_service = PDFFallbackService()
            print("✅ PDF Fallback Service ready")
            
        except Exception as e:
            print(f"❌ PDF Services error: {e}")
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    finally:
        os.chdir('..')
    
    return True

def test_google_oauth_config():
    """Test Google OAuth configuration"""
    print("\n🔐 Testing Google OAuth Configuration...")
    
    # Check backend environment
    backend_env = os.path.join('tailorcv-backend', '.env')
    if os.path.exists(backend_env):
        print("✅ Backend .env file exists")
        with open(backend_env, 'r') as f:
            content = f.read()
            if 'GOOGLE_CLIENT_ID' in content:
                print("✅ GOOGLE_CLIENT_ID configured")
            else:
                print("❌ GOOGLE_CLIENT_ID not found in .env")
    else:
        print("❌ Backend .env file missing")
        print("   Create tailorcv-backend/.env with GOOGLE_CLIENT_ID")
    
    # Check frontend environment
    frontend_env = os.path.join('tailorcv-frontend', '.env')
    if os.path.exists(frontend_env):
        print("✅ Frontend .env file exists")
        with open(frontend_env, 'r') as f:
            content = f.read()
            if 'REACT_APP_GOOGLE_CLIENT_ID' in content:
                print("✅ REACT_APP_GOOGLE_CLIENT_ID configured")
            else:
                print("❌ REACT_APP_GOOGLE_CLIENT_ID not found in .env")
    else:
        print("❌ Frontend .env file missing")
        print("   Create tailorcv-frontend/.env with REACT_APP_GOOGLE_CLIENT_ID")

def create_sample_env_files():
    """Create sample environment files"""
    print("\n📝 Creating sample environment files...")
    
    # Backend .env sample
    backend_env_sample = """# Backend Environment Variables
GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com
JWT_SECRET=your_super_secret_jwt_key_here_make_it_long_and_random
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENROUTER_API_KEY=your_openrouter_key
DEBUG=True
"""
    
    # Frontend .env sample
    frontend_env_sample = """# Frontend Environment Variables
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
"""
    
    # Create backend .env if it doesn't exist
    backend_env_path = os.path.join('tailorcv-backend', '.env.sample')
    with open(backend_env_path, 'w') as f:
        f.write(backend_env_sample)
    print(f"✅ Created {backend_env_path}")
    
    # Create frontend .env if it doesn't exist
    frontend_env_path = os.path.join('tailorcv-frontend', '.env.sample')
    with open(frontend_env_path, 'w') as f:
        f.write(frontend_env_sample)
    print(f"✅ Created {frontend_env_path}")
    
    print("\n🔧 To complete setup:")
    print("1. Copy .env.sample to .env in both directories")
    print("2. Fill in your actual Google Client ID and other credentials")
    print("3. Follow the GOOGLE_AUTH_SETUP.md guide")

def test_sample_resume_generation():
    """Test sample resume generation"""
    print("\n📄 Testing Sample Resume Generation...")
    
    sample_resume_data = {
        "personalInfo": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA"
        },
        "summary": "Experienced software developer with 5+ years in full-stack development.",
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "SQL"
        ],
        "experience": [
            {
                "title": "Senior Software Developer",
                "company": "Tech Corp",
                "startDate": "2021",
                "endDate": "Present",
                "description": [
                    "Led development of microservices architecture",
                    "Improved system performance by 40%",
                    "Mentored junior developers"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of California",
                "startDate": "2017",
                "endDate": "2021"
            }
        ]
    }
    
    try:
        os.chdir('tailorcv-backend')
        
        from services.latex_service import LaTeXService
        latex_service = LaTeXService()
        
        # Test PDF generation
        pdf_bytes = latex_service.generate_pdf(sample_resume_data, is_premium=False)
        
        if pdf_bytes and len(pdf_bytes) > 0:
            print("✅ PDF generation successful")
            print(f"   Generated PDF size: {len(pdf_bytes)} bytes")
            
            # Save sample PDF
            with open('sample_resume.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("✅ Sample resume saved as sample_resume.pdf")
            
        else:
            print("❌ PDF generation failed - empty result")
            
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        print("   This is expected if LaTeX is not installed - fallback should work")
    finally:
        os.chdir('..')

def main():
    """Main test function"""
    print("🚀 TailorCV Setup and Functionality Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_environment,
        test_backend_dependencies,
        test_google_oauth_config,
        test_sample_resume_generation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    # Create sample environment files
    create_sample_env_files()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"   Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! TailorCV is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   Most likely issues:")
        print("   1. Missing environment variables (.env files)")
        print("   2. Missing Python dependencies (run: pip install -r requirements.txt)")
        print("   3. LaTeX not installed (fallback PDF generation should work)")
    
    print("\n🔗 Next steps:")
    print("1. Set up Google OAuth credentials following GOOGLE_AUTH_SETUP.md")
    print("2. Configure environment variables in .env files")
    print("3. Run backend: cd tailorcv-backend && python app.py")
    print("4. Run frontend: cd tailorcv-frontend && npm start")

if __name__ == "__main__":
    main()