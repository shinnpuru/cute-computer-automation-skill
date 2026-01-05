# CompUTEr Use MCP Server

This project implements a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides tools for automating GUI interactions on both local machines and Android devices via ADB.

## Features

- **Multi-Platform Support**: Works on Windows, macOS, and Linux.
- **Local GUI Control**: Move mouse, click, drag, type text, and take screenshots using `pyautogui`.
- **Android Control**: Tap, swipe, type, and take screenshots on connected Android devices using `adbutils`.
- **Device Management**: List and select specific ADB devices.

## Supported Platforms

- **Windows**: Full support for GUI automation and app management.
- **macOS**: Full support for GUI automation and app management.
- **Linux**: Support for GUI automation and app management (requires `xdg-utils`).
- **Android**: Support via ADB for any connected device with USB debugging enabled.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended)
- For Android control: ADB installed and devices connected with USB debugging enabled.

## Installation

## Tutorial: 

<details>
<summary><b>Using with Claude Desktop or Gemini</b></summary>

To use this server with Claude Desktop or Gemini, add the following to your `config.json`: 

```json
{
  "mcpServers": {
    "gui-automation": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/cute_mcp",
        "run",
        "cute_mcp.py"
      ]
    }
  }
}
```
</details>

<details>
<summary><b>Using with Cursor</b></summary>

1. Open **Cursor Settings**.
2. Navigate to **Features > MCP**.
3. Click **+ Add New MCP Server**.
4. Set the name to `cute_mcp`.
5. Set the type to `command`.
6. Paste the following command:
   `uv --directory /path/to/cute_mcp run cute_mcp.py`
</details>


### Steps to Automate
1. **Start the Server**: Ensure your ADB device is connected if you plan to use Android tools.
2. **Ask Claude**: "Take a screenshot of my screen and tell me what you see."
3. **Local Action**: "Move the mouse to the center of the screen and right-click."
4. **Android Action**: "List my ADB devices, select the first one, and press the Home button."

## Available Tools

### Device Management
- `adb_list_devices`: List all connected ADB devices.
- `select_device`: Switch the active device. Pass a serial for ADB, or `null` for local machine.

### Unified Interaction Tools
These tools work on both the local machine and the selected ADB device.

- `mouse_move`: Move the mouse cursor (Local only).
- `click`: Click or Tap at (x, y).
- `drag_or_swipe`: Drag (Local) or Swipe (ADB) from (x1, y1) to (x2, y2).
- `type_text`: Type text on the active device.
- `press_key`: Press a specific key or keyevent (e.g., 'ENTER', 'HOME').
- `list_apps`: List installed applications.
- `run_app`: Start an application by its ID or name.
- `take_screenshot`: Capture a screenshot and return the image with its dimensions.