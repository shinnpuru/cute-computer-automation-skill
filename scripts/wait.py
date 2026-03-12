from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import wait


parser = argparse.ArgumentParser(description="Pause between GUI operations.")
parser.add_argument("seconds", type=float, nargs="?", default=1.0)
args = parser.parse_args()

print(wait(args.seconds))
