# Objective
Implement a pipeline-based CLI architecture for `gitignore-gen` that guarantees sequential insertion of templates and allows source-specific options (like headers and include patterns) to be applied sequentially from left to right.

# Key Files & Context
- `src/gitignore_gen/cli.py`

# Implementation Steps
1.  **Pipeline Argparse Action**:
    - Create a custom `argparse.Action` called `PipelineAction` that appends a tuple of `(action_type, destination, values, option_string)` to a global `namespace.pipeline` list.
    - This action will be applied to *all* arguments that affect generation state or trigger output (e.g., `--repo`, `--local-dir`, `--include-file`, `--section-header-template`, positional `templates`, `--include-text`, `--include-local-file`).
2.  **Execution Engine (`_do_generate`)**:
    - Initialize a `state` dictionary with default values for headers, repository, ref, base_url, etc.
    - Initialize a `current_source` variable to `None`.
    - Iterate through the `namespace.pipeline` events in order.
    - **State Update Events**: If the event updates a setting (e.g., `--repo "github/gitignore"`, `--section-header-template "### {path} ###"`), update the `state` dictionary.
    - **Source Update Events**: If the event changes the source type (`--local-dir`, `--repo`), close the `current_source`, instantiate the new source using the current `state`, and set it as `current_source`.
    - **Action Events**: If the event is an inclusion request (`--include-regex`, positional template, `--include-text`), use the `current_source` to fetch/match the template, format it using the *current* `state` (headers), and append it to the final output list.
3.  **New Inclusion Types**:
    - Add `--include-text TEXT` to inject literal text (e.g., custom local ignores).
    - Add `--include-local-file PATH` to inject the contents of a specific file.
4.  **Deduplication**:
    - Deduplication will track `(source_label, path)` to allow pulling the same filename from different sources without collision, while preventing duplicate outputs from the same source block.
5.  **Documentation & Examples**:
    - Update the README and `--help` to explain the left-to-right sequential evaluation.

# Verification
- Write a quick test script to verify `argparse` correctly preserves the interleaved order of `nargs="*"` and optional flags when using a custom `Action`.
- Run the full test suite (`uv run pytest tests/`) and strict linting (`uv run ruff check .`, `uv run ty check src/`).
- Perform manual integration tests combining multiple sources and custom text injections.