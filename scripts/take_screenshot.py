from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_runtime import take_screenshot as runtime_take_screenshot


def main():
    parser = argparse.ArgumentParser(description="Take a screenshot and optionally perform OCR.")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR text recognition using PaddleOCR")
    args = parser.parse_args()
    
    result = runtime_take_screenshot(ocr=args.ocr)
    print(result)


if __name__ == "__main__":
    main()
