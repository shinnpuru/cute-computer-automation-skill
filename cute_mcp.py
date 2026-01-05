import os
import sys
import subprocess
import pyautogui
import adbutils
import uiautomator2 as u2
import xml.etree.ElementTree as ET
from datetime import datetime
from fastmcp import FastMCP
from fastmcp.utilities.types import Image, Audio, File

# Initialize FastMCP server
mcp = FastMCP(
    name = "cute_mcp",
    instructions= (
        "You are an automation assistant. You MUST use the provided MCP tools to interact with the "
        "local machine or connected Android devices. \n\n"
        "CRITICAL RULES:\n"
        "1. DO NOT attempt to run shell commands, 'adb' CLI commands, or Python scripts in the terminal "
        "to perform automation. Use the tools provided in this server exclusively.\n"
        "2. Always allow one second or more to wait the gui action.\n"
        "3. Use 'get_a11y_tree' first to identify UI elements and their coordinates. Use 'take_screenshot' to verify the visual state or if the accessibility tree is insufficient.\n"
        "4. For Android tasks, ensure a device is selected using 'adb_list_devices' and 'select_device'.\n"
        "5. If an action fails, use 'get_a11y_tree' and 'take_screenshot' to diagnose the issue rather than guessing coordinates."
    )
)

# Global state for ADB
current_adb_serial = None

def get_adb_device():
    if not current_adb_serial:
        return None
    return u2.connect(current_adb_serial)

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

# --- App Functions ---

@mcp.tool()
def list_apps():
    """List installed applications on the active device (Local or ADB)."""
    device = get_adb_device()
    if device:
        return "\n".join(device.app_list())
    
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
    elif sys.platform == 'linux':
        try:
            return subprocess.check_output(["ls", "/usr/share/applications"], text=True)
        except Exception as e:
            return f"Error listing Linux apps: {str(e)}"
    else:
        return "List app not supported on {sys.platform}."

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
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", app_id], check=True)
        else:
            return "Run app not supported on {sys.platform}."
        return f"Local ({sys.platform}): Started {app_id}"
    except Exception as e:
        return f"Error starting local app: {str(e)}"

# --- Vision Functions ---

@mcp.tool()
def get_a11y_tree():
    """Get the accessibility tree of the current screen (Android, Windows, macOS, or Linux)."""
    device = get_adb_device()
    output = []

    if device:
        try:
            xml_data = device.dump_hierarchy()
            root = ET.fromstring(xml_data)
            
            def walk_xml(node, depth):
                # Extract attributes
                cls = node.get('class', 'Unknown')
                text = node.get('text', '')
                desc = node.get('content-desc', '')
                name = text if text else (desc if desc else "No Name")
                bounds = node.get('bounds', '')
                
                output.append(f"[{depth}][{cls}] {name} Bounds: {bounds}")
                for child in node:
                    walk_xml(child, depth + 1)
            
            walk_xml(root, 0)
            return "\n".join(output) if output else "No UI elements found."
        except Exception as e:
            return f"Android Error: {str(e)}"

    if sys.platform == "win32":
        import uiautomation as auto
        def walk(control, depth):
            name = control.Name if control.Name else "No Name"
            rect = control.BoundingRectangle
            output.append(f"[{depth}][{control.ControlTypeName}] {name} (ID: {control.AutomationId}) Bounds: {rect}")
            for child in control.GetChildren():
                walk(child, depth + 1)
        
        # Start from the focused window or root
        root = auto.GetFocusedControl() or auto.GetRootControl()
        walk(root, 0)
        return "\n".join(output) if output else "No UI elements found."

    if sys.platform == "darwin":
        import atomacos
        def walk(element, depth):
            try:
                role = element.AXRole
                name = element.AXTitle or element.AXDescription or "No Name"
                frame = element.AXFrame
                output.append(f"[{depth}][{role}] {name} Bounds: {frame}")
                for child in element.AXChildren:
                    walk(child, depth + 1)
            except: pass
        try:
            root = atomacos.AXUIElement.systemWide()
            walk(root, 0)
        except Exception as e: return f"macOS Error: {str(e)}"
        return "\n".join(output) if output else "No UI elements found."

    elif sys.platform == "linux":
        from dogtail import tree
        def walk(node, depth):
            try:
                output.append(f"[{depth}][{node.roleName}] {node.name} Bounds: {node.position}, {node.size}")
                for child in node.children:
                    walk(child, depth + 1)
            except: pass
        try:
            walk(tree.root, 0)
        except Exception as e: return f"Linux Error: {str(e)}"
        return "\n".join(output) if output else "No UI elements found."

    return f"Accessibility tree retrieval not supported on {sys.platform}."

@mcp.tool()
def take_screenshot():
    """Take a screenshot of the active device (Local or ADB) and get {width}x{height}. It requires vision ability, please use a11y tree first."""
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