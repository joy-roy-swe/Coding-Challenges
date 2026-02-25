"""
processor_state.py — Inter-chunk state tracking for the processor.
"""
from dataclasses import dataclass, field
from result import Result


@dataclass
class WcContext:
    prev_ended_mid_word: bool = False      # Was the last char of previous chunk non-whitespace?
    partial_line_buffer: str = ""          # Incomplete line carried over from previous chunk
    accumulated: Result = field(default_factory=lambda: Result(
        file_name="",
        lines=0,
        words=0,
        bytes=0,
        chars=0,
        max_line_length=0,
    ))
