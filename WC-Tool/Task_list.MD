# WC Tool — Task List

> Track implementation progress here. Update checkboxes as you go.

---

## Phase 1: Project Setup

- [x] Create project directory structure (`main.py`, `cli_parser.py`, etc.)
- [x] Set up a virtual environment (`python -m venv .venv`)
- [x] Create `requirements.txt` (initially empty or with `pytest`)
- [x] Create `README.MD` with usage instructions

---

## Phase 2: CLI Parser (`cli_parser.py`)

- [ ] Parse flags: `-l`, `-w`, `-c`, `-m`, `-L`
- [ ] Support combined flags (e.g., `-lw`)
- [ ] Extract file paths from arguments
- [ ] Detect when no file is given → stdin mode
- [ ] Default behavior: show lines + words + bytes when no flags given

---

## Phase 3: Input Reader (`input_reader.py`)

- [ ] Implement `read_file(path)` — opens file as binary, yields 8KB chunks
- [ ] Implement `read_stdin()` — reads from `sys.stdin.buffer` in chunks
- [ ] Handle `FileNotFoundError` → print to `stderr`, skip file
- [ ] Handle `PermissionError` → print to `stderr`, skip file

---

## Phase 4: Processor State (`processor_state.py`)

- [ ] Define `WcContext` dataclass with:
  - [ ] `prev_ended_mid_word: bool`
  - [ ] `partial_line_buffer: str`
  - [ ] `accumulated: Result`

---

## Phase 5: Processor (`processor.py`)

- [ ] Implement `analyze(stream, flags) → Result` (chunk-based, uses `WcContext`)
- [ ] `_count_bytes(chunk)` — `len(chunk)`
- [ ] `_count_lines(chunk)` — count `\n` characters
- [ ] `_count_words(chunk, state)` — handle word boundary across chunks via `prev_ended_mid_word`
- [ ] `_count_chars(chunk)` — decode with `errors='replace'`, count code points
- [ ] `_max_line_length(chunk, state)` — track max across chunks using `partial_line_buffer`
- [ ] Binary file handling — count bytes; decode with `errors='replace'` for other flags; emit warning

---

## Phase 6: Result Model (`result.py`)

- [ ] Define `Result` dataclass:
  - [ ] `file_name: str`
  - [ ] `lines: int`
  - [ ] `words: int`
  - [ ] `bytes: int`
  - [ ] `chars: int`
  - [ ] `max_line_length: int`

---

## Phase 7: Controller (`controller.py`)

- [ ] Implement `run(flags, file_paths) → list[Result]`
- [ ] Iterate over each file, call reader + processor
- [ ] Handle stdin path when no files given
- [ ] Collect and return all `Result` objects

---

## Phase 8: Output Formatter (`output_formatter.py`)

- [ ] Implement `format_single(result, flags) → str`
- [ ] Implement `format_multiple(results, flags) → str` with totals row
- [ ] Column alignment (right-justified, consistent width)
- [ ] Only print columns for requested flags

---

## Phase 9: Testing

- [ ] Unit tests for each counting function (`processor.py`)
- [ ] Unit tests for `cli_parser.py`
- [ ] Unit tests for `output_formatter.py`
- [ ] Integration test: full pipeline end-to-end
- [ ] Edge case tests:
  - [ ] Empty file
  - [ ] File with no trailing newline
  - [ ] Unicode / emoji / CJK characters
  - [ ] Binary file
  - [ ] Very large file (GB-scale streaming test)
  - [ ] Word split across 8KB chunk boundary
- [ ] Golden tests — compare `mywc` output against real `wc` output on same files
- [ ] Stdin pipe tests

---

## Phase 10: Future / Nice-to-Have

- [ ] `--encoding` flag for custom input encoding
- [ ] Parallel file processing (`threading` / `asyncio`)
- [ ] Recursive mode (`-r`) for directories
- [ ] JSON / CSV output format (`--format json`)
- [ ] Glob support (`mywc *.txt`)
- [ ] Config file (`.mywcrc`) for default flags
