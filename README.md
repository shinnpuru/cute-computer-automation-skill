# Cute (CompUTEr automation) Skill Deployment Guide

This repository is an OpenClaw Agent Skill for GUI automation on the local computer and on Android devices connected through ADB.

This README is written as an execution manual so that both humans and coding agents can deploy it without guessing.

## Goal

Deploy this repository as an OpenClaw Skill named `cute-automation`, then verify that OpenClaw can discover and use it.

## Download source

Clone the repository from GitHub instead of downloading a zip archive.

- Repository: `https://github.com/shinnpuru/cute-mcp.git`

Human workflow:

1. git clone the repository
2. navigate into the cloned directory

Agent workflow:

1. git clone `https://github.com/shinnpuru/cute-mcp.git` into a temporary working directory
2. navigate into the cloned directory

Expected result:

- the cloned directory contains `SKILL.md`, `skill_runtime.py`, `scripts/`, and `pyproject.toml`

## Skill contents

Required runtime files:

```text
SKILL.md
skill_runtime.py
scripts/
    adb_list_devices.py
    click.py
    drag_or_swipe.py
    get_a11y_tree.py
    list_apps.py
    mouse_move.py
    press_key.py
    run_app.py
    select_device.py
    take_screenshot.py
    type_text.py
    wait.py
pyproject.toml
```

## Prerequisites

Install these before deploying:

- Python `3.10+`
- `uv` recommended
- `adb` only if Android automation is needed
- OpenClaw with Skill discovery enabled

## Deployment options

Choose one location:

### Option A: Personal skill

Use this when the skill should be available in all projects for the current user.

- Target directory: `~/.openclaw/skills/cute-automation/`

### Option B: Project skill

Use this when the skill should be available only inside one repository.

- Target directory: `.openclaw/skills/cute-automation/`

## Deployment procedure

### Step 1: Clone the repository into the skill directory

Requirement:

- the final directory itself must contain `SKILL.md` at its root

Correct result:

```text
<skill-dir>/
├── SKILL.md
├── skill_runtime.py
├── scripts/
└── pyproject.toml
```

Windows example for personal install:

```powershell
$target = Join-Path $HOME ".openclaw/skills/cute-automation"
git clone https://github.com/shinnpuru/cute-mcp.git "$target"
```

Unix example for personal install:

```bash
target_dir="$HOME/.openclaw/skills/cute-automation"
git clone https://github.com/shinnpuru/cute-mcp.git "$target_dir"
```

Project-local example:

```powershell
$target = "<repo>\.openclaw\skills\cute-automation"
git clone https://github.com/shinnpuru/cute-mcp.git "$target"
```

Unix project-local example:

```bash
target_dir="<repo>/.openclaw/skills/cute-automation"
git clone https://github.com/shinnpuru/cute-mcp.git "$target_dir"
```

### Step 2: Install Python dependencies

Run inside the deployed skill directory:

```bash
uv sync
```

Windows PowerShell (recommended before `uv` commands):

```powershell
$env:PYTHONUTF8='1'
uv sync
```

Expected outcome:

- `pyautogui`, `adbutils`, `uiautomator2`, and platform-specific packages become importable

### Step 3: Verify the skill files are complete

Check these conditions:

- `SKILL.md` exists
- `scripts/select_device.py` exists
- `scripts/get_a11y_tree.py` exists
- `skill_runtime.py` exists
- `pyproject.toml` exists

If any of the files above are missing, deployment is incomplete.

### Step 4: Verify the Python scripts run

Run these commands from the skill directory:

```bash
uv run python scripts/select_device.py --serial local
uv run python scripts/wait.py 0
```

Windows PowerShell example:

```powershell
$env:PYTHONUTF8='1'
uv run python scripts/select_device.py --serial local
uv run python scripts/wait.py 0
```

Expected output pattern:

- `Active target: local`
- `Waited 0.00s`

### Step 5: Verify OpenClaw can see the skill

In OpenClaw, use either of these checks:

- ask: `What skills are available?`
- invoke directly: `/cute-automation`

Expected outcome:

- OpenClaw lists or recognizes the `cute-automation` skill

If OpenClaw does not see it:

1. confirm the directory name is `cute-automation`
2. confirm `SKILL.md` is at the skill root, not nested one level deeper
3. restart OpenClaw or refresh the session
4. verify the skill is in either `~/.openclaw/skills/` or `.openclaw/skills/`

## Standard runtime pattern for agents

When the skill is active, use this operating order:

1. select target device
2. inspect UI tree
3. take screenshot if needed
4. perform one action
5. wait at least one second
6. re-check state before the next action

## Canonical commands

Use `${OPENCLAW_SKILL_DIR}` when the skill is invoked by OpenClaw.

### Local machine

```bash
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/select_device.py" --serial local
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/get_a11y_tree.py"
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/click.py" --x 400 --y 300
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/wait.py" 1
```

### Android

```bash
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/adb_list_devices.py"
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/select_device.py" --serial <adb-serial>
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/get_a11y_tree.py"
uv --directory "${OPENCLAW_SKILL_DIR}" run python "${OPENCLAW_SKILL_DIR}/scripts/press_key.py" home
```

## Agent-readable deployment checklist

An agent can follow this checklist exactly:

1. choose install scope: personal or project
2. git clone `https://github.com/shinnpuru/cute-mcp.git` into target directory named `cute-automation`
3. ensure `SKILL.md` is at the cloned root
4. run `uv sync` in the cloned directory
5. run `uv run python scripts/select_device.py --serial local`
6. run `uv run python scripts/wait.py 0`
7. confirm expected outputs appear
8. start OpenClaw and verify `/cute-automation` is available

## Update

To update the skill to the latest version:

1. navigate to the skill directory
2. run `git pull` to fetch the latest changes
3. run `uv sync` to update dependencies if needed

Windows PowerShell example:

```powershell
cd "$HOME\.openclaw\skills\cute-automation"
git pull
uv sync
```

Unix example:

```bash
cd "$HOME/.openclaw/skills/cute-automation"
git pull
uv sync
```

## Notes

- `skill_runtime.py` stores the selected ADB device in `.cute_skill_state.json`
- screenshots are written to `screenshots/`
- both of those paths are safe to ignore in version control
- the detailed runtime instructions for the agent remain in `SKILL.md`