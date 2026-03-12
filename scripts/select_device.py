from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import set_selected_serial


parser = argparse.ArgumentParser(description="Select the active device for later scripts.")
parser.add_argument("--serial", default="local", help="ADB serial, or 'local' to target the current computer")
args = parser.parse_args()

selected = set_selected_serial(args.serial)
print(f"Active target: {selected}")
