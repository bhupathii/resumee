import os
import tempfile
import subprocess
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import re
import logging

class LaTeXService:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Configure Jinja2 filters for LaTeX escaping
        self.jinja_env.filters['latex_escape'] = self._latex_escape
    
    def _latex_escape(self, text):
        """
        Escape special LaTeX characters in text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # LaTeX special characters that need escaping
        latex_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\^{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\~{}',
            '\\': r'\textbackslash{}',
        }
        
        # Replace special characters
        for char, replacement in latex_chars.items():
            text = text.replace(char, replacement)
        
        return text
    
    def generate_pdf(self, resume_data: Dict[str, Any], is_premium: bool = False) -> bytes:
        """
        Generate PDF from resume data using LaTeX
        """
        try:
            # Choose template based on premium status
            template_name = 'premium_resume.tex' if is_premium else 'free_resume.tex'
            
            # Generate LaTeX content
            latex_content = self._generate_latex_content(resume_data, template_name, is_premium)
            
            # Compile LaTeX to PDF
            pdf_content = self._compile_latex_to_pdf(latex_content)
            
            return pdf_content
            
        except Exception as e:
            logging.error(f"PDF generation failed: {str(e)}")
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def _generate_latex_content(self, resume_data: Dict[str, Any], template_name: str, is_premium: bool) -> str:
        """
        Generate LaTeX content from resume data and template
        """
        try:
            # Load template
            template = self.jinja_env.get_template(template_name)
            
            # Clean and prepare data for template
            template_data = self._prepare_template_data(resume_data, is_premium)
            
            # Render template
            latex_content = template.render(template_data)
            
            return latex_content
            
        except Exception as e:
            logging.error(f"Template rendering failed: {str(e)}")
            # Fallback to basic template if template rendering fails
            return self._generate_fallback_latex(resume_data, is_premium)
    
    def _prepare_template_data(self, resume_data: Dict[str, Any], is_premium: bool) -> Dict[str, Any]:
        """
        Prepare and clean resume data for LaTeX template
        """
        # Escape LaTeX special characters in all text fields
        def clean_text(text):
            if isinstance(text, str):
                return self._latex_escape(text)
            return text
        
        def clean_dict(data):
            if isinstance(data, dict):
                return {k: clean_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_dict(item) for item in data]
            else:
                return clean_text(data)
        
        # Clean all data
        cleaned_data = clean_dict(resume_data)
        
        # Prepare data for template
        template_data = {
            'personal_info': cleaned_data.get('personalInfo', {}),
            'summary': cleaned_data.get('summary', ''),
            'skills': cleaned_data.get('skills', []),
            'experience': cleaned_data.get('experience', []),
            'education': cleaned_data.get('education', []),
            'projects': cleaned_data.get('projects', []),
            'certifications': cleaned_data.get('certifications', []),
            'is_premium': is_premium,
            'show_watermark': not is_premium
        }
        
        return template_data
    
    def _compile_latex_to_pdf(self, latex_content: str) -> bytes:
        """
        Compile LaTeX content to PDF using pdflatex
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX content to file
            tex_file = os.path.join(temp_dir, 'resume.tex')
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                # First attempt with pdflatex
                result = subprocess.run([
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory=' + temp_dir,
                    '-halt-on-error',
                    tex_file
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    logging.warning(f"pdflatex failed, trying xelatex. Error: {result.stderr}")
                    # If pdflatex fails, try with xelatex
                    result = subprocess.run([
                        'xelatex',
                        '-interaction=nonstopmode',
                        '-output-directory=' + temp_dir,
                        '-halt-on-error',
                        tex_file
                    ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    # Log the LaTeX error for debugging
                    error_msg = f"LaTeX compilation failed.\nStdout: {result.stdout}\nStderr: {result.stderr}"
                    logging.error(error_msg)
                    
                    # Try to extract useful error information
                    error_lines = result.stdout.split('\n') + result.stderr.split('\n')
                    useful_errors = []
                    for line in error_lines:
                        if any(keyword in line.lower() for keyword in ['error', 'undefined', 'missing', 'not found']):
                            useful_errors.append(line.strip())
                    
                    if useful_errors:
                        raise Exception(f"LaTeX compilation error: {'; '.join(useful_errors[:3])}")
                    else:
                        raise Exception(f"LaTeX compilation failed with return code {result.returncode}")
                
                # Read generated PDF
                pdf_file = os.path.join(temp_dir, 'resume.pdf')
                if not os.path.exists(pdf_file):
                    raise Exception("PDF file was not generated despite successful compilation")
                
                with open(pdf_file, 'rb') as f:
                    return f.read()
                    
            except subprocess.TimeoutExpired:
                raise Exception("LaTeX compilation timed out after 60 seconds")
            except FileNotFoundError:
                raise Exception("LaTeX compiler not found. Please ensure pdflatex or xelatex is installed.")
    
    def _generate_fallback_latex(self, resume_data: Dict[str, Any], is_premium: bool) -> str:
        """
        Generate basic LaTeX content as fallback when template fails
        """
        personal_info = resume_data.get('personalInfo', {})
        name = self._latex_escape(personal_info.get('name', 'Your Name'))
        email = self._latex_escape(personal_info.get('email', 'your.email@example.com'))
        phone = self._latex_escape(personal_info.get('phone', '(555) 123-4567'))
        location = self._latex_escape(personal_info.get('location', 'Your City, State'))
        
        watermark = '' if is_premium else '\\usepackage{background}\n\\backgroundsetup{scale=1,color=black,opacity=0.1,angle=45,contents={Generated by TailorCV}}'
        
        latex_content = f"""
\\documentclass[letterpaper,11pt]{{article}}
\\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{{geometry}}
\\usepackage{{titlesec}}
\\usepackage{{enumitem}}
\\usepackage{{hyperref}}
\\usepackage{{xcolor}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
{watermark}

\\pagestyle{{empty}}
\\setlength{{\\tabcolsep}}{{0em}}

\\titleformat{{\\section}}{{\\vspace{{-4pt}}\\raggedright\\large\\bfseries}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-5pt}}]

\\begin{{document}}

\\begin{{center}}
    {{\\Huge \\bfseries {name}}} \\\\ \\vspace{{1pt}}
    \\small Phone: {phone} | Email: \\href{{mailto:{email}}}{{{email}}} | Location: {location}
\\end{{center}}

\\section{{Summary}}
{self._latex_escape(resume_data.get('summary', 'Professional summary goes here.'))}

\\section{{Skills}}
\\begin{{itemize}}[leftmargin=0.15in, label={{$\\bullet$}}]
"""
        
        # Add skills
        for skill in resume_data.get('skills', []):
            escaped_skill = self._latex_escape(str(skill))
            latex_content += f"    \\item {escaped_skill}\n"
        
        latex_content += """
\\end{itemize}

\\section{Experience}
"""
        
        # Add experience
        for exp in resume_data.get('experience', []):
            company = self._latex_escape(exp.get('company', ''))
            title = self._latex_escape(exp.get('title', ''))
            start_date = self._latex_escape(exp.get('startDate', ''))
            end_date = self._latex_escape(exp.get('endDate', ''))
            
            latex_content += f"""
\\textbf{{{title}}} \\hfill {start_date} -- {end_date} \\\\
\\textit{{{company}}} \\\\
\\begin{{itemize}}[leftmargin=0.15in, label={{$\\bullet$}}]
"""
            
            for desc in exp.get('description', []):
                escaped_desc = self._latex_escape(str(desc))
                latex_content += f"    \\item {escaped_desc}\n"
            
            latex_content += "\\end{itemize}\n"
        
        latex_content += """
\\section{Education}
"""
        
        # Add education
        for edu in resume_data.get('education', []):
            degree = self._latex_escape(edu.get('degree', ''))
            institution = self._latex_escape(edu.get('institution', ''))
            start_date = self._latex_escape(edu.get('startDate', ''))
            end_date = self._latex_escape(edu.get('endDate', ''))
            
            latex_content += f"""
\\textbf{{{degree}}} \\hfill {start_date} -- {end_date} \\\\
\\textit{{{institution}}} \\\\
"""
        
        # Add projects if available
        if resume_data.get('projects'):
            latex_content += """
\\section{Projects}
"""
            
            for project in resume_data.get('projects', []):
                name = self._latex_escape(project.get('name', ''))
                description = self._latex_escape(project.get('description', ''))
                technologies = ', '.join([self._latex_escape(str(tech)) for tech in project.get('technologies', [])])
                
                latex_content += f"""
\\textbf{{{name}}} \\\\
{description} \\\\
\\textit{{Technologies: {technologies}}} \\\\
"""
        
        latex_content += """
\\end{document}
"""
        
        return latex_content
    
    def validate_latex_installation(self) -> bool:
        """
        Check if LaTeX is properly installed
        """
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                result = subprocess.run(['xelatex', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False
    
    def get_available_templates(self) -> list:
        """
        Get list of available LaTeX templates
        """
        templates = []
        
        if os.path.exists(self.template_dir):
            for file in os.listdir(self.template_dir):
                if file.endswith('.tex'):
                    templates.append(file)
        
        return templates