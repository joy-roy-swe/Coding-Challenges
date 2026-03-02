# mywc — A Python `wc` Clone

A command-line tool that replicates the Unix `wc` command. Reads from files or `stdin` and outputs line, word, character, and byte counts.

---

## Project Structure

```
WC-Tool/
├── main.py              # Entry point
├── cli_parser.py        # Argument & flag parsing
├── input_reader.py      # Chunked file / stdin reader
├── controller.py        # Orchestration layer
├── processor.py         # Core counting logic (pure functions)
├── processor_state.py   # WcContext — inter-chunk state
├── result.py            # Result dataclass
├── output_formatter.py  # Aligned output & totals
├── errors.py            # Custom exceptions
├── requirements.txt
├── Design.MD
└── Task_list.MD
```

---

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
# Default (lines, words, bytes)
python main.py file.txt

# Specific flags
python main.py -l file.txt          # line count only
python main.py -w file.txt          # word count only
python main.py -c file.txt          # byte count only
python main.py -m file.txt          # character count only
python main.py -L file.txt          # longest line length
python main.py -l -w file.txt       # combined flags
python main.py -lw file.txt         # shorthand combined

# Multiple files (prints totals row)
python main.py file1.txt file2.txt

# Read from stdin
cat file.txt | python main.py
echo "hello world" | python main.py -w
```

---

## Running Tests

```bash
pytest
```

---

## Supported Flags

| Flag | Description |
|------|-------------|
| `-l` | Number of newline characters (line count) |
| `-w` | Number of words (whitespace-delimited) |
| `-c` | Byte count |
| `-m` | Character count (Unicode-aware) |
| `-L` | Length of the longest line |
| *(none)* | Default: lines + words + bytes |

---

## Design Highlights

- **Byte-first reading** — opens files as binary (`rb`) for accurate `-c` counts
- **8KB chunk streaming** — never loads the full file into memory; safe for GB-scale files
- **Cross-chunk word boundary tracking** — via `WcContext.prev_ended_mid_word`
- **Per-file error handling** — one bad file doesn't stop the rest
- **Pure processor** — no I/O in counting logic; fully unit-testable

See [`Design.MD`](Design.MD) for the full architecture document.
