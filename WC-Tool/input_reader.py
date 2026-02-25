"""
input_reader.py — Reads file or stdin as chunked byte streams.
"""
import sys

CHUNK_SIZE = 8 * 1024  # 8KB


def read_file(path):
    """
    Generator: yields raw byte chunks from a file.
    Raises FileNotFoundError or PermissionError on failure.
    """
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


def read_stdin():
    """
    Generator: yields raw byte chunks from stdin.
    """
    while True:
        chunk = sys.stdin.buffer.read(CHUNK_SIZE)
        if not chunk:
            break
        yield chunk
