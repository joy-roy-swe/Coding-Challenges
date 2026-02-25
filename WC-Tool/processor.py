"""
processor.py — Core counting logic. Pure functions, no I/O.
"""
from processor_state import WcContext
from result import Result


def analyze(stream, flags, file_name="") -> Result:
    """
    Iterates over a byte-chunk stream and accumulates counts.
    Returns a Result with all requested counts populated.
    """
    ctx = WcContext()
    ctx.accumulated.file_name = file_name

    for chunk in stream:
        # --- Byte count ---
        if flags.get("bytes"):
            ctx.accumulated.bytes += len(chunk)

        # Decode for text-based counts
        text = chunk.decode("utf-8", errors="replace")

        # --- Line count ---
        if flags.get("lines"):
            ctx.accumulated.lines += text.count("\n")

        # --- Word count (with cross-chunk boundary tracking) ---
        if flags.get("words"):
            ctx.accumulated.words += _count_words(text, ctx)

        # --- Character count ---
        if flags.get("chars"):
            ctx.accumulated.chars += len(text)

        # --- Max line length ---
        if flags.get("max_line_length"):
            _update_max_line_length(text, ctx)

    # If byte count not explicitly via flag but needed, it was already collected
    return ctx.accumulated


def _count_words(text: str, ctx: WcContext) -> int:
    """
    Counts words in `text`, using ctx.prev_ended_mid_word to handle
    words split across chunk boundaries.
    """
    count = 0
    in_word = ctx.prev_ended_mid_word

    for ch in text:
        if ch.isspace():
            in_word = False
        else:
            if not in_word:
                count += 1
            in_word = True

    ctx.prev_ended_mid_word = in_word
    return count


def _update_max_line_length(text: str, ctx: WcContext):
    """
    Tracks the longest line across chunks using partial_line_buffer.
    """
    lines = text.split("\n")

    # First segment continues the previous partial line
    lines[0] = ctx.partial_line_buffer + lines[0]

    for line in lines[:-1]:
        length = len(line)
        if length > ctx.accumulated.max_line_length:
            ctx.accumulated.max_line_length = length

    # Last segment may be incomplete; carry it forward
    ctx.partial_line_buffer = lines[-1]

    # Flush partial line at very end — caller is responsible for
    # checking after stream exhaustion (handled in analyze via final check)
    ctx.accumulated.max_line_length = max(
        ctx.accumulated.max_line_length,
        len(ctx.partial_line_buffer)
    )
