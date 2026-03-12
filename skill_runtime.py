from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
STATE_FILE = ROOT_DIR / ".cute_skill_state.json"
SCREENSHOT_DIR = ROOT_DIR / "screenshots"


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {"adb_serial": None}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"adb_serial": None}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def normalize_serial(serial: str | None) -> str | None:
    if serial is None:
        return None

    value = serial.strip()
    if not value or value.lower() in {"local", "none", "null"}:
        return None
    return value


def get_selected_serial() -> str | None:
    return normalize_serial(_load_state().get("adb_serial"))


def set_selected_serial(serial: str | None) -> str:
    normalized = normalize_serial(serial)
    _save_state({"adb_serial": normalized})
    return normalized or "local"


def get_adb_device():
    serial = get_selected_serial()
    if not serial:
        return None

    import uiautomator2 as u2

    return u2.connect(serial)


def list_adb_devices() -> list[dict[str, str]]:
    import adbutils

    return [{"serial": device.serial, "state": device.state} for device in adbutils.adb.list()]


def require_local() -> None:
    if get_selected_serial():
        raise RuntimeError("This action only works on the local machine. Run select_device.py --serial local first.")


def _pyautogui():
    import pyautogui

    return pyautogui


def mouse_move(x: int, y: int, duration: float = 0.1) -> str:
    require_local()
    pyautogui = _pyautogui()
    pyautogui.moveTo(x, y, duration=duration)
    return f"Local: moved mouse to ({x}, {y}) in {duration:.2f}s"


