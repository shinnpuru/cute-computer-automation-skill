from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import drag_or_swipe


parser = argparse.ArgumentParser(description="Drag locally or swipe on the selected Android device.")
parser.add_argument("--x1", type=int, required=True)
parser.add_argument("--y1", type=int, required=True)
parser.add_argument("--x2", type=int, required=True)
parser.add_argument("--y2", type=int, required=True)
parser.add_argument("--duration", type=float, default=0.5)
args = parser.parse_args()

print(drag_or_swipe(args.x1, args.y1, args.x2, args.y2, args.duration))
