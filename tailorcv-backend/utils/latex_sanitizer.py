import re

def sanitize_for_latex(text):
    """
    Sanitizes a string to make it safe for LaTeX compilation.
    This is crucial for handling text from external sources like an AI.
    
    Args:
        text (str): The input string.
        
    Returns:
        str: The sanitized string.
    """
    if not isinstance(text, str):
        # If the input is not a string (e.g., None), return it as is.
        return text

    # Dictionary of special LaTeX characters and their escaped versions
    replacements = {
        '&': r'\\&',
        '%': r'\\%',
        '$': r'\\$',
        '#': r'\\#',
        '_': r'\\_',
        '{': r'\\{',
        '}': r'\\}',
        '~': r'\\textasciitilde{}',
        '^': r'\\textasciicircum{}',
        '\\': r'\\textbackslash{}',
        '<': r'\\textless{}',
        '>': r'\\textgreater{}',
    }

    # Use regex to perform all replacements in one pass
    # The keys are escaped to be safe inside the regex character set
    regex = re.compile(r'|'.join(map(re.escape, replacements.keys())))
    
    # The lambda function looks up the replacement for each matched character
    return regex.sub(lambda match: replacements[match.group(0)], text) 