import os
import json
import requests
from typing import Dict, Any

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Check if running in demo mode (for local development)
        self.demo_mode = (
            self.api_key == "test-gemini-key-for-local-development" or
            os.environ.get('DEBUG') == 'True' and self.api_key == "your-gemini-api-key"
        )
        
        # Validate API key is configured (unless in demo mode)
        if not self.demo_mode and (not self.api_key or self.api_key == "your-gemini-api-key"):
            raise Exception("GEMINI_API_KEY environment variable is required and must be set to a valid API key")
        
    def optimize_resume(self, resume_data: str, job_description: str) -> Dict[str, Any]:
        """
        Use Gemini API to optimize resume content based on job description
        """
        # If in demo mode, return structured demo data
        if self.demo_mode:
            return self._get_demo_resume_data(resume_data, job_description)
            
        prompt = self._create_optimization_prompt(resume_data, job_description)
        response = self._call_gemini_api(prompt)
        return self._parse_gemini_response(response)
    
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
                raise ValueError(f"No JSON found in Gemini response. Response: {response_text[:200]}...")
            
            json_str = response_text[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['personalInfo', 'summary', 'skills', 'experience']
            missing_fields = [field for field in required_fields if field not in parsed_data]
            if missing_fields:
                raise ValueError(f"Gemini response missing required fields: {missing_fields}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON from Gemini response: {e}. Response: {response_text[:500]}...")
        except Exception as e:
            raise Exception(f"Error parsing Gemini response: {e}")
    
    def _get_demo_resume_data(self, resume_data: str, job_description: str) -> Dict[str, Any]:
        """
        Generate demo resume data for local development/testing
        """
        return {
            "personalInfo": {
                "name": "Alex Johnson",
                "email": "alex.johnson@email.com",
                "phone": "+1 (555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/alexjohnson",
                "github": "github.com/alexjohnson",
                "website": "alexjohnson.dev"
            },
            "summary": f"Experienced professional optimized for {job_description.lower()} with proven expertise in web development, programming, and technology solutions. Skilled in modern development practices and committed to delivering high-quality results.",
            "skills": [
                "JavaScript/TypeScript",
                "React.js & Next.js",
                "Python & Flask",
                "Node.js",
                "SQL/NoSQL Databases",
                "Git/Version Control",
                "HTML/CSS",
                "API Development",
                "Problem Solving",
                "Team Collaboration"
            ],
            "experience": [
                {
                    "title": "Software Developer",
                    "company": "Tech Solutions Inc.",
                    "location": "San Francisco, CA",
                    "startDate": "01/2022",
                    "endDate": "Present",
                    "description": [
                        "Developed web applications using React and Python, serving thousands of users daily",
                        "Collaborated with cross-functional teams to deliver features on schedule",
                        "Implemented responsive designs and optimized application performance",
                        "Participated in code reviews and maintained high code quality standards"
                    ]
                },
                {
                    "title": "Junior Developer",
                    "company": "Digital Agency",
                    "location": "San Francisco, CA", 
                    "startDate": "06/2021",
                    "endDate": "12/2021",
                    "description": [
                        "Built responsive web interfaces using modern frontend technologies",
                        "Worked on API integration and database management",
                        "Supported senior developers in project planning and execution"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of California, San Francisco",
                    "location": "San Francisco, CA",
                    "startDate": "08/2017",
                    "endDate": "05/2021",
                    "gpa": "3.8",
                    "relevantCourses": ["Data Structures", "Algorithms", "Web Development", "Software Engineering"]
                }
            ],
            "projects": [
                {
                    "name": "Resume Builder Application",
                    "description": "Full-stack web application for creating professional resumes with AI optimization",
                    "technologies": ["React", "Python", "Flask", "PostgreSQL"],
                    "date": "2023",
                    "github": "github.com/alexjohnson/resume-builder",
                    "link": "resume-builder.alexjohnson.dev"
                },
                {
                    "name": "Task Management System",
                    "description": "Collaborative task management tool with real-time updates and team features",
                    "technologies": ["JavaScript", "Node.js", "MongoDB", "Socket.io"],
                    "date": "2022",
                    "github": "github.com/alexjohnson/task-manager",
                    "link": "tasks.alexjohnson.dev"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Developer Associate",
                    "issuer": "Amazon Web Services",
                    "date": "10/2023",
                    "link": "aws.amazon.com/certification"
                }
            ]
        }
    
    def test_connection(self) -> bool:
        """
        Test if Gemini API is accessible and working
        """
        if not self.api_key or self.api_key == "your-gemini-api-key":
            raise Exception("Gemini API key is required for testing connection.")
        
        try:
            response = self._call_gemini_api("Hello, this is a test. Please respond with 'Hello back!'")
            return "hello" in response.lower()
        except Exception as e:
            raise Exception(f"Gemini connection test failed: {e}")