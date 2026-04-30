# Objective
Refactor the CLI into a subcommand-based architecture (`ls` and `generate`), share template selection logic across both, clean up implementation-specific docstrings, and add advanced selection examples.

# Key Files & Context
- `gitignore_gen.py` (standalone gist script)

# Implementation Steps
1.  **Docstring Cleanup**:
    - Remove phrases like "Functional generator", "functional paradigms", and "immutable".
    - Update module docstring with examples of using CLI selection options (e.g., `--include-regex '.*Python.*'`).
2.  **CLI Restructuring (Subcommands)**:
    - Update `_create_parser` to define a global parser with `add_subparsers`.
    - Create a `ls` (or `list`) subcommand: Uses the same selection options but only prints matching paths. If no filters are provided, it lists all templates.
    - Create a `generate` subcommand: Takes the selection options and output options to combine the files.
    - Move `--repo`, `--base-url` (formerly `--repo-url`), and caching flags to a global argument group.
3.  **Logic Separation**:
    - Refactor `_process_archive` to handle both subcommands elegantly.
    - If `command == "ls"`, run `_select_templates` (if filters exist, else all members) and print.
    - If `command == "generate"`, run `_select_templates` and build the output file.
4.  **Verification**:
    - Run `python3 gitignore_gen.py --help` (verify subcommands).
    - Run `python3 gitignore_gen.py ls --include-filename Python` (verify filtering).
    - Run `python3 gitignore_gen.py generate Python --output .gitignore` (verify generation).
    - Run `uvx ruff check ...` and `uvx ty check` to ensure compliance.