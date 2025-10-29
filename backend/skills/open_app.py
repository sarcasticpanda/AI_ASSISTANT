"""
Open App Skill - Open applications and folders
Opens local applications, folders, or websites.
"""

import os
import logging
import subprocess
import platform

logger = logging.getLogger(__name__)

# Common application paths (Windows)
APP_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "vscode": r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}

# Common folders
FOLDER_PATHS = {
    "downloads": "{USERPROFILE}\\Downloads",
    "documents": "{USERPROFILE}\\Documents",
    "desktop": "{USERPROFILE}\\Desktop",
    "pictures": "{USERPROFILE}\\Pictures",
    "music": "{USERPROFILE}\\Music",
}


def open_app(name: str) -> str:
    """
    Open an application, folder, or website.
    
    Args:
        name: App name, folder name, or URL
    
    Returns:
        str: Status message
    
    Examples:
        open_app("chrome")  # Opens Google Chrome
        open_app("downloads")  # Opens Downloads folder
        open_app("https://google.com")  # Opens URL in default browser
    """
    name = name.lower().strip()
    
    logger.info(f"Opening: {name}")
    
    # Check if it's a URL
    if name.startswith("http://") or name.startswith("https://"):
        return _open_url(name)
    
    # Check if it's a known folder
    if name in FOLDER_PATHS:
        return _open_folder(FOLDER_PATHS[name])
    
    # Check if it's a known app
    if name in APP_PATHS:
        return _open_application(APP_PATHS[name])
    
    # Try to find and open as executable
    return _try_open_any(name)


def _open_application(path: str) -> str:
    """Open an application by path"""
    try:
        # Expand environment variables
        path = os.path.expandvars(path)
        
        if not os.path.exists(path):
            return f"Application not found: {path}"
        
        # Open application
        if platform.system() == "Windows":
            subprocess.Popen([path], shell=True)
        else:
            subprocess.Popen([path])
        
        logger.info(f"✓ Opened application: {path}")
        return f"Opened {os.path.basename(path)}"
    
    except Exception as e:
        logger.error(f"Failed to open application: {e}")
        return f"Error opening application: {e}"


def _open_folder(path: str) -> str:
    """Open a folder in Explorer"""
    try:
        # Expand environment variables
        path = os.path.expandvars(path)
        
        if not os.path.exists(path):
            return f"Folder not found: {path}"
        
        # Open in Explorer
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
        
        logger.info(f"✓ Opened folder: {path}")
        return f"Opened folder {os.path.basename(path)}"
    
    except Exception as e:
        logger.error(f"Failed to open folder: {e}")
        return f"Error opening folder: {e}"


def _open_url(url: str) -> str:
    """Open URL in default browser"""
    try:
        import webbrowser
        
        webbrowser.open(url)
        
        logger.info(f"✓ Opened URL: {url}")
        return f"Opened {url}"
    
    except Exception as e:
        logger.error(f"Failed to open URL: {e}")
        return f"Error opening URL: {e}"


def _try_open_any(name: str) -> str:
    """Try to open anything - search in common locations"""
    try:
        # Try as Windows command
        if platform.system() == "Windows":
            result = subprocess.run(
                ["where", name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Found executable
                exe_path = result.stdout.strip().split('\n')[0]
                return _open_application(exe_path)
        
        # Fallback: try to start as shell command
        if platform.system() == "Windows":
            subprocess.Popen(["start", name], shell=True)
        else:
            subprocess.Popen([name])
        
        return f"Attempted to open {name}"
    
    except Exception as e:
        logger.error(f"Failed to open {name}: {e}")
        return f"Could not open '{name}'. Please provide full path or check if it's installed."
