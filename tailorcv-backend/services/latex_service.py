import os
import shutil
from jinja2 import Environment, FileSystemLoader
from pdflatex import PDFLaTeX
import traceback
from .latex_sanitizer import sanitize_for_latex
from .pdf_fallback_service import PDFFallbackService

class LaTeXService:
    def __init__(self):
        """Initializes the LaTeX service, setting up the template directory."""
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.template_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True, # Enable autoescaping
            variable_start_string='((', # Use custom delimiters
            variable_end_string='))',
            comment_start_string='((#',  # Custom comment delimiters to avoid LaTeX conflicts
            comment_end_string='#))',
            block_start_string='((%',    # Custom block delimiters  
            block_end_string='%)',
        )
        # Initialize fallback service for when LaTeX fails
        self.fallback_service = PDFFallbackService()

    def _sanitize_data(self, data):
        """
        Recursively sanitizes all string values in a dictionary or list
        to make them safe for LaTeX.
        """
        if isinstance(data, dict):
            return {key: self._sanitize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Apply the sanitizer to every string
            return sanitize_for_latex(data)
        # Return non-string, non-dict, non-list values as-is
        return data

    def generate_pdf(self, template_name, data, is_premium=False):
        """
        Generates a PDF from a given LaTeX template and data.
        Sanitizes the data before rendering and falls back to ReportLab if LaTeX fails.
        """
        if not shutil.which('pdflatex'):
            print("ERROR: pdflatex command not found. LaTeX is not installed or not in PATH.")
            print("Falling back to ReportLab PDF generation...")
            return self.fallback_service.generate_pdf(data, is_premium)

        try:
            # First, sanitize all the data to prevent injection and errors
            sanitized_data = self._sanitize_data(data)
            
            # Load the template
            template = self.template_env.get_template(f"{template_name}.tex")
            
            # Render the template with the sanitized data
            latex_content = template.render(sanitized_data)

            # Create a PDFLaTeX object from the rendered content
            p = PDFLaTeX.from_binarystring(latex_content.encode('utf-8'), 'generated_resume')
            
            # Create the PDF. This might take a few seconds.
            pdf_bytes, log, _ = p.create_pdf(keep_pdf_file=False, max_runs=3)

            # Check if the PDF was successfully created
            if not pdf_bytes:
                print("="*20 + " LATEX COMPILATION FAILED " + "="*20)
                print("LaTeX failed to produce a PDF. This is often due to complex characters or formatting.")
                if log:
                    print("--- LaTeX Compiler Log ---")
                    print(log.decode('utf-8', errors='ignore'))
                    print("--------------------------")
                print("Falling back to ReportLab PDF generation...")
                return self.fallback_service.generate_pdf(data, is_premium)
            
            return pdf_bytes
            
        except Exception as e:
            print("="*20 + " UNEXPECTED PDF GENERATION ERROR " + "="*20)
            print(f"An unexpected error occurred in LaTeXService.generate_pdf: {e}")
            traceback.print_exc()
            print("="*60)
            print("Falling back to ReportLab PDF generation...")
            try:
                return self.fallback_service.generate_pdf(data, is_premium)
            except Exception as fallback_error:
                print(f"Fallback PDF generation also failed: {fallback_error}")
                return None