#!/usr/bin/env python3
"""Repo-local launcher for SupportRAG CLI.

Use this when the package is not installed yet:
  python3 supportrag.py --help
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
sys.path.insert(0, str(CODE))

from cli import main

if __name__ == "__main__":
    raise SystemExit(main())
