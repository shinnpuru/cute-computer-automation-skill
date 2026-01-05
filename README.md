# CUTE-MCP: Computer Use AutomaTEd

This project implements a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides tools for automating GUI interactions on both local machines and Android devices via ADB.

## Features

- **Multi-Platform Support**: Works on Windows, macOS, and Linux.
- **Local GUI Control**: Move mouse, click, drag, type text, and take screenshots.
- **Android Control**: Tap, swipe, type, and take screenshots on connected Android devices`.
- **Accessibility(a11y) Tree Support**: Extract UI hierarchies to identify elements, significantly saving tokens and improving accuracy.
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

## Steps to Automate

1. **Start the Server**: Set the MCP command in your agent system as follows. Also ensure your ADB device is connected and in debugging mode if you plan to use Android tools.

<details>
<summary><b>Using with Claude Desktop or Gemini</b></summary>

To use this server with Claude Desktop or Gemini, add the following to your `config.json`: 

```json
{
  "mcpServers": {
    "cute_mcp": {
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
<summary><b>Using with Cursor or Cherry Studio</b></summary>

1. Open **MCP Settings**.
2. Click **+ Add New MCP Server**.
3. Set the name to `cute_mcp`.
4. Set the type to `stdio`.
5. Paste the following command:
   `uv --directory /path/to/cute_mcp run cute_mcp.py`
</details>

2. **Local Action**: "Use cute mcp to move the mouse to the Windows button and right-click."
3. **Android Action**: "Use cute mcp to list my ADB devices, select the first one, and press the Home button."


## Available Tools

### Device Management
- `adb_list_devices`: List all connected ADB devices.
- `select_device`: Switch the active device. Pass a serial for ADB, or `null` for local machine.

### Interaction Functions
These tools work on both the local machine and the selected ADB device.

- `mouse_move`: Move the mouse cursor (Local only).
- `click`: Click or Tap at (x, y).
- `drag_or_swipe`: Drag (Local) or Swipe (ADB) from (x1, y1) to (x2, y2).
- `type_text`: Type text on the active device.
- `press_key`: Press a specific key or keyevent (e.g., 'ENTER', 'HOME').

### App Functions

- `list_apps`: List installed applications.
- `run_app`: Start an application by its ID or name.

### Vision Functions

- `get_a11y_tree`: Get the accessibility tree of the current screen (Android, Windows, macOS, or Linux).
- `take_screenshot`: Capture a screenshot and return the image with its dimensions.