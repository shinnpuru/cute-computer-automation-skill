from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import get_a11y_tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get accessibility tree")
    parser.add_argument("--depth", type=int, default=None, help="Maximum tree depth to include (0 = root only)")
    parser.add_argument("--scope", type=str, default=None, help="Scope to filter nodes by id, name, or role (case-insensitive substring match)")
    args = parser.parse_args()

    print(get_a11y_tree(max_depth=args.depth, scope=args.scope))
