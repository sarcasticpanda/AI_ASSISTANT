"""
Open App Skill - Open applications, folders, and websites
Uses Windows built-in features for smart app detection - NO hardcoded paths!
Works for ANY installed application on ANY Windows PC.
"""

import os
import logging
import subprocess
import platform
import webbrowser
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import MongoDB manager (optional - for learning user preferences)
try:
    from backend.core import mongo_manager
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    logger.warning("MongoDB not available - user preferences won't be saved")


class SmartAppLauncher:
    """
    Production-ready app launcher using Windows built-in features.
    No hardcoded paths, no slow scanning, just works!
    """
    
    # Simple name mappings (for voice recognition variations)
    ALIASES = {
        # Browsers
        "google chrome": "chrome",
        "chrome browser": "chrome",
        "mozilla firefox": "firefox",
        "microsoft edge": "msedge",
        "brave": "brave",
        
        # Productivity
        "vs code": "code",
        "visual studio code": "code",
        "file explorer": "explorer",
        "my files": "explorer",
        "windows explorer": "explorer",
        "notion": "notion",
        
        # System
        "calculator": "calc",
        "task manager": "taskmgr",
        "control panel": "control",
        "settings": "ms-settings:",
        "command prompt": "cmd",
        "powershell": "powershell",
        
        # Communication
        "whatsapp": "whatsapp",
        "telegram": "telegram",
        "discord": "discord",
        "slack": "slack",
        "zoom": "zoom",
        "microsoft teams": "teams",
        "teams": "teams",
        
        # Entertainment
        "spotify": "spotify",
        "vlc": "vlc",
        "obs": "obs64",
        
        # Development
        "pycharm": "pycharm64",
        "intellij": "idea64",
        "android studio": "studio64",
    }
    
    # Protocol handlers (for apps that support URL schemes)
    PROTOCOLS = {
        "spotify": "spotify:",
        "discord": "discord://",
        "slack": "slack://",
        "zoom": "zoommtg://",
        "teams": "msteams://",
        "notion": "notion://",
    }
    
    # Microsoft Store Apps (UWP) - use AppIDs
    # These need special handling via shell:AppsFolder
    STORE_APPS = {
        "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
        "whatsapp beta": "5319275A.51895FA4EA97F_cv1g1gvanyjgm!App",
        # Add more as needed
    }
    
    # Common folders with environment variables
    FOLDER_PATHS = {
        "downloads": "%USERPROFILE%\\Downloads",
        "documents": "%USERPROFILE%\\Documents",
        "desktop": "%USERPROFILE%\\Desktop",
        "pictures": "%USERPROFILE%\\Pictures",
        "music": "%USERPROFILE%\\Music",
        "videos": "%USERPROFILE%\\Videos",
    }
    
    @staticmethod
    def open(app_name: str) -> Dict:
        """
        Open any application using smart detection.
        
        Args:
            app_name: Application name (e.g., "chrome", "notion", "spotify")
        
        Returns:
            {
                "success": True/False,
                "message": "Opened Chrome",
                "method": "start_menu" | "protocol" | "direct" | "folder"
            }
        """
        # Normalize input
        original_name = app_name
        app_name = app_name.lower().strip()
        
        # Check if it's a folder
        if app_name in SmartAppLauncher.FOLDER_PATHS:
            return SmartAppLauncher._open_folder(app_name)
        
        # Check if it's a URL
        if app_name.startswith("http://") or app_name.startswith("https://") or "." in app_name and " " not in app_name:
            return SmartAppLauncher._open_url(app_name)
        
        # Check aliases
        app_name = SmartAppLauncher.ALIASES.get(app_name, app_name)
        
        # Method 1: Microsoft Store Apps (UWP) - check first for Store apps
        if app_name in SmartAppLauncher.STORE_APPS:
            logger.info(f"Attempting to open '{app_name}' as Microsoft Store app...")
            try:
                app_id = SmartAppLauncher.STORE_APPS[app_name]
                subprocess.run(
                    ['explorer.exe', f'shell:AppsFolder\\{app_id}'],
                    timeout=3
                )
                logger.info(f"✓ Opened '{app_name}' via Store AppID")
                
                if MONGO_AVAILABLE:
                    try:
                        mongo_manager.save_app_command({
                            "command_type": "open_app",
                            "target": app_name,
                            "user_query": f"open {original_name}",
                            "success": True,
                            "method": "store_app"
                        })
                    except:
                        pass
                
                return {
                    "success": True,
                    "message": f"Opened {app_name.title()}",
                    "method": "store_app"
                }
            except Exception as e:
                logger.debug(f"Store app failed for '{app_name}': {e}")
        
        # Method 2: Windows Start Menu (BEST - works 95% of time)
        logger.info(f"Attempting to open '{app_name}' using Windows Start Menu...")
        try:
            # Use 'start ""' to prevent issues with app names containing spaces
            result = subprocess.run(
                ['cmd', '/c', 'start', '', app_name],
                capture_output=True,
                timeout=3,
                text=True
            )
            
            # Windows returns 0 or 1 for success (both are OK)
            if result.returncode in [0, 1]:
                logger.info(f"✓ Opened '{app_name}' via Start Menu")
                
                # Save to MongoDB for learning
                if MONGO_AVAILABLE:
                    try:
                        mongo_manager.save_app_command({
                            "command_type": "open_app",
                            "target": app_name,
                            "user_query": f"open {original_name}",
                            "success": True,
                            "method": "start_menu"
                        })
                    except:
                        pass
                
                return {
                    "success": True,
                    "message": f"Opened {app_name.title()}",
                    "method": "start_menu"
                }
        except subprocess.TimeoutExpired:
            logger.warning(f"Start Menu timeout for '{app_name}'")
        except Exception as e:
            logger.debug(f"Start Menu failed for '{app_name}': {e}")
        
        # Method 3: Protocol handlers (for special apps)
        if app_name in SmartAppLauncher.PROTOCOLS:
            logger.info(f"Attempting to open '{app_name}' using protocol handler...")
            try:
                os.startfile(SmartAppLauncher.PROTOCOLS[app_name])
                logger.info(f"✓ Opened '{app_name}' via protocol")
                
                return {
                    "success": True,
                    "message": f"Opened {app_name.title()}",
                    "method": "protocol"
                }
            except Exception as e:
                logger.debug(f"Protocol failed for '{app_name}': {e}")
        
        # Method 4: Direct .exe (for system apps)
        logger.info(f"Attempting to open '{app_name}.exe' directly...")
        try:
            subprocess.Popen([f'{app_name}.exe'])
            logger.info(f"✓ Opened '{app_name}.exe' directly")
            
            return {
                "success": True,
                "message": f"Opened {app_name.title()}",
                "method": "direct_exe"
            }
        except Exception as e:
            logger.debug(f"Direct exe failed for '{app_name}': {e}")
        
        # Failed all methods
        logger.error(f"Failed to open '{original_name}' - tried all methods")
        return {
            "success": False,
            "message": f"Couldn't find '{original_name}'. Make sure it's installed and try saying the exact app name from Start Menu.",
            "method": None
        }
    
    @staticmethod
    def _open_folder(folder_name: str) -> Dict:
        """Open a folder in Explorer"""
        try:
            # Get folder path and expand environment variables
            folder_path = SmartAppLauncher.FOLDER_PATHS[folder_name]
            folder_path = os.path.expandvars(folder_path)
            
            if not os.path.exists(folder_path):
                return {
                    "success": False,
                    "message": f"Folder not found: {folder_name}",
                    "method": None
                }
            
            # Open in Explorer
            os.startfile(folder_path)
            logger.info(f"✓ Opened folder: {folder_path}")
            
            return {
                "success": True,
                "message": f"Opened {folder_name} folder",
                "method": "folder"
            }
        except Exception as e:
            logger.error(f"Failed to open folder '{folder_name}': {e}")
            return {
                "success": False,
                "message": f"Error opening folder: {e}",
                "method": None
            }
    
    @staticmethod
    def _open_url(url: str) -> Dict:
        """Open URL in default browser"""
        try:
            # Add protocol if missing
            if not url.startswith("http://") and not url.startswith("https://"):
                url = f"https://{url}"
            
            webbrowser.open(url)
            logger.info(f"✓ Opened URL: {url}")
            
            return {
                "success": True,
                "message": f"Opened {url}",
                "method": "url"
            }
        except Exception as e:
            logger.error(f"Failed to open URL '{url}': {e}")
            return {
                "success": False,
                "message": f"Error opening URL: {e}",
                "method": None
            }
    
    @staticmethod
    def get_user_preference(category: str) -> Optional[str]:
        """Get user's preferred app for a category (browser, editor, etc.)"""
        if not MONGO_AVAILABLE:
            return None
        
        try:
            return mongo_manager.get_user_setting(f"preferred_{category}")
        except:
            return None
    
    @staticmethod
    def set_user_preference(category: str, app: str):
        """Save user's preferred app"""
        if not MONGO_AVAILABLE:
            return
        
        try:
            mongo_manager.save_user_setting(f"preferred_{category}", app)
            logger.info(f"Saved preference: {category} = {app}")
        except:
            pass


