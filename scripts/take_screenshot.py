from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import take_screenshot


if __name__ == "__main__":
    print(take_screenshot())
