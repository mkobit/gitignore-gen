# Objective
Refactor `_select_templates` to respect the order of user arguments, ensure all documentation uses sentence case, and provide a clean `test_outputs` verification.

# Key Files & Context
- `gitignore_gen.py`

# Implementation Steps
1.  **Sentence Case Enforcement**:
    - Review the module docstring, argument help texts, and parser descriptions.
    - Ensure all text strictly adheres to sentence case ("Generator to compose..." -> "Generator to compose...").
2.  **Order-Preserving Template Selection**:
    - Update `_select_templates` to iterate through the user's provided patterns sequentially, rather than iterating through the archive members.
    - For each pattern provided via positional `templates` or `--include-*` flags, scan the `members` list, find the match(es), and append them to `selected`.
    - This ensures that if the user provides `Python macOS`, the matching members for `Python` are appended first, followed by the matching members for `macOS`.
3.  **Local Testing Strategy**:
    - Clear the `test_outputs/` directory.
    - Run the initial cached generation to confirm successful retrieval.
    - Re-run the tests (generating files like `initial.gitignore`, `standard.gitignore`, `lexicographic.gitignore`, and `clean.gitignore`) to verify the new sequence logic correctly applies `args_order`.

# Verification
- The output of `test_outputs/standard.gitignore` should display templates in the exact order requested (`Python` then `macOS` then `Windows` then `Docker`).
- Run the strict `ruff` and `ty` commands to ensure all changes remain compliant.