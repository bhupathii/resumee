import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
import html

class PDFFallbackService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=HexColor('#2563eb')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#64748b')
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#1e293b'),
            borderWidth=1,
            borderColor=HexColor('#2563eb'),
            borderPadding=2
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#374151')
        )
        
        # List item style
        self.list_style = ParagraphStyle(
            'ListItem',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20,
            bulletIndent=10,
            textColor=HexColor('#374151')
        )
    
    def generate_pdf(self, resume_data: Dict[str, Any], is_premium: bool = False) -> bytes:
        """Generate PDF from resume data using ReportLab"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the PDF content
            story = []
            
            # Add header
            self._add_header(story, resume_data.get('personalInfo', {}))
            
            # Add summary
            if resume_data.get('summary'):
                self._add_section(story, 'Professional Summary', resume_data['summary'])
            
            # Add skills
            if resume_data.get('skills'):
                self._add_skills_section(story, resume_data['skills'])
            
            # Add experience
            if resume_data.get('experience'):
                self._add_experience_section(story, resume_data['experience'])
            
            # Add education
            if resume_data.get('education'):
                self._add_education_section(story, resume_data['education'])
            
            # Add projects
            if resume_data.get('projects'):
                self._add_projects_section(story, resume_data['projects'])
            
            # Add certifications
            if resume_data.get('certifications'):
                self._add_certifications_section(story, resume_data['certifications'])
            
            # Add watermark for free users
            if not is_premium:
                self._add_watermark(story)
            
            # Build PDF
            doc.build(story)
            
            # Get the PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def _escape_html(self, text):
        """Escape HTML characters for safe PDF rendering"""
        if not isinstance(text, str):
            text = str(text)
        return html.escape(text)
    
    def _add_header(self, story, personal_info):
        """Add header section with personal information"""
        # Name
        name = personal_info.get('name', 'Your Name')
        story.append(Paragraph(self._escape_html(name), self.title_style))
        
        # Contact info
        contact_parts = []
        if personal_info.get('email'):
            contact_parts.append(f"Email: {personal_info['email']}")
        if personal_info.get('phone'):
            contact_parts.append(f"Phone: {personal_info['phone']}")
        if personal_info.get('location'):
            contact_parts.append(f"Location: {personal_info['location']}")
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            story.append(Paragraph(self._escape_html(contact_text), self.subtitle_style))
        
        story.append(Spacer(1, 12))
    
    def _add_section(self, story, title, content):
        """Add a general section with title and content"""
        story.append(Paragraph(title, self.section_style))
        if isinstance(content, str):
            story.append(Paragraph(self._escape_html(content), self.body_style))
        elif isinstance(content, list):
            for item in content:
                story.append(Paragraph(f"• {self._escape_html(str(item))}", self.list_style))
        story.append(Spacer(1, 6))
    
    def _add_skills_section(self, story, skills):
        """Add skills section"""
        story.append(Paragraph("Technical Skills", self.section_style))
        
        # Group skills in a more readable format
        if isinstance(skills, list):
            for skill in skills:
                story.append(Paragraph(f"• {self._escape_html(str(skill))}", self.list_style))
        
        story.append(Spacer(1, 6))
    
    def _add_experience_section(self, story, experiences):
        """Add experience section"""
        story.append(Paragraph("Professional Experience", self.section_style))
        
        for exp in experiences:
            # Job title and company
            title = exp.get('title', 'Job Title')
            company = exp.get('company', 'Company')
            start_date = exp.get('startDate', '')
            end_date = exp.get('endDate', '')
            
            # Create a table for job header
            job_header = f"<b>{self._escape_html(title)}</b> at {self._escape_html(company)}"
            date_range = f"{start_date} - {end_date}"
            
            story.append(Paragraph(job_header, self.body_style))
            story.append(Paragraph(self._escape_html(date_range), self.body_style))
            
            # Job description
            if exp.get('description'):
                descriptions = exp['description'] if isinstance(exp['description'], list) else [exp['description']]
                for desc in descriptions:
                    story.append(Paragraph(f"• {self._escape_html(str(desc))}", self.list_style))
            
            story.append(Spacer(1, 8))
    
    def _add_education_section(self, story, education):
        """Add education section"""
        story.append(Paragraph("Education", self.section_style))
        
        for edu in education:
            degree = edu.get('degree', 'Degree')
            institution = edu.get('institution', 'Institution')
            start_date = edu.get('startDate', '')
            end_date = edu.get('endDate', '')
            
            edu_header = f"<b>{self._escape_html(degree)}</b> - {self._escape_html(institution)}"
            date_range = f"{start_date} - {end_date}"
            
            story.append(Paragraph(edu_header, self.body_style))
            story.append(Paragraph(self._escape_html(date_range), self.body_style))
            
            if edu.get('gpa'):
                story.append(Paragraph(f"GPA: {edu['gpa']}", self.body_style))
            
            story.append(Spacer(1, 8))
    
    def _add_projects_section(self, story, projects):
        """Add projects section"""
        story.append(Paragraph("Projects", self.section_style))
        
        for project in projects:
            name = project.get('name', 'Project Name')
            description = project.get('description', '')
            technologies = project.get('technologies', [])
            
            story.append(Paragraph(f"<b>{self._escape_html(name)}</b>", self.body_style))
            
            if description:
                story.append(Paragraph(self._escape_html(description), self.body_style))
            
            if technologies:
                tech_list = ', '.join([str(tech) for tech in technologies])
                story.append(Paragraph(f"Technologies: {self._escape_html(tech_list)}", self.body_style))
            
            story.append(Spacer(1, 8))
    
    def _add_certifications_section(self, story, certifications):
        """Add certifications section"""
        story.append(Paragraph("Certifications", self.section_style))
        
        for cert in certifications:
            name = cert.get('name', 'Certification')
            issuer = cert.get('issuer', 'Issuer')
            date = cert.get('date', '')
            
            cert_text = f"<b>{self._escape_html(name)}</b> - {self._escape_html(issuer)}"
            if date:
                cert_text += f" ({self._escape_html(date)})"
            
            story.append(Paragraph(cert_text, self.body_style))
            story.append(Spacer(1, 4))
    
    def _add_watermark(self, story):
        """Add watermark for free users"""
        story.append(Spacer(1, 20))
        watermark_style = ParagraphStyle(
            'Watermark',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=HexColor('#9ca3af')
        )
        story.append(Paragraph("Generated by TailorCV - AI-Powered Resume Generator", watermark_style))