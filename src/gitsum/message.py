"""
Module for output (warning messages, etc.)
"""
import sys


def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)
