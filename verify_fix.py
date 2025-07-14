#!/usr/bin/env python3
"""
Verify that the PDF generation fix works
"""
import os
import sys

def test_pdf_generation():
    """Test that PDF generation works without LaTeX"""
    try:
        # Add the backend directory to Python path
        sys.path.append(os.path.join(os.getcwd(), 'tailorcv-backend'))
        
        # Test sample resume data
        sample_data = {
            "personalInfo": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "location": "San Francisco, CA"
            },
            "summary": "Experienced software developer with 5+ years in full-stack development. Skilled in Python, JavaScript, and modern web technologies.",
            "skills": [
                "Python", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Docker", "AWS"
            ],
            "experience": [
                {
                    "title": "Senior Software Developer",
                    "company": "Tech Corp",
                    "startDate": "2021",
                    "endDate": "Present",
                    "description": [
                        "Led development of microservices architecture serving 1M+ users",
                        "Improved system performance by 40% through optimization",
                        "Mentored 5 junior developers and conducted code reviews"
                    ]
                },
                {
                    "title": "Full Stack Developer",
                    "company": "StartupXYZ",
                    "startDate": "2019",
                    "endDate": "2021",
                    "description": [
                        "Built responsive web applications using React and Node.js",
                        "Implemented RESTful APIs and database design",
                        "Collaborated with design team to improve user experience"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of California, Berkeley",
                    "startDate": "2015",
                    "endDate": "2019",
                    "gpa": "3.8"
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack e-commerce solution with payment integration",
                    "technologies": ["React", "Node.js", "MongoDB", "Stripe"]
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Developer",
                    "issuer": "Amazon",
                    "date": "2023"
                }
            ]
        }
        
        # Test ReportLab PDF generation
        from tailorcv_backend.services.pdf_fallback_service import PDFFallbackService
        
        pdf_service = PDFFallbackService()
        
        # Generate free version
        print("🔄 Generating free version PDF...")
        free_pdf = pdf_service.generate_pdf(sample_data, is_premium=False)
        
        if free_pdf and len(free_pdf) > 0:
            with open('test_resume_free.pdf', 'wb') as f:
                f.write(free_pdf)
            print(f"✅ Free PDF generated successfully ({len(free_pdf)} bytes)")
            print("   Saved as: test_resume_free.pdf")
        else:
            print("❌ Free PDF generation failed")
            return False
        
        # Generate premium version
        print("🔄 Generating premium version PDF...")
        premium_pdf = pdf_service.generate_pdf(sample_data, is_premium=True)
        
        if premium_pdf and len(premium_pdf) > 0:
            with open('test_resume_premium.pdf', 'wb') as f:
                f.write(premium_pdf)
            print(f"✅ Premium PDF generated successfully ({len(premium_pdf)} bytes)")
            print("   Saved as: test_resume_premium.pdf")
        else:
            print("❌ Premium PDF generation failed")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Verifying PDF Generation Fix")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('tailorcv-backend'):
        print("❌ Please run this script from the project root directory")
        return
    
    # Test PDF generation
    if test_pdf_generation():
        print("\n✅ PDF generation fix verified successfully!")
        print("🎉 The resume generation should now work without LaTeX errors")
        print("\n📋 Next steps:")
        print("1. Deploy the updated code to your production environment")
        print("2. Ensure ReportLab is installed on the production server")
        print("3. Test the complete user flow from sign-in to PDF generation")
    else:
        print("\n❌ PDF generation fix verification failed")
        print("🔧 Please check the error messages above")

if __name__ == "__main__":
    main()