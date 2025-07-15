import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any
from urllib.parse import urlparse

class LinkedInService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_profile_data(self, linkedin_url: str) -> str:
        """
        Extract profile data from LinkedIn URL
        Note: This is a simplified implementation. In production, you'd use LinkedIn's API
        or a more sophisticated scraping approach with proper rate limiting.
        """
        if not self._is_valid_linkedin_url(linkedin_url):
            raise ValueError("Invalid LinkedIn URL format")
        
        try:
            # For demo purposes, we'll return a structured format
            # that can be parsed by the AI model
            return self._scrape_public_profile(linkedin_url)
            
        except Exception as e:
            print(f"LinkedIn extraction failed: {str(e)}")
            # Return fallback data for testing
            return self._get_fallback_format(linkedin_url)
    
    def _is_valid_linkedin_url(self, url: str) -> bool:
        """
        Validate LinkedIn URL format
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc in ['linkedin.com', 'www.linkedin.com'] and
                '/in/' in parsed.path
            )
        except Exception:
            return False
    
    def _scrape_public_profile(self, url: str) -> str:
        """
        Scrape public LinkedIn profile information
        Note: This is a simplified implementation for demo purposes
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            profile_data = {
                'name': self._extract_name(soup),
                'headline': self._extract_headline(soup),
                'location': self._extract_location(soup),
                'about': self._extract_about(soup),
                'experience': self._extract_experience(soup),
                'education': self._extract_education(soup),
                'skills': self._extract_skills(soup)
            }
            
            # Convert to text format for AI processing
            return self._format_profile_data(profile_data)
            
        except requests.RequestException as e:
            # If scraping fails, return a template format
            return self._get_fallback_format(url)
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract name from LinkedIn profile"""
        try:
            name_selectors = [
                'h1.text-heading-xlarge',
                'h1.pv-text-details__left-panel-title',
                'h1[data-generated-suggestion-target]'
            ]
            
            for selector in name_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            
            return "Name not found"
        except Exception:
            return "Name not found"
    
    def _extract_headline(self, soup: BeautifulSoup) -> str:
        """Extract headline from LinkedIn profile"""
        try:
            headline_selectors = [
                '.text-body-medium.break-words',
                '.pv-text-details__left-panel-subtitle',
                '.text-body-medium'
            ]
            
            for selector in headline_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            
            return "Headline not found"
        except Exception:
            return "Headline not found"
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location from LinkedIn profile"""
        try:
            location_selectors = [
                '.text-body-small.inline.t-black--light.break-words',
                '.pv-text-details__left-panel-subtitle'
            ]
            
            for selector in location_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if any(keyword in text.lower() for keyword in ['city', 'state', 'country', ',']):
                        return text
            
            return "Location not found"
        except Exception:
            return "Location not found"
    
    def _extract_about(self, soup: BeautifulSoup) -> str:
        """Extract about section from LinkedIn profile"""
        try:
            about_selectors = [
                '.pv-about-section .pv-about__summary-text',
                '.pv-about__summary-text',
                '.inline-show-more-text'
            ]
            
            for selector in about_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            
            return "About section not found"
        except Exception:
            return "About section not found"
    
    def _extract_experience(self, soup: BeautifulSoup) -> list:
        """Extract experience from LinkedIn profile"""
        try:
            # This is a simplified extraction
            experience_data = []
            
            # Look for experience section
            experience_sections = soup.select('.pv-profile-section.experience-section')
            
            if experience_sections:
                # Extract experience items
                for item in experience_sections[0].select('.pv-entity__position-group-pager'):
                    job_title = item.select_one('.t-16.t-black.t-bold')
                    company = item.select_one('.pv-entity__secondary-title')
                    
                    if job_title and company:
                        experience_data.append({
                            'title': job_title.get_text(strip=True),
                            'company': company.get_text(strip=True),
                            'description': 'Experience details from LinkedIn'
                        })
            
            return experience_data
        except Exception:
            return []
    
    def _extract_education(self, soup: BeautifulSoup) -> list:
        """Extract education from LinkedIn profile"""
        try:
            education_data = []
            
            # Look for education section
            education_sections = soup.select('.pv-profile-section.education-section')
            
            if education_sections:
                for item in education_sections[0].select('.pv-entity__position-group-pager'):
                    school = item.select_one('.pv-entity__school-name')
                    degree = item.select_one('.pv-entity__degree-name')
                    
                    if school:
                        education_data.append({
                            'school': school.get_text(strip=True),
                            'degree': degree.get_text(strip=True) if degree else 'Degree not specified',
                        })
            
            return education_data
        except Exception:
            return []
    
    def _extract_skills(self, soup: BeautifulSoup) -> list:
        """Extract skills from LinkedIn profile"""
        try:
            skills = []
            
            # Look for skills section
            skills_sections = soup.select('.pv-skill-category-entity__name')
            
            for skill_element in skills_sections:
                skill_text = skill_element.get_text(strip=True)
                if skill_text:
                    skills.append(skill_text)
            
            return skills[:20]  # Limit to first 20 skills
        except Exception:
            return []
    
    def _format_profile_data(self, profile_data: Dict[str, Any]) -> str:
        """Format profile data for AI processing"""
        formatted_text = f"""
LINKEDIN PROFILE DATA:

Name: {profile_data['name']}
Headline: {profile_data['headline']}
Location: {profile_data['location']}

About:
{profile_data['about']}

Experience:
"""
        
        for exp in profile_data['experience']:
            formatted_text += f"- {exp['title']} at {exp['company']}\n"
            formatted_text += f"  {exp['description']}\n"
        
        formatted_text += "\nEducation:\n"
        for edu in profile_data['education']:
            formatted_text += f"- {edu['degree']} from {edu['school']}\n"
        
        formatted_text += "\nSkills:\n"
        for skill in profile_data['skills']:
            formatted_text += f"- {skill}\n"
        
        return formatted_text
    
    def _get_fallback_format(self, url: str) -> str:
        """Return fallback format when scraping fails"""
        return f"""
LINKEDIN PROFILE DATA (Manual Processing Required):

LinkedIn URL: {url}

Note: Unable to automatically extract profile data. Please manually provide the following information:

1. Name and contact information
2. Professional headline
3. Current location
4. About/Summary section
5. Work experience with job titles, companies, and descriptions
6. Education background
7. Key skills and technologies

This information will be used to generate your tailored resume.
"""