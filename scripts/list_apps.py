from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import list_apps


if __name__ == "__main__":
    print(list_apps())