def click(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    device = get_adb_device()
    if device:
        device.click(x, y)
        return f"ADB: tapped ({x}, {y})"

    pyautogui = _pyautogui()
    pyautogui.click(x=x, y=y, clicks=clicks, button=button)
    return f"Local: clicked {button} at ({x}, {y}) x{clicks}"


def drag_or_swipe(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> str:
    device = get_adb_device()
    if device:
        device.swipe(x1, y1, x2, y2, duration=duration)
        return f"ADB: swiped ({x1}, {y1}) -> ({x2}, {y2}) in {duration:.2f}s"

    pyautogui = _pyautogui()
    pyautogui.moveTo(x1, y1)
    pyautogui.dragTo(x2, y2, duration=duration)
    return f"Local: dragged ({x1}, {y1}) -> ({x2}, {y2}) in {duration:.2f}s"


def type_text(text: str, interval: float = 0.05) -> str:
    device = get_adb_device()
    if device:
        device.send_keys(text)
        return f"ADB: typed text ({len(text)} chars)"

    pyautogui = _pyautogui()
    pyautogui.write(text, interval=interval)
    return f"Local: typed text ({len(text)} chars)"


def press_key(key: str, times: int = 1) -> str:
    device = get_adb_device()
    if device:
        for _ in range(times):
            device.keyevent(key)
        return f"ADB: sent keyevent {key} x{times}"

    pyautogui = _pyautogui()
    for _ in range(times):
        pyautogui.press(key)
    return f"Local: pressed {key} x{times}"


def list_apps() -> str:
    device = get_adb_device()
    if device:
        return "\n".join(device.app_list())

    if sys.platform == "win32":
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-StartApps | Sort-Object Name | ForEach-Object { \"$($_.Name)`t$($_.AppID)\" }",
        ]
        return subprocess.check_output(command, text=True)

    if sys.platform == "darwin":
        return subprocess.check_output(["ls", "/Applications"], text=True)

    if sys.platform == "linux":
        return subprocess.check_output(["ls", "/usr/share/applications"], text=True)

    raise RuntimeError(f"list_apps is not supported on {sys.platform}")


def run_app(app_id: str) -> str:
    device = get_adb_device()
    if device:
        device.app_start(app_id)
        return f"ADB: started {app_id}"

    if sys.platform == "win32":
        os.startfile(app_id)
        return f"Windows: started {app_id}"

    if sys.platform == "darwin":
        subprocess.run(["open", "-a", app_id], check=True)
        return f"macOS: started {app_id}"

    if sys.platform == "linux":
        subprocess.run(["xdg-open", app_id], check=True)
        return f"Linux: started {app_id}"

    raise RuntimeError(f"run_app is not supported on {sys.platform}")


def get_a11y_tree(max_depth: int | None = None, scope: str | None = None) -> str:
    if max_depth is not None and max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    device = get_adb_device()
    output: list[str] = []
    node_count = 0
    scope_matched = False if scope else True  # If no scope, match all

    def _clean(value) -> str:
        text = "" if value is None else str(value)
        text = " ".join(text.split())
        return text if text else "No Name"

    def _clean_optional(value) -> str:
        text = "" if value is None else str(value)
        text = " ".join(text.split())
        return text

    def _matches_scope(node_id: str, name: str, role: str = "") -> bool:
        if not scope:
            return True
        scope_lower = scope.lower()
        return (
            scope_lower in _clean_optional(node_id).lower() or
            scope_lower in _clean_optional(name).lower() or
            scope_lower in _clean_optional(role).lower()
        )

    def _append(depth: int, role: str, name: str, node_id: str = "", bounds: str = "", extras: list[str] | None = None) -> None:
        nonlocal node_count
        node_count += 1
        indent = "  " * depth
        parts = [f"{indent}- [{node_count}] role={_clean(role)}", f'name="{_clean(name)}"']

        cleaned_id = _clean_optional(node_id)
        if cleaned_id:
            parts.append(f'id="{cleaned_id}"')

        cleaned_bounds = _clean_optional(bounds)
        if cleaned_bounds:
            parts.append(f"bounds={cleaned_bounds}")

        if extras:
            extra_values = [item for item in extras if _clean_optional(item)]
            if extra_values:
                parts.append("attrs=" + ", ".join(extra_values))

        output.append(" | ".join(parts))

    if device:
        xml_data = device.dump_hierarchy()
        root = ET.fromstring(xml_data)

        def walk_xml(node, depth: int) -> None:
            nonlocal scope_matched
            node_class = node.get("class", "Unknown")
            text = node.get("text", "")
            description = node.get("content-desc", "")
            name = text or description or "No Name"
            bounds = node.get("bounds", "")
            node_id = node.get("resource-id", "")
            extras = [
                f'clickable={node.get("clickable", "")}',
                f'enabled={node.get("enabled", "")}',
                f'focused={node.get("focused", "")}',
                f'selected={node.get("selected", "")}',
            ]
            
            # Check if this node matches the scope
            if not scope_matched and _matches_scope(node_id, name, node_class):
                scope_matched = True
                _append(depth, node_class, name, node_id=node_id, bounds=bounds, extras=extras)
                if max_depth is not None and depth >= max_depth:
                    return
                for child in node:
                    walk_xml(child, depth + 1)
                scope_matched = False if scope else True  # Reset for siblings if scope was set
                return
            
            # If scope already matched, continue traversing children
            if scope_matched:
                _append(depth, node_class, name, node_id=node_id, bounds=bounds, extras=extras)
                if max_depth is not None and depth >= max_depth:
                    return
                for child in node:
                    walk_xml(child, depth + 1)
            else:
                # Keep searching for scope match
                for child in node:
                    walk_xml(child, depth)

        walk_xml(root, 0)
        if not output:
            if scope:
                return f"No UI elements found matching scope: {scope}"
            return "No UI elements found."

        serial = get_selected_serial() or "unknown"
        header = f"A11Y_TREE source=android serial={serial} nodes={node_count} scope={scope or 'root'}"
        return "\n".join([header, *output])

    if sys.platform == "win32":
        import uiautomation as auto

        def walk(control, depth: int) -> None:
            nonlocal scope_matched
            name = control.Name or "No Name"
            rect = control.BoundingRectangle
            control_type = control.ControlTypeName
            node_id = control.AutomationId
            extras = [
                f'class={_clean_optional(getattr(control, "ClassName", ""))}',
                f'offscreen={_clean_optional(getattr(control, "IsOffscreen", ""))}',
            ]
            
            # Check if this node matches the scope
            if not scope_matched and _matches_scope(node_id, name, control_type):
                scope_matched = True
                _append(
                    depth,
                    control_type,
                    name,
                    node_id=node_id,
                    bounds=str(rect),
                    extras=extras,
                )
                if max_depth is not None and depth >= max_depth:
                    return
                for child in control.GetChildren():
                    walk(child, depth + 1)
                scope_matched = False if scope else True  # Reset for siblings if scope was set
                return
            
            # If scope already matched, continue traversing children
            if scope_matched:
                _append(
                    depth,
                    control_type,
                    name,
                    node_id=node_id,
                    bounds=str(rect),
                    extras=extras,
                )
                if max_depth is not None and depth >= max_depth:
                    return
                for child in control.GetChildren():
                    walk(child, depth + 1)
            else:
                # Keep searching for scope match
                for child in control.GetChildren():
                    walk(child, depth)

        root = auto.GetRootControl()
        walk(root, 0)
        if not output:
            if scope:
                return f"No UI elements found matching scope: {scope}"
            return "No UI elements found."

        header = f"A11Y_TREE source=local platform=win32 nodes={node_count} scope={scope or 'root'}"
        return "\n".join([header, *output])

    if sys.platform == "darwin":
        import atomacos

        def walk(element, depth: int) -> None:
            nonlocal scope_matched
            try:
                role = element.AXRole
                name = element.AXTitle or element.AXDescription or "No Name"
                frame = element.AXFrame
                node_id = getattr(element, "AXIdentifier", "")
                
                # Check if this node matches the scope
                if not scope_matched and _matches_scope(node_id, name, role):
                    scope_matched = True
                    _append(depth, role, name, bounds=str(frame))
                    if max_depth is not None and depth >= max_depth:
                        return
                    for child in element.AXChildren:
                        walk(child, depth + 1)
                    scope_matched = False if scope else True
                    return
                
                # If scope already matched, continue traversing children
                if scope_matched:
                    _append(depth, role, name, bounds=str(frame))
                    if max_depth is not None and depth >= max_depth:
                        return
                    for child in element.AXChildren:
                        walk(child, depth + 1)
                else:
                    # Keep searching for scope match
                    for child in element.AXChildren:
                        walk(child, depth)
            except Exception:
                return

        root = atomacos.AXUIElement.systemWide()
        walk(root, 0)
        if not output:
            if scope:
                return f"No UI elements found matching scope: {scope}"
            return "No UI elements found."

        header = f"A11Y_TREE source=local platform=darwin nodes={node_count} scope={scope or 'root'}"
        return "\n".join([header, *output])

    if sys.platform == "linux":
        from dogtail import tree

        def walk(node, depth: int) -> None:
            nonlocal scope_matched
            try:
                role = node.roleName
                name = node.name
                node_id = getattr(node, "id", "")
                
                # Check if this node matches the scope
                if not scope_matched and _matches_scope(node_id, name, role):
                    scope_matched = True
                    _append(depth, role, name, bounds=f"{node.position}, {node.size}")
                    if max_depth is not None and depth >= max_depth:
                        return
                    for child in node.children:
                        walk(child, depth + 1)
                    scope_matched = False if scope else True
                    return
                
                # If scope already matched, continue traversing children
                if scope_matched:
                    _append(depth, role, name, bounds=f"{node.position}, {node.size}")
                    if max_depth is not None and depth >= max_depth:
                        return
                    for child in node.children:
                        walk(child, depth + 1)
                else:
                    # Keep searching for scope match
                    for child in node.children:
                        walk(child, depth)
            except Exception:
                return

        walk(tree.root, 0)
        if not output:
            if scope:
                return f"No UI elements found matching scope: {scope}"
            return "No UI elements found."

        header = f"A11Y_TREE source=local platform=linux nodes={node_count} scope={scope or 'root'}"
        return "\n".join([header, *output])

    raise RuntimeError(f"Accessibility tree retrieval is not supported on {sys.platform}")


def take_screenshot() -> str:
    device = get_adb_device()
    if device:
        image = device.screenshot()
    else:
        pyautogui = _pyautogui()
        image = pyautogui.screenshot()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = SCREENSHOT_DIR / f"screenshot_{timestamp}.png"
    image.save(filename)
    width, height = image.size
    return f"Saved screenshot to {filename} ({width}x{height})"


def wait(seconds: float) -> str:
    time.sleep(seconds)
    return f"Waited {seconds:.2f}s"
