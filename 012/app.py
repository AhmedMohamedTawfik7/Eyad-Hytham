"""Compatibility entry point; run the repository's cross-platform launcher."""

import runpy
from pathlib import Path


if __name__ == "__main__":
    launcher = Path(__file__).resolve().parents[1] / "app.py"
    runpy.run_path(str(launcher), run_name="__main__")
