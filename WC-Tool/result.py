"""
result.py — Data model for per-file wc counts.
"""
from dataclasses import dataclass


@dataclass
class Result:
    file_name: str
    lines: int = 0
    words: int = 0
    bytes: int = 0
    chars: int = 0
    max_line_length: int = 0