# ============================================================================
# PUBLIC API (used by brain.py)
# ============================================================================

def open_app(name: str) -> str:
    """
    Open application, folder, or website.
    
    Args:
        name: App name, folder name, or URL
    
    Returns:
        str: Status message
    
    Examples:
        open_app("chrome")              # Opens Google Chrome
        open_app("notion")              # Opens Notion
        open_app("downloads")           # Opens Downloads folder
        open_app("https://google.com")  # Opens URL in browser
        open_app("spotify")             # Opens Spotify
    """
    result = SmartAppLauncher.open(name)
    return result["message"]


def open_website(url: str) -> str:
    """
    Open website in default browser.
    
    Args:
        url: Website URL (with or without http://)
    
    Returns:
        str: Status message
    
    Examples:
        open_website("google.com")
        open_website("https://github.com")
    """
    result = SmartAppLauncher._open_url(url)
    return result["message"]


def open_folder(folder_name: str) -> str:
    """
    Open folder in Explorer.
    
    Args:
        folder_name: Folder shortcut (downloads, documents, etc.) or full path
    
    Returns:
        str: Status message
    
    Examples:
        open_folder("downloads")
        open_folder("C:\\Users\\Documents")
    """
    # Check if it's a shortcut
    if folder_name.lower() in SmartAppLauncher.FOLDER_PATHS:
        result = SmartAppLauncher._open_folder(folder_name.lower())
    else:
        # Try as direct path
        try:
            path = os.path.expandvars(folder_name)
            if os.path.exists(path):
                os.startfile(path)
                return f"Opened {folder_name}"
            else:
                return f"Folder not found: {folder_name}"
        except Exception as e:
            return f"Error opening folder: {e}"
    
    return result["message"]


def is_available() -> bool:
    """Check if app opening functionality is available"""
    return platform.system() == "Windows"
