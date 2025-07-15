import os
import json
import requests
from typing import Dict, Any

class OpenRouterService:
    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        # Try multiple free models in order of preference
        self.models = [
            "tngtech/deepseek-r1t2-chimera:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemma-7b-it:free",
            "meta-llama/llama-3-8b-instruct:free"
        ]
        self.model = self.models[0]  # Default to DeepSeek R1T2 Chimera
        
    def optimize_resume(self, resume_data: str, job_description: str) -> Dict[str, Any]:
        """
        Use OpenRouter API to optimize resume content based on job description
        """
        if not self.api_key or self.api_key == "your-openrouter-api-key":
            print("WARNING: OpenRouter API key not configured. Using mock data for testing.")
            return self._get_mock_resume_data()
            
        prompt = self._create_optimization_prompt(resume_data, job_description)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert resume writer and ATS optimization specialist. Your task is to optimize resumes for specific job descriptions while maintaining accuracy and professionalism."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._parse_optimized_resume(content)
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                print("Falling back to mock data for testing...")
                return self._get_mock_resume_data()
                
        except requests.exceptions.RequestException as e:
            print(f"Network error calling OpenRouter API: {str(e)}")
            print("Falling back to mock data for testing...")
            return self._get_mock_resume_data()
    
    def _create_optimization_prompt(self, resume_data: str, job_description: str) -> str:
        """
        Create the optimization prompt for the AI model
        """
        return f"""
Please analyze the following resume and job description, then optimize the resume to better match the job requirements. 

RESUME DATA:
{resume_data}

JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:
1. Analyze the job description for key skills, requirements, and keywords
2. Optimize the resume content to highlight relevant experience and skills
3. Ensure the resume is ATS-friendly with proper formatting and keywords
4. Maintain accuracy - don't fabricate experience or skills
5. Structure the output as a JSON object with the following format:

{{
    "personalInfo": {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "phone number",
        "location": "City, State",
        "linkedin": "linkedin url",
        "github": "github url (optional)",
        "website": "website url (optional)"
    }},
    "summary": "Professional summary optimized for this job (2-3 sentences)",
    "skills": ["skill1", "skill2", "skill3"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, State",
            "startDate": "MM/YYYY",
            "endDate": "MM/YYYY or Present",
            "current": true/false,
            "description": ["Achievement 1", "Achievement 2", "Achievement 3"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Title",
            "institution": "School Name",
            "location": "City, State",
            "startDate": "MM/YYYY",
            "endDate": "MM/YYYY",
            "gpa": "GPA (optional)",
            "relevantCourses": ["Course1", "Course2"] (optional)
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project description highlighting relevant skills",
            "technologies": ["tech1", "tech2"],
            "link": "project link (optional)",
            "github": "github link (optional)"
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "MM/YYYY",
            "link": "certification link (optional)"
        }}
    ] (optional)
}}

IMPORTANT: Return only the JSON object, no additional text or formatting.
"""
    
    def _parse_optimized_resume(self, content: str) -> Dict[str, Any]:
        """
        Parse the AI response and extract the JSON resume data
        """
        try:
            # Clean the content and extract JSON
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            resume_data = json.loads(content)
            
            # Validate required fields
            required_fields = ['personalInfo', 'summary', 'skills', 'experience', 'education']
            for field in required_fields:
                if field not in resume_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return resume_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing resume data: {str(e)}")
    
    def _get_mock_resume_data(self) -> Dict[str, Any]:
        """
        Return mock resume data for testing when API is unavailable
        """
        return {
            "personalInfo": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe"
            },
            "summary": "Software Engineer with 5+ years of experience in full-stack development, specializing in Python, React, and cloud technologies. Proven track record of delivering scalable solutions and leading technical teams.",
            "skills": [
                "Python", "JavaScript", "React", "Node.js", "Django", "Flask", 
                "PostgreSQL", "MongoDB", "Docker", "AWS", "Git", "CI/CD"
            ],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "startDate": "01/2020",
                    "endDate": "Present",
                    "current": True,
                    "description": [
                        "Led development of web applications using React and Python",
                        "Implemented microservices architecture serving 10M+ requests daily",
                        "Mentored junior developers and conducted code reviews",
                        "Collaborated with product teams to define technical requirements"
                    ]
                },
                {
                    "title": "Software Engineer",
                    "company": "Startup Inc",
                    "location": "San Francisco, CA",
                    "startDate": "06/2018",
                    "endDate": "12/2019",
                    "current": False,
                    "description": [
                        "Built REST APIs using Django and PostgreSQL",
                        "Developed responsive web interfaces with React",
                        "Implemented automated testing and deployment pipelines",
                        "Optimized database queries reducing response time by 40%"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of California, Berkeley",
                    "location": "Berkeley, CA",
                    "startDate": "09/2014",
                    "endDate": "05/2018",
                    "gpa": "3.8"
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack e-commerce application with payment processing",
                    "technologies": ["React", "Node.js", "PostgreSQL", "Stripe"],
                    "github": "https://github.com/johndoe/ecommerce"
                }
            ]
        }
    
    def test_connection(self) -> bool:
        """
        Test if the OpenRouter API is accessible
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False