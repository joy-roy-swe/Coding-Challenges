"""
output_formatter.py — Formats Result objects into aligned columns for stdout.
"""
from result import Result


# Column order (matches real wc output order)
_COLUMN_ORDER = ["lines", "words", "bytes", "chars", "max_line_length"]

_FLAG_KEYS = {
    "lines": "lines",
    "words": "words",
    "bytes": "bytes",
    "chars": "chars",
    "max_line_length": "max_line_length",
}


def _active_fields(flags: dict) -> list:
    """Returns the list of field names to display, in wc column order."""
    return [f for f in _COLUMN_ORDER if flags.get(f)]


def _format_row(result: Result, fields: list, width: int) -> str:
    values = [str(getattr(result, f)).rjust(width) for f in fields]
    parts = " ".join(values)
    if result.file_name:
        return f"{parts} {result.file_name}"
    return parts


def format_single(result: Result, flags: dict) -> str:
    fields = _active_fields(flags)
    max_val = max((getattr(result, f) for f in fields), default=0)
    width = max(len(str(max_val)), 4)
    return _format_row(result, fields, width)


def format_multiple(results: list, flags: dict) -> str:
    fields = _active_fields(flags)

    # Compute totals
    total = Result(file_name="total")
    for r in results:
        for f in fields:
            setattr(total, f, getattr(total, f) + getattr(r, f))

    all_results = results + [total]

    # Determine column width based on largest value
    max_val = max(
        (getattr(r, f) for r in all_results for f in fields),
        default=0
    )
    width = max(len(str(max_val)), 4)

    lines = [_format_row(r, fields, width) for r in all_results]
    return "\n".join(lines)
