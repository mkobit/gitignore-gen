# Objective
Add `fzf` integration hooks by making positional arguments smarter, add an `fzf` example to the docstring, and ensure all future linting strictly follows the header arguments.

# Key Files & Context
- `gitignore_gen.py`

# Implementation Steps
1.  **Smart Positional Arguments**:
    - Update `_select_templates` so that positional arguments (`filenames`) intelligently handle `.gitignore` extensions.
    - If a template argument ends with `.gitignore` (which is what `ls` outputs), match it using `m.name.endswith(p)`. If it doesn't, fall back to the existing behavior (`m.name.rsplit("/", 1)[-1] == f"{p}.gitignore"`).
    - This allows passing the output of `ls` directly back into `generate`.
2.  **Documentation Update**:
    - Add an "Interactive Selection" example to the top docstring:
      `python3 gitignore_gen.py generate $(python3 gitignore_gen.py ls | fzf --multi)`
3.  **Strict Linting Protocol**:
    - During the verification phase, explicitly copy and paste the exact `uvx ruff check ...` command found in the file header, including all `--select` arguments and the `# noqa: E501` exception line handling (if applicable in shell).

# Verification
- Run the updated unit test manually using `python3 gitignore_gen.py generate Global/macOS.gitignore Python` to verify both the `.gitignore` path match and the short-name match work seamlessly.
- Run the exact `ruff` and `ty` commands specified in the file's header.