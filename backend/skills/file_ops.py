"""
File Operations Skill - Create, open, and manage files
"""

import os
import logging
import platform

logger = logging.getLogger(__name__)


def create_file(filepath: str, content: str = "") -> str:
    """
    Create a new file with optional content.
    
    Args:
        filepath: Path where file should be created
        content: Optional initial content
    
    Returns:
        str: Status message
    
    Examples:
        create_file("C:/Users/test/notes.txt", "Hello world")
    """
    try:
        # Expand environment variables and user home
        filepath = os.path.expandvars(os.path.expanduser(filepath))
        
        # Create parent directories if needed
        parent_dir = os.path.dirname(filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✓ Created file: {filepath}")
        return f"Created file: {os.path.basename(filepath)}"
    
    except Exception as e:
        logger.error(f"Failed to create file: {e}")
        return f"Error creating file: {e}"


def open_file(filepath: str) -> str:
    """
    Open a file with default application.
    
    Args:
        filepath: Path to file to open
    
    Returns:
        str: Status message
    
    Examples:
        open_file("C:/Users/test/document.pdf")
    """
    try:
        # Expand environment variables and user home
        filepath = os.path.expandvars(os.path.expanduser(filepath))
        
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        # Open with default application
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            subprocess.Popen(["open", filepath])
        else:  # Linux
            import subprocess
            subprocess.Popen(["xdg-open", filepath])
        
        logger.info(f"✓ Opened file: {filepath}")
        return f"Opened {os.path.basename(filepath)}"
    
    except Exception as e:
        logger.error(f"Failed to open file: {e}")
        return f"Error opening file: {e}"


def parse_file_command(text: str) -> tuple:
    """
    Parse file operation from natural language.
    
    Args:
        text: Natural language command
    
    Returns:
        tuple: (operation, filepath, content) or (None, None, None)
    
    Examples:
        "create a file named notes.txt" -> ("create", "notes.txt", "")
        "open document.pdf" -> ("open", "document.pdf", None)
    """
    import re
    
    text_lower = text.lower()
    
    # Pattern: "create (a) file (named/called) X"
    match = re.search(r"create\s+(?:a\s+)?file\s+(?:named|called)?\s*(.+?)(?:\s+with|$)", text_lower)
    if match:
        filename = match.group(1).strip()
        
        # Check for content: "with content X" or "containing X"
        content_match = re.search(r"(?:with content|containing)\s+(.+)", text_lower)
        content = content_match.group(1) if content_match else ""
        
        return ("create", filename, content)
    
    # Pattern: "open (file) X"
    match = re.search(r"open\s+(?:file\s+)?(.+?)(?:\s+in|$)", text_lower)
    if match:
        filename = match.group(1).strip()
        return ("open", filename, None)
    
    return (None, None, None)


def is_available() -> bool:
    """Check if file operations are available"""
    return True
