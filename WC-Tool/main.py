"""
mywc — Entry Point
Parses CLI arguments and delegates to the controller.
"""
from controller import run
from output_formatter import format_single, format_multiple
from cli_parser import parse_args


def main():
    flags, file_paths = parse_args()

    results = run(flags, file_paths)

    if len(results) == 1:
        print(format_single(results[0], flags))
    else:
        print(format_multiple(results, flags))


if __name__ == "__main__":
    main()
