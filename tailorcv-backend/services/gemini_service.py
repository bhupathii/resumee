import os
import json
import requests
from typing import Dict, Any

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
    def optimize_resume(self, resume_data: str, job_description: str) -> Dict[str, Any]:
        """
        Use Gemini API to optimize resume content based on job description
        """
        if not self.api_key or self.api_key == "your-gemini-api-key":
            print("WARNING: Gemini API key not configured. Using mock data for testing.")
            return self._get_mock_resume_data()
            
        prompt = self._create_optimization_prompt(resume_data, job_description)
        
        try:
            response = self._call_gemini_api(prompt)
            return self._parse_gemini_response(response)
        except Exception as e:
            print(f"Gemini API call failed: {str(e)}")
            print("Falling back to mock data...")
            return self._get_mock_resume_data()
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Make API call to Gemini
        """
        url = f"{self.base_url}?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 4000,
            }
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Gemini API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        
        if 'candidates' not in data or not data['candidates']:
            raise Exception("No candidates in Gemini response")
        
        if 'content' not in data['candidates'][0] or 'parts' not in data['candidates'][0]['content']:
            raise Exception("Invalid response structure from Gemini")
        
        return data['candidates'][0]['content']['parts'][0]['text']
    
    def _create_optimization_prompt(self, resume_data: str, job_description: str) -> str:
        """
        Create optimized prompt for Gemini
        """
        return f"""You are an expert resume writer and ATS optimization specialist. Your task is to optimize a resume for a specific job description while maintaining accuracy and professionalism.

RESUME DATA:
{resume_data}

JOB DESCRIPTION:
{job_description}

Please create an optimized resume that:
1. Highlights relevant skills and experience for this specific job
2. Uses keywords from the job description naturally
3. Maintains truthfulness about the candidate's background
4. Follows ATS-friendly formatting
5. Creates compelling bullet points that show impact and results

Return your response as a JSON object with the following structure:
{{
    "personalInfo": {{
        "name": "Candidate Name",
        "email": "email@example.com",
        "phone": "+1234567890",
        "location": "City, State",
        "linkedin": "linkedin.com/in/profile",
        "github": "github.com/username",
        "website": "portfolio-website.com"
    }},
    "summary": "A compelling 2-3 sentence professional summary that highlights key qualifications for this role",
    "skills": [
        "Relevant technical skills",
        "Programming languages",
        "Frameworks and tools",
        "Soft skills relevant to the job"
    ],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, State",
            "startDate": "MM/YYYY",
            "endDate": "MM/YYYY or Present",
            "description": [
                "Achievement-focused bullet point with quantifiable results",
                "Another accomplishment that relates to the target job",
                "Technical implementation or leadership example"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University Name",
            "location": "City, State",
            "startDate": "MM/YYYY",
            "endDate": "MM/YYYY",
            "gpa": "3.X" (if mentioned and above 3.5),
            "relevantCourses": ["Course 1", "Course 2"] (if relevant)
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description highlighting technologies and impact",
            "technologies": ["Tech1", "Tech2", "Tech3"],
            "date": "MM/YYYY",
            "github": "github.com/repo-link",
            "link": "live-demo-link.com"
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "MM/YYYY",
            "link": "credential-link.com"
        }}
    ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini's response and extract JSON
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['personalInfo', 'summary', 'skills', 'experience']
            for field in required_fields:
                if field not in parsed_data:
                    print(f"Warning: Missing required field '{field}', using fallback")
                    return self._get_mock_resume_data()
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from Gemini response: {e}")
            print(f"Response text: {response_text[:500]}...")
            return self._get_mock_resume_data()
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._get_mock_resume_data()
    
    def _get_mock_resume_data(self) -> Dict[str, Any]:
        """
        Provide mock resume data for testing when API is unavailable
        """
        return {
            "personalInfo": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1 (555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/johndoe",
                "github": "github.com/johndoe",
                "website": "johndoe.dev"
            },
            "summary": "Experienced Software Engineer with 3+ years of expertise in full-stack development, specializing in React, Python, and cloud technologies. Proven track record of building scalable web applications and optimizing system performance.",
            "skills": [
                "JavaScript/TypeScript",
                "React.js",
                "Python",
                "Node.js",
                "SQL/NoSQL Databases",
                "AWS/Cloud Services",
                "Git/Version Control",
                "Agile/Scrum Methodologies"
            ],
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Innovations Inc.",
                    "location": "San Francisco, CA",
                    "startDate": "01/2022",
                    "endDate": "Present",
                    "description": [
                        "Developed and maintained 5+ web applications using React and Python, serving 10,000+ daily active users",
                        "Optimized database queries resulting in 40% improvement in application response time",
                        "Collaborated with cross-functional teams to deliver features ahead of schedule in Agile environment"
                    ]
                },
                {
                    "title": "Junior Developer",
                    "company": "StartupXYZ",
                    "location": "Palo Alto, CA",
                    "startDate": "06/2021",
                    "endDate": "12/2021",
                    "description": [
                        "Built responsive web interfaces using React and modern CSS frameworks",
                        "Implemented RESTful APIs using Python Flask framework",
                        "Participated in code reviews and maintained 95%+ test coverage"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of California, Berkeley",
                    "location": "Berkeley, CA",
                    "startDate": "08/2017",
                    "endDate": "05/2021",
                    "gpa": "3.7",
                    "relevantCourses": ["Data Structures", "Algorithms", "Web Development", "Database Systems"]
                }
            ],
            "projects": [
                {
                    "name": "E-Commerce Platform",
                    "description": "Full-stack e-commerce application with payment integration and inventory management",
                    "technologies": ["React", "Node.js", "MongoDB", "Stripe API"],
                    "date": "03/2021",
                    "github": "github.com/johndoe/ecommerce-platform",
                    "link": "ecommerce-demo.johndoe.dev"
                },
                {
                    "name": "Task Management App",
                    "description": "Collaborative task management tool with real-time updates and team collaboration features",
                    "technologies": ["Python", "Flask", "PostgreSQL", "WebSocket"],
                    "date": "11/2020",
                    "github": "github.com/johndoe/task-manager",
                    "link": "tasks.johndoe.dev"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Developer Associate",
                    "issuer": "Amazon Web Services",
                    "date": "09/2022",
                    "link": "aws.amazon.com/certification"
                }
            ]
        }
    
    def test_connection(self) -> bool:
        """
        Test if Gemini API is accessible and working
        """
        if not self.api_key or self.api_key == "your-gemini-api-key":
            return False
        
        try:
            response = self._call_gemini_api("Hello, this is a test. Please respond with 'Hello back!'")
            return "hello" in response.lower()
        except Exception as e:
            print(f"Gemini connection test failed: {e}")
            return False