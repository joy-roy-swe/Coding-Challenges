# Architecture Design: `wc` CLI Tool (Python)

---

## 1. Overview

A command-line tool that replicates the Unix `wc` command. It reads input from files or `stdin`, and outputs statistics like line count, word count, character count, and byte count.

---

## 2. Supported Flags

| Flag | Feature | Description |
|------|---------|-------------|
| `-l` | Line Count | Number of newline characters |
| `-w` | Word Count | Words delimited by whitespace |
| `-c` | Byte Count | Size in bytes |
| `-m` | Character Count | Number of characters (encoding-aware) |
| `-L` | Max Line Length | Length of the longest line |
| *(none)* | Default | Show lines, words, and bytes (like real `wc`) |

---

## 3. Input Methods

| Method | Example |
|--------|---------|
| Single file | `mywc file.txt` |
| Multiple files | `mywc file1.txt file2.txt` |
| Stdin (pipe) | `cat file.txt \| mywc` |
| Stdin (interactive) | `mywc` then type, end with `Ctrl+D` |

---

## 4. High-Level Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  CLI Parser  │────▶│  Input       │────▶│  Controller  │────▶│  Processor   │────▶│  Output      │
│  (args/flags)│     │  Reader      │     │ (orchestrate)│     │  (counting)  │     │  Formatter   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

| Layer | Responsibility |
|-------|---------------|
| CLI Parser | Parse command-line arguments: flags + file paths |
| Input Reader | Open files or read from `stdin`, handle encoding & errors |
| Controller | Orchestrate iteration over files, collect `Result` objects |
| Processor | Core counting logic (lines, words, chars, bytes) via streaming |
| Output Formatter | Format results into aligned columns, print to `stdout` |

---

## 5. Module / Class Structure

```
project/
├── main.py                  # Entry point — parse args, delegate to controller
│
├── cli_parser.py
│   ├── Parse flags (-l, -w, -c, -m, -L)
│   ├── Extract file paths
│   └── Detect stdin mode
│
├── input_reader.py
│   ├── read_file(path) → byte stream (chunked)
│   ├── read_stdin() → byte stream (chunked)
│   └── Handle errors (file not found, permissions, encoding)
│
├── controller.py            # NEW: Orchestration layer
│   ├── run(flags, file_paths) → list[Result]
│   ├── Iterates over files, invokes reader + processor per file
│   └── Collects and returns all Result objects for formatting
│
├── processor.py             # Pure logic — no I/O, no side effects
│   ├── analyze(stream, flags) → Result   # accepts a byte stream/generator
│   ├── _count_lines(chunk, state) → int
│   ├── _count_words(chunk, state) → int
│   ├── _count_bytes(chunk) → int
│   ├── _count_chars(chunk) → int
│   └── _max_line_length(chunk, state) → int
│
├── processor_state.py       # NEW: Inter-chunk state tracking
│   └── WcContext dataclass
│       ├── prev_ended_mid_word: bool    # tracks word split across chunks
│       ├── partial_line_buffer: str     # tracks line split across chunks
│       └── accumulated: Result          # running totals
│
├── result.py                # Data model
│   ├── file_name: str
│   ├── lines: int
│   ├── words: int
│   ├── bytes: int
│   ├── chars: int
│   └── max_line_length: int
│
├── output_formatter.py
│   ├── format_single(result, flags) → str
│   ├── format_multiple(results, flags) → str   # includes totals row
│   └── Column alignment logic
│
└── errors.py
    ├── FileNotFoundError
    ├── PermissionError
    └── EncodingError
```

---

## 6. Data Flow

```
CLI Input:  mywc -l -w file1.txt file2.txt

Step 1 — CLI Parser
   ├── flags = { lines: true, words: true }
   └── files = ["file1.txt", "file2.txt"]

Step 2 — Controller
   └── Iterates over each file path, delegates to reader + processor

Step 3 — Input Reader
   ├── file1.txt → chunked byte stream
   └── file2.txt → chunked byte stream

Step 4 — Processor  (per file, streaming)
   ├── file1 → Result { lines: 2, words: 4 }
   └── file2 → Result { lines: 1, words: 2 }

Step 5 — Output Formatter
   ├── "  2   4  file1.txt"
   ├── "  1   2  file2.txt"
   └── "  3   6  total"
```

