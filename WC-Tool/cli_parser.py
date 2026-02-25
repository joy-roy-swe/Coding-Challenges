"""
cli_parser.py — Parses command-line arguments and flags.
"""
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        prog="mywc",
        description="A Python clone of the Unix wc command."
    )

    parser.add_argument("-l", action="store_true", help="Print line count")
    parser.add_argument("-w", action="store_true", help="Print word count")
    parser.add_argument("-c", action="store_true", help="Print byte count")
    parser.add_argument("-m", action="store_true", help="Print character count")
    parser.add_argument("-L", action="store_true", help="Print length of longest line")
    parser.add_argument("files", nargs="*", help="Input file(s). Reads from stdin if omitted.")

    args = parser.parse_args()

    flags = {
        "lines": args.l,
        "words": args.w,
        "bytes": args.c,
        "chars": args.m,
        "max_line_length": args.L,
    }

    # Default: show lines, words, bytes when no flags given
    if not any(flags.values()):
        flags["lines"] = True
        flags["words"] = True
        flags["bytes"] = True

    return flags, args.files
