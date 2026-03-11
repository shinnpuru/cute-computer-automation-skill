from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import get_a11y_tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get accessibility tree")
    parser.add_argument("--depth", type=int, default=None, help="Maximum tree depth to include (0 = root only)")
    args = parser.parse_args()

    print(get_a11y_tree(max_depth=args.depth))
