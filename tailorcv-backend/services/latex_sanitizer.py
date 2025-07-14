import re

def sanitize_for_latex(text: str) -> str:
    """
    Escapes special LaTeX characters in a given string.
    """
    if not isinstance(text, str):
        return ""

    # Characters that need to be escaped
    conv = {
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
    
    # Use regex to perform replacements
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=len, reverse=True)))
    return regex.sub(lambda match: conv[match.group()], text) 