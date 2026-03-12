from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import run_app


parser = argparse.ArgumentParser(description="Launch a local app or Android package/activity.")
parser.add_argument("app_id", help="Local app path/name or Android package")
args = parser.parse_args()

print(run_app(args.app_id))
