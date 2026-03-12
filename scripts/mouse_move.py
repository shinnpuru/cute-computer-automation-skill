from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import mouse_move


parser = argparse.ArgumentParser(description="Move the local mouse cursor.")
parser.add_argument("--x", type=int, required=True)
parser.add_argument("--y", type=int, required=True)
parser.add_argument("--duration", type=float, default=0.1)
args = parser.parse_args()

print(mouse_move(args.x, args.y, args.duration))
