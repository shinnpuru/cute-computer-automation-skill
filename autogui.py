import os
import sys
import subprocess
import pyautogui
import adbutils
from datetime import datetime
from fastmcp import FastMCP
from fastmcp.utilities.types import Image, Audio, File

# Initialize FastMCP server
mcp = FastMCP(
    name = "Simple GUI Automation",
    instructions= (
        "You are an automation assistant. You MUST use the provided MCP tools to interact with the "
        "local machine or connected Android devices. \n\n"
        "CRITICAL RULES:\n"
        "1. DO NOT attempt to run shell commands, 'adb' CLI commands, or Python scripts in the terminal "
        "to perform automation. Use the tools provided in this server exclusively.\n"
        "2. Always allow one second or more to wait the gui action.\n"
        "3. Take a screenshot using 'take_screenshot' to verify the UI state before and after complex actions.\n"
        "4. For Android tasks, ensure a device is selected using 'adb_list_devices' and 'select_device'.\n"
        "5. If an action fails, take a screenshot to diagnose the issue rather than guessing coordinates."
    )
)

# Global state for ADB
current_adb_serial = None

def get_adb_device():
    if not current_adb_serial:
        return None
    return adbutils.adb.device(serial=current_adb_serial)

# --- Device Control Functions ---

@mcp.tool()
def adb_list_devices():
    """List all connected ADB devices."""
    devices = adbutils.adb.list()
    return [{"serial": d.serial, "state": d.state} for d in devices]

@mcp.tool()
def select_device(serial: str = None):
    """Switch the active device. Pass a serial for ADB, or None for local machine."""
    global current_adb_serial
    current_adb_serial = serial
    return f"Active device set to: {serial or 'Local Machine'}"

# --- Unified Interaction Functions ---

@mcp.tool()
def mouse_move(x: int, y: int, duration: float = 0.1):
    """Move the mouse cursor to (x, y) coordinates (Local only)."""
    if current_adb_serial:
        return "ADB: mouse_move not supported (use click instead)."
    pyautogui.moveTo(x, y, duration=duration)
    return f"Local: Mouse moved to ({x}, {y})"

@mcp.tool()
def click(x: int, y: int, button: str = "left", clicks: int = 1):
    """Click/Tap at (x, y). Uses ADB if a device is selected, otherwise local."""
    device = get_adb_device()
    if device:
        device.click(x, y)
        return f"ADB: Tapped at ({x}, {y})"
    else:
        pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        return f"Local: Clicked {button} at ({x}, {y})"

@mcp.tool()
def drag_or_swipe(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5):
    """Drag (Local) or Swipe (ADB) from (x1, y1) to (x2, y2)."""
    device = get_adb_device()
    if device:
        device.swipe(x1, y1, x2, y2, duration=duration)
        return f"ADB: Swiped from ({x1}, {y1}) to ({x2}, {y2})"
    else:
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=duration)
        return f"Local: Dragged from ({x1}, {y1}) to ({x2}, {y2})"

@mcp.tool()
def type_text(text: str, interval: float = 0.05):
    """Type text on the active device."""
    device = get_adb_device()
    if device:
        device.send_keys(text)
        return f"ADB: Typed text: {text}"
    else:
        pyautogui.write(text, interval=interval)
        return f"Local: Typed text: {text}"

@mcp.tool()
def press_key(key: str, times: int = 1):
    """Press a key (e.g., 'ENTER', 'HOME', 'BACK', 'F1', 'F2')"""
    device = get_adb_device()
    if device:
        for i in range(times):
            device.keyevent(key)
        return f"ADB: Sent keyevent: {key} for {times} times."
    else:
        for i in range(times):
            pyautogui.press(key)
        return f"Local: Pressed key: {key} for {times} times."

@mcp.tool()
def list_apps():
    """List installed applications on the active device (Local or ADB)."""
    device = get_adb_device()
    if device:
        packages = device.list_packages()
        return "\n".join(packages)
    
    # Local Machine
    if sys.platform == "win32":
        try:
            cmd = 'powershell "Get-StartApps | Select-Object -ExpandProperty Name"'
            return subprocess.check_output(cmd, shell=True, text=True)
        except Exception as e:
            return f"Error listing Windows apps: {str(e)}"
    elif sys.platform == "darwin":
        try:
            return subprocess.check_output(["ls", "/Applications"], text=True)
        except Exception as e:
            return f"Error listing macOS apps: {str(e)}"
    else:  # Linux
        try:
            return subprocess.check_output(["ls", "/usr/share/applications"], text=True)
        except Exception as e:
            return f"Error listing Linux apps: {str(e)}"

@mcp.tool()
def run_app(app_id: str):
    """Run/Start an application by its ID or name."""
    device = get_adb_device()
    if device:
        device.app_start(app_id)
        return f"ADB: Started app {app_id}"
    
    # Local Machine
    try:
        if sys.platform == "win32":
            os.startfile(app_id)
        elif sys.platform == "darwin":
            subprocess.run(["open", "-a", app_id], check=True)
        else:  # Linux
            subprocess.run(["xdg-open", app_id], check=True)
        return f"Local ({sys.platform}): Started {app_id}"
    except Exception as e:
        return f"Error starting local app: {str(e)}"

# --- Screenshot Functions ---

@mcp.tool()
def take_screenshot():
    """Take a screenshot of the active device (Local or ADB) and get {width}x{height}"""
    device = get_adb_device()
    if device:
        image = device.screenshot()
    else:
        image = pyautogui.screenshot()

    width, height = image.size
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    image.save(filename)
    return [Image(path=filename), f"{width}x{height}"]

if __name__ == "__main__":
    mcp.run()