---

## 7. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Read as bytes first | Needed for accurate `-c` byte count; decode to text for `-w`, `-m`, `-l` |
| Stream processing for large files | Don't load entire file into memory — read in 8KB chunks |
| Processor accepts a stream, not full content | Unifies streaming and in-memory paths; resolves API contradiction |
| `WcContext` carries inter-chunk state | Handles word/line boundaries that span chunk edges |
| Processor is pure logic | No I/O, no side effects — easy to unit test |
| Separate formatter | Output formatting is independent of counting logic |
| Explicit `controller.py` | Clear orchestration layer — `main` stays thin |
| Error handling per file | One bad file shouldn't crash the whole run (like real `wc`) |
| Default behavior | No flags = show lines + words + bytes (matches real `wc`) |
| Encoding default: UTF-8 | Best match for modern systems; add `--encoding` flag in future |

---

## 8. Edge Cases to Handle

| Case | Behavior |
|------|----------|
| Empty file | All counts = 0 |
| File with no trailing newline | Last line still counts for words/chars, but not as a newline |
| Binary files | Count bytes (`-c`) only; attempt decode with `errors='replace'` for other flags; emit a warning |
| Very large files (GBs) | Chunk-based processing (8KB buffer), never fully loaded into memory |
| Unicode (emoji, CJK) | `-m` counts code points; `-c` counts raw bytes |
| File not found | Print error to `stderr`, continue with remaining files |
| No read permission | Print error to `stderr`, continue |
| Empty stdin | All counts = 0 |
| Mixed flags | e.g., `-lw` or `-l -w` both work |
| Word split across chunk boundary | Tracked via `WcContext.prev_ended_mid_word` |

---

## 9. Streaming Strategy (for Large Files)

```
Open file as byte stream (8KB chunks)
  │
  ├── Read chunk
  │     ├── Accumulate byte count (len of raw chunk)
  │     ├── Decode chunk to text (UTF-8, errors='replace')
  │     ├── Count newlines in chunk
  │     ├── Count words — check WcContext.prev_ended_mid_word for boundary
  │     ├── Count characters (code points)
  │     └── Update WcContext with new state
  │
  ├── Repeat until EOF
  │
  └── Return accumulated Result from WcContext
```

> ⚠️ **Tricky part:** A word can be split across two chunks. `WcContext.prev_ended_mid_word` tracks whether the previous chunk ended mid-word so the next chunk correctly continues or starts a new word count.

---

## 10. Testing Strategy

| Test Type | What to Test |
|-----------|-------------|
| Unit tests | Each counting function independently with known inputs |
| Integration tests | Full pipeline: args → read → process → output |
| Edge case tests | Empty files, Unicode, binary, huge files |
| Golden / comparison tests | Run real `wc` and `mywc` on the same files; byte-for-byte output match |
| Stdin tests | Pipe input and verify results |
| Chunk boundary tests | Craft inputs where words/lines straddle the 8KB chunk boundary |

---

## 11. Language-Specific Notes (Python 🐍)

- Use `argparse` for CLI parsing
- Use `open(file, 'rb')` and read in chunks for byte-level access
- `sys.stdin.buffer` for binary stdin
- `chunk.decode('utf-8', errors='replace')` for safe text decoding
- `len(text.encode('utf-8'))` for byte count from text
- Use `@dataclass` for `Result` and `WcContext`

---

## 12. Future Extensibility

| Feature | Description |
|---------|-------------|
| Parallel processing | Process multiple files concurrently with `threading` or `asyncio` |
| Recursive mode (`-r`) | Count all files in a directory tree |
| Custom delimiters | Count "words" by custom separators |
| Output formats | JSON, CSV output for scripting |
| Config file | `.mywcrc` for default flags |
| Glob support | `mywc *.txt` |
| `--encoding` flag | Let users specify input encoding (default: UTF-8) |

---
