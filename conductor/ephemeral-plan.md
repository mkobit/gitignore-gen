# Objective
Refactor `gitignore_gen.py` to be strictly documented as an ephemeral script, improve code readability by replacing lambdas with typed functions, expand argument help text, and remove versioning.

# Key Files & Context
- `gitignore_gen.py`

# Implementation Steps
1.  **Ephemeral Examples**:
    - Update the module docstring. Remove all examples that assume `gitignore_gen.py` is saved locally.
    - Provide a bash variable approach: `GIST_URL="https://gist.github.com/.../raw/..."`
    - Provide examples using `curl -sL $GIST_URL | python3 - [command] [args]`.
    - Provide the `fzf` interactive example using the ephemeral approach.
2.  **Refactor Selection Logic**:
    - In `_select_templates`, replace the untyped `lambda m: ...` list with well-named, fully typed inner functions (e.g., `def match_path(m: tarfile.TarInfo) -> bool:`).
3.  **Enhance Help Text**:
    - Review every `parser.add_argument` call.
    - Expand the `help` strings to be more descriptive and informative for users running `--help`.
4.  **Remove Versioning**:
    - Delete `parser.add_argument("--version", ...)` from `_create_parser()`.
5.  **Strict Verification**:
    - Run the exact `uvx ruff check ...` command from the header (including all 30+ groups).
    - Run `uvx ruff format`.
    - Run `uvx ty check`.