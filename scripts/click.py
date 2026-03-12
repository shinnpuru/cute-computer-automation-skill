from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import click


parser = argparse.ArgumentParser(description="Click locally or tap on the selected Android device.")
parser.add_argument("--x", type=int, required=True)
parser.add_argument("--y", type=int, required=True)
parser.add_argument("--button", default="left")
parser.add_argument("--clicks", type=int, default=1)
args = parser.parse_args()

print(click(args.x, args.y, args.button, args.clicks))
