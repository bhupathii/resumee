import re
from typing import Optional, List
from werkzeug.datastructures import FileStorage

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_linkedin_url(url: str) -> bool:
    """
    Validate LinkedIn URL format
    """
    if not url:
        return False
    
    linkedin_pattern = r'^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+/?$'
    return re.match(linkedin_pattern, url) is not None

def validate_file(file: FileStorage, 
                 allowed_types: Optional[List[str]] = None, 
                 max_size_mb: int = 10) -> bool:
    """
    Validate uploaded file
    """
    if not file or not file.filename:
        return False
    
    # Check file size
    if file.content_length and file.content_length > max_size_mb * 1024 * 1024:
        return False
    
    # Check file type
    if allowed_types:
        if file.content_type not in allowed_types:
            return False
    else:
        # Default allowed types for resumes
        default_allowed = ['application/pdf']
        if file.content_type not in default_allowed:
            return False
    
    return True

def validate_job_description(job_description: str) -> bool:
    """
    Validate job description content
    """
    if not job_description:
        return False
    
    # Check minimum length
    if len(job_description.strip()) < 100:
        return False
    
    # Check maximum length
    if len(job_description) > 10000:
        return False
    
    return True

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and other issues
    """
    if not text:
        return ""
    
    # Remove dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Limit length
    if len(text) > 10000:
        text = text[:10000]
    
    return text.strip()

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    """
    if not phone:
        return False
    
    # Remove common formatting characters
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # Check if it's a valid length
    if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
        return False
    
    return True

def validate_url(url: str) -> bool:
    """
    Validate URL format
    """
    if not url:
        return False
    
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(url_pattern, url) is not None

def validate_name(name: str) -> bool:
    """
    Validate person name
    """
    if not name:
        return False
    
    # Check length
    if len(name.strip()) < 2 or len(name) > 100:
        return False
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    name_pattern = r"^[a-zA-Z\s\-'\.]+$"
    return re.match(name_pattern, name) is not None

def validate_location(location: str) -> bool:
    """
    Validate location string
    """
    if not location:
        return False
    
    # Check length
    if len(location.strip()) < 2 or len(location) > 200:
        return False
    
    # Check for reasonable characters
    location_pattern = r"^[a-zA-Z0-9\s\-,\.]+$"
    return re.match(location_pattern, location) is not None

def validate_skill(skill: str) -> bool:
    """
    Validate individual skill
    """
    if not skill:
        return False
    
    # Check length
    if len(skill.strip()) < 1 or len(skill) > 50:
        return False
    
    # Check for valid characters
    skill_pattern = r"^[a-zA-Z0-9\s\-\+\#\.]+$"
    return re.match(skill_pattern, skill) is not None

def validate_company_name(company: str) -> bool:
    """
    Validate company name
    """
    if not company:
        return False
    
    # Check length
    if len(company.strip()) < 2 or len(company) > 100:
        return False
    
    # Check for valid characters
    company_pattern = r"^[a-zA-Z0-9\s\-\.,&]+$"
    return re.match(company_pattern, company) is not None

def validate_date(date_str: str) -> bool:
    """
    Validate date format (MM/YYYY or YYYY)
    """
    if not date_str:
        return False
    
    # Handle "Present" case
    if date_str.lower() == 'present':
        return True
    
    # Check MM/YYYY format
    date_pattern1 = r'^\d{2}/\d{4}$'
    if re.match(date_pattern1, date_str):
        return True
    
    # Check YYYY format
    date_pattern2 = r'^\d{4}$'
    if re.match(date_pattern2, date_str):
        return True
    
    return False

def validate_gpa(gpa: str) -> bool:
    """
    Validate GPA format
    """
    if not gpa:
        return True  # GPA is optional
    
    try:
        gpa_float = float(gpa)
        return 0.0 <= gpa_float <= 4.0
    except ValueError:
        return False

def validate_resume_data(resume_data: dict) -> tuple[bool, str]:
    """
    Validate complete resume data structure
    """
    try:
        # Check required fields
        required_fields = ['personalInfo', 'summary', 'skills', 'experience', 'education']
        for field in required_fields:
            if field not in resume_data:
                return False, f"Missing required field: {field}"
        
        # Validate personal info
        personal_info = resume_data['personalInfo']
        if not validate_name(personal_info.get('name', '')):
            return False, "Invalid name format"
        
        if not validate_email(personal_info.get('email', '')):
            return False, "Invalid email format"
        
        # Validate skills
        skills = resume_data['skills']
        if not isinstance(skills, list) or len(skills) == 0:
            return False, "Skills must be a non-empty list"
        
        for skill in skills:
            if not validate_skill(skill):
                return False, f"Invalid skill: {skill}"
        
        # Validate experience
        experience = resume_data['experience']
        if not isinstance(experience, list):
            return False, "Experience must be a list"
        
        for exp in experience:
            if not validate_company_name(exp.get('company', '')):
                return False, f"Invalid company name: {exp.get('company', '')}"
        
        return True, "Valid resume data"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"