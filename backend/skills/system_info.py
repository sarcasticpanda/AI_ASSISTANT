"""
System Info Skill - Get system information (battery, CPU, memory, etc.)
Uses psutil for system metrics.
"""

import logging

logger = logging.getLogger(__name__)

# Try importing psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not installed. Install with: pip install psutil")
    PSUTIL_AVAILABLE = False


def get_battery_status() -> str:
    """
    Get battery status and percentage.
    
    Returns:
        str: Battery information
    
    Examples:
        "Battery: 85% (charging)"
        "Battery: 45% (on battery)"
        "No battery detected"
    """
    if not PSUTIL_AVAILABLE:
        return "System info requires psutil. Install with: pip install psutil"
    
    try:
        battery = psutil.sensors_battery()
        
        if battery is None:
            return "No battery detected (desktop or plugged in)"
        
        percent = battery.percent
        charging = "charging" if battery.power_plugged else "on battery"
        
        # Time remaining
        time_left = ""
        if not battery.power_plugged and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            time_left = f", {int(hours)}h {int(minutes)}m remaining"
        
        logger.info(f"Battery: {percent}% ({charging})")
        return f"Battery: {int(percent)}% ({charging}){time_left}"
    
    except Exception as e:
        logger.error(f"Failed to get battery status: {e}")
        return f"Error getting battery status: {e}"


def get_cpu_usage() -> str:
    """
    Get CPU usage percentage.
    
    Returns:
        str: CPU usage info
    
    Examples:
        "CPU usage: 23%"
    """
    if not PSUTIL_AVAILABLE:
        return "System info requires psutil. Install with: pip install psutil"
    
    try:
        # Get average over 1 second
        cpu_percent = psutil.cpu_percent(interval=1)
        
        logger.info(f"CPU: {cpu_percent}%")
        return f"CPU usage: {cpu_percent}%"
    
    except Exception as e:
        logger.error(f"Failed to get CPU usage: {e}")
        return f"Error getting CPU usage: {e}"


def get_memory_usage() -> str:
    """
    Get memory (RAM) usage.
    
    Returns:
        str: Memory usage info
    
    Examples:
        "Memory: 8.2 GB used of 16.0 GB (51%)"
    """
    if not PSUTIL_AVAILABLE:
        return "System info requires psutil. Install with: pip install psutil"
    
    try:
        mem = psutil.virtual_memory()
        
        # Convert to GB
        total_gb = mem.total / (1024 ** 3)
        used_gb = mem.used / (1024 ** 3)
        percent = mem.percent
        
        logger.info(f"Memory: {used_gb:.1f}/{total_gb:.1f} GB ({percent}%)")
        return f"Memory: {used_gb:.1f} GB used of {total_gb:.1f} GB ({percent}%)"
    
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        return f"Error getting memory usage: {e}"


def get_disk_usage(path: str = "/") -> str:
    """
    Get disk usage for a path.
    
    Args:
        path: Path to check (default: root)
    
    Returns:
        str: Disk usage info
    
    Examples:
        "Disk C:: 245.3 GB used of 500.0 GB (49%)"
    """
    if not PSUTIL_AVAILABLE:
        return "System info requires psutil. Install with: pip install psutil"
    
    try:
        # On Windows, use C: if path is /
        if path == "/" and psutil.WINDOWS:
            path = "C:\\"
        
        disk = psutil.disk_usage(path)
        
        # Convert to GB
        total_gb = disk.total / (1024 ** 3)
        used_gb = disk.used / (1024 ** 3)
        percent = disk.percent
        
        logger.info(f"Disk {path}: {used_gb:.1f}/{total_gb:.1f} GB ({percent}%)")
        return f"Disk {path}: {used_gb:.1f} GB used of {total_gb:.1f} GB ({percent}%)"
    
    except Exception as e:
        logger.error(f"Failed to get disk usage: {e}")
        return f"Error getting disk usage: {e}"


def get_system_info() -> str:
    """
    Get comprehensive system information.
    
    Returns:
        str: Full system info summary
    """
    if not PSUTIL_AVAILABLE:
        return "System info requires psutil. Install with: pip install psutil"
    
    try:
        parts = []
        
        # CPU
        cpu = psutil.cpu_percent(interval=1)
        parts.append(f"CPU: {cpu}%")
        
        # Memory
        mem = psutil.virtual_memory()
        mem_gb = mem.used / (1024 ** 3)
        mem_total_gb = mem.total / (1024 ** 3)
        parts.append(f"Memory: {mem_gb:.1f}/{mem_total_gb:.1f} GB ({mem.percent}%)")
        
        # Disk
        disk = psutil.disk_usage("C:\\" if psutil.WINDOWS else "/")
        disk_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        parts.append(f"Disk: {disk_gb:.1f}/{disk_total_gb:.1f} GB ({disk.percent}%)")
        
        # Battery (if available)
        battery = psutil.sensors_battery()
        if battery:
            charging = "charging" if battery.power_plugged else "on battery"
            parts.append(f"Battery: {int(battery.percent)}% ({charging})")
        
        info = ", ".join(parts)
        logger.info(f"System info: {info}")
        return f"System: {info}"
    
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return f"Error getting system info: {e}"


def is_available() -> bool:
    """Check if system info functionality is available"""
    return PSUTIL_AVAILABLE
