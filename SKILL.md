---
name: cute-automation
description: Automate the local computer or a connected Android device from Claude. Use when you need GUI clicks, typing, key presses, screenshots, accessibility tree inspection, app launching, or Android ADB interactions.
disable-model-invocation: true
allowed-tools: Bash(uv *), Bash(python *), Read
argument-hint: [task]
---

# Cute Automation

This directory is a Claude Agent Skill. It replaces the old FastMCP server with direct Python scripts that Claude can run.

## What this skill can do

- Control the local computer: move the mouse, click, drag, type, press keys, list apps, launch apps.
- Control a connected Android device through ADB: list devices, select a device, tap, swipe, type, press Android keyevents, inspect UI hierarchy, take screenshots.
- Persist the current target device across script calls using a small state file, so later commands keep using the same local/ADB target.

## Files

- `scripts/adb_list_devices.py`: list connected Android devices.
- `scripts/select_device.py`: set the current target to an ADB serial or `local`.
- `scripts/mouse_move.py`: move the local mouse.
- `scripts/click.py`: click locally or tap on Android.
- `scripts/drag_or_swipe.py`: drag locally or swipe on Android.
- `scripts/type_text.py`: type text locally or on Android.
- `scripts/press_key.py`: press a local key or Android keyevent.
- `scripts/list_apps.py`: list apps for the active target.
- `scripts/run_app.py`: launch a local app or Android package.
- `scripts/get_a11y_tree.py`: dump the accessibility/UI tree. Supports `--depth` and `--scope` options to filter results.
- `scripts/take_screenshot.py`: save a screenshot under `screenshots/`. Supports `--ocr` flag for text recognition using EasyOCR.
- `scripts/wait.py`: sleep between GUI actions.

## Operating rules

1. For Android work, run `adb_list_devices.py` first, then `select_device.py --serial <serial>`.
2. For local work, run `select_device.py --serial local` first.
3. **ALWAYS use `get_a11y_tree.py` first** to inspect the UI state. This is the primary method for understanding the screen.
4. **Only use `take_screenshot.py` when explicitly requested by the user.** Do not take screenshots automatically.
5. After every UI action, run `wait.py 1` or longer before the next action.
6. Prefer the smallest action that completes the step, then re-check the state.

## Command pattern

Run scripts from any working directory with the skill directory variable:

```bash
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/select_device.py" --serial local
```

## Common examples

### Local machine

```bash
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/select_device.py" --serial local
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/get_a11y_tree.py"
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/get_a11y_tree.py" --depth 3 --scope "Calculator"
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/click.py" --x 200 --y 300
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/wait.py" 1
```

### Android

```bash
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/adb_list_devices.py"
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/select_device.py" --serial emulator-5554
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/get_a11y_tree.py"
uv --directory "${CLAUDE_SKILL_DIR}" run python "${CLAUDE_SKILL_DIR}/scripts/press_key.py" home
```

## OCR Text Recognition (Optional)

The `take_screenshot.py` script supports OCR text recognition using EasyOCR.

**Prerequisites:**
```bash
uv pip install easyocr
```

Or install with the ocr extra:
```bash
uv sync --extra ocr
```

**Usage:**
```bash
# Take screenshot with OCR
python scripts/take_screenshot.py --ocr
```

The OCR result will include:
- Screenshot file path
- Recognized text with confidence scores
- Support for Chinese and English text

## Accessibility Tree Scope Filtering

The `get_a11y_tree.py` script supports filtering by scope to return only a specific node and its children:

```bash
# Get the entire tree (default)
python scripts/get_a11y_tree.py

# Limit depth only
python scripts/get_a11y_tree.py --depth 3

# Filter by scope (case-insensitive substring match on id, name, or role)
python scripts/get_a11y_tree.py --scope "Calculator"
python scripts/get_a11y_tree.py --scope "FileExplorerCommandBar" --depth 5
python scripts/get_a11y_tree.py --scope "回收站" --depth 3
```

The `--scope` parameter matches against:
- **id**: AutomationId (Windows), resource-id (Android)
- **name**: Control/element name or text
- **role**: Control type or class name

When scope is specified, the tree traversal starts from the first matching node and returns only that node and its descendants.

## When handling a user request

1. Identify whether the target is local or Android.
2. Ensure the correct target is selected.
3. **Always use `get_a11y_tree.py` first** to inspect the current UI state.
4. **Only take a screenshot with `take_screenshot.py` if the user explicitly asks for it.**
5. Execute the requested action with one of the scripts.
6. Wait briefly and verify the new state before chaining more actions.
