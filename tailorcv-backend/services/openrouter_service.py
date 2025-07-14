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
            "mistralai/mistral-7b-instruct:free",
            "huggingface/microsoft/DialoGPT-medium:free", 
            "google/gemma-7b-it:free",
            "meta-llama/llama-3-8b-instruct:free"
        ]
        self.model = self.models[0]  # Default to first available
        
    def optimize_resume(self, resume_data: str, job_description: str) -> Dict[str, Any]:
        """
        Use OpenRouter API to optimize resume content based on job description
        """
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
            
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
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error calling OpenRouter API: {str(e)}")
    
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