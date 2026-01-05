"""
List Installed Apps
Shows all applications available in Windows Start Menu.
Useful for finding exact app names for voice commands.
"""

import os
import glob

def list_installed_apps():
    """
    List all installed applications from Windows Start Menu.
    """
    print("\n" + "="*70)
    print("📱 INSTALLED APPLICATIONS")
    print("="*70)
    
    apps = set()  # Use set to avoid duplicates
    
    # Search paths
    search_paths = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]
    
    print("\n🔍 Scanning Start Menu shortcuts...\n")
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            # Find all .lnk files
            shortcuts = glob.glob(f"{base_path}/**/*.lnk", recursive=True)
            
            for shortcut in shortcuts:
                # Get app name (filename without .lnk)
                app_name = os.path.splitext(os.path.basename(shortcut))[0]
                
                # Skip uninstall shortcuts
                if "uninstall" not in app_name.lower():
                    apps.add(app_name)
    
    # Sort and display
    apps_sorted = sorted(apps, key=str.lower)
    
    # Group by category (first letter)
    current_letter = ""
    count = 0
    
    for app in apps_sorted:
        first_letter = app[0].upper()
        
        if first_letter != current_letter:
            current_letter = first_letter
            print(f"\n--- {current_letter} ---")
        
        print(f"  • {app}")
        count += 1
    
    print("\n" + "="*70)
    print(f"✅ Found {count} installed applications")
    print("="*70)
    
    # Common app suggestions
    print("\n💡 COMMON APPS TO TRY:")
    common = [
        "Google Chrome", "Microsoft Edge", "Firefox",
        "Visual Studio Code", "Notepad", "Calculator",
        "File Explorer", "Command Prompt", "PowerShell",
        "Discord", "Slack", "Zoom", "Teams",
        "Spotify", "VLC", "OBS Studio",
        "Notion", "Obsidian"
    ]
    
    for app in common:
        if app in apps_sorted:
            print(f"  ✓ {app} - Installed")
    
    print("\n📝 To open any app:")
    print("   Voice: 'Open [app name]'")
    print("   Code:  open_app('[app name]')")
    print()

if __name__ == "__main__":
    list_installed_apps()
