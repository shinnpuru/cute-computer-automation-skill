from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import type_text


parser = argparse.ArgumentParser(description="Type text locally or on the selected Android device.")
parser.add_argument("text", help="Text to type")
parser.add_argument("--interval", type=float, default=0.05)
args = parser.parse_args()

print(type_text(args.text, args.interval))
