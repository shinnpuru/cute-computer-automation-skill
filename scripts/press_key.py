from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import press_key


parser = argparse.ArgumentParser(description="Press a key locally or send an Android keyevent.")
parser.add_argument("key", help="Examples: enter, tab, home, back")
parser.add_argument("--times", type=int, default=1)
args = parser.parse_args()

print(press_key(args.key, args.times))
