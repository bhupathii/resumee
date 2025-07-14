import PyPDF2
import io
from typing import Dict, Any
from werkzeug.datastructures import FileStorage

class PDFService:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_file: FileStorage) -> str:
        """
        Extract text content from uploaded PDF resume
        """
        try:
            # Read the PDF file
            pdf_content = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            # Extract text from all pages
            extracted_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                extracted_text += text + "\n"
            
            if not extracted_text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            # Clean and format the extracted text
            formatted_text = self._clean_extracted_text(extracted_text)
            
            return formatted_text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and format extracted text for better AI processing
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Format for AI processing
        formatted_text = f"""
RESUME CONTENT FROM PDF:

{cleaned_text}

END OF RESUME CONTENT
"""
        
        return formatted_text
    
    def validate_pdf_file(self, pdf_file: FileStorage) -> bool:
        """
        Validate that the uploaded file is a valid PDF
        """
        try:
            # Check file extension
            if not pdf_file.filename.lower().endswith('.pdf'):
                return False
            
            # Check MIME type
            if pdf_file.content_type != 'application/pdf':
                return False
            
            # Try to read the PDF
            pdf_content = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            # Check if PDF has pages
            if len(pdf_reader.pages) == 0:
                return False
            
            # Try to extract text from first page to ensure it's readable
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            return True
            
        except Exception:
            return False
    
    def get_pdf_metadata(self, pdf_file: FileStorage) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        """
        try:
            pdf_content = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            metadata = {
                'page_count': len(pdf_reader.pages),
                'file_size': len(pdf_content),
                'filename': pdf_file.filename
            }
            
            # Try to get PDF metadata
            if pdf_reader.metadata:
                metadata.update({
                    'title': pdf_reader.metadata.get('/Title', 'Unknown'),
                    'author': pdf_reader.metadata.get('/Author', 'Unknown'),
                    'creator': pdf_reader.metadata.get('/Creator', 'Unknown'),
                    'producer': pdf_reader.metadata.get('/Producer', 'Unknown'),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', 'Unknown'),
                    'modification_date': pdf_reader.metadata.get('/ModDate', 'Unknown')
                })
            
            return metadata
            
        except Exception as e:
            return {
                'error': f"Failed to extract metadata: {str(e)}",
                'filename': pdf_file.filename,
                'file_size': 0,
                'page_count': 0
            }
    
    def extract_structured_data(self, pdf_file: FileStorage) -> Dict[str, Any]:
        """
        Attempt to extract structured data from resume PDF
        This is a basic implementation - in production, you'd use more sophisticated NLP
        """
        try:
            text = self.extract_text_from_pdf(pdf_file)
            
            # Basic extraction patterns
            structured_data = {
                'raw_text': text,
                'sections': self._identify_sections(text),
                'contact_info': self._extract_contact_info(text),
                'skills': self._extract_skills(text),
                'experience': self._extract_experience_keywords(text),
                'education': self._extract_education_keywords(text)
            }
            
            return structured_data
            
        except Exception as e:
            return {'error': f"Failed to extract structured data: {str(e)}"}
    
    def _identify_sections(self, text: str) -> Dict[str, int]:
        """
        Identify common resume sections
        """
        sections = {}
        section_keywords = {
            'summary': ['summary', 'objective', 'profile'],
            'experience': ['experience', 'employment', 'work history', 'professional experience'],
            'education': ['education', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'competencies'],
            'projects': ['projects', 'portfolio'],
            'certifications': ['certifications', 'certificates', 'licenses']
        }
        
        text_lower = text.lower()
        
        for section, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    sections[section] = text_lower.find(keyword)
                    break
        
        return sections
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract contact information using basic regex patterns
        """
        import re
        
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone pattern
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{10,}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9\-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        return contact_info
    
    def _extract_skills(self, text: str) -> list:
        """
        Extract skills using keyword matching
        """
        # Common technical skills
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'express', 'django', 'flask', 'spring', 'sql', 'mysql',
            'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'gcp', 'docker',
            'kubernetes', 'jenkins', 'git', 'html', 'css', 'bootstrap', 'tailwind',
            'machine learning', 'data science', 'artificial intelligence', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'spark', 'hadoop'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience_keywords(self, text: str) -> list:
        """
        Extract experience-related keywords
        """
        experience_keywords = [
            'managed', 'led', 'developed', 'implemented', 'designed', 'created',
            'built', 'architected', 'optimized', 'improved', 'increased', 'reduced',
            'collaborated', 'coordinated', 'mentored', 'supervised', 'trained'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in experience_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_education_keywords(self, text: str) -> list:
        """
        Extract education-related keywords
        """
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'institute', 'school', 'gpa', 'graduated', 'major', 'minor',
            'computer science', 'engineering', 'business', 'mathematics'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in education_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords