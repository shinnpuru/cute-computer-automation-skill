from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import list_adb_devices


if __name__ == "__main__":
    print(json.dumps(list_adb_devices(), ensure_ascii=False, indent=2))
