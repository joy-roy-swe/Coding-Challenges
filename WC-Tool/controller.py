"""
controller.py — Orchestrates reading, processing, and error handling per file.
"""
import sys
from input_reader import read_file, read_stdin
from processor import analyze
from result import Result


def run(flags: dict, file_paths: list) -> list:
    """
    Processes each file (or stdin) and returns a list of Result objects.
    Errors are printed to stderr and the file is skipped.
    """
    results = []

    if not file_paths:
        # No files given — read from stdin
        stream = read_stdin()
        result = analyze(stream, flags, file_name="")
        results.append(result)
    else:
        for path in file_paths:
            try:
                stream = read_file(path)
                result = analyze(stream, flags, file_name=path)
                results.append(result)
            except FileNotFoundError:
                print(f"mywc: {path}: No such file or directory", file=sys.stderr)
            except PermissionError:
                print(f"mywc: {path}: Permission denied", file=sys.stderr)
            except Exception as e:
                print(f"mywc: {path}: {e}", file=sys.stderr)

    return results
