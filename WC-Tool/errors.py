"""
errors.py — Custom exception types for mywc.
"""


class MywcFileNotFoundError(FileNotFoundError):
    """Raised when a given file path does not exist."""
    pass


class MywcPermissionError(PermissionError):
    """Raised when a file cannot be read due to permissions."""
    pass


class MywcEncodingError(UnicodeDecodeError):
    """Raised when a file cannot be decoded with the expected encoding."""
    pass
