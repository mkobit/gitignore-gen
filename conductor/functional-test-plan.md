# Objective
Implement functional testing using a local copy of the `github/gitignore` repository to prevent network requests during tests, and establish a robust local/CI fixture mechanism.

# Key Files & Context
- `.github/workflows/ci.yml`
- `tests/conftest.py`
- `tests/functional/test_cli.py`
- `tests/unit/test_selection.py`

# Implementation Steps
1.  **Test Reorganization**:
    - Move existing `tests/test_selection.py` to `tests/unit/`.
    - Create `tests/functional/` for CLI integration tests.
2.  **Pytest Fixture (`tests/conftest.py`)**:
    - Create a `session`-scoped fixture `templates_dir`.
    - The fixture checks if `tests/fixtures/gitignore` exists.
    - If it does NOT exist (e.g., local developer running tests for the first time), the fixture downloads the tarball for a specific pinned SHA of `github/gitignore` and extracts it to that directory, then yields the `Path`.
    - If it DOES exist, it simply yields the `Path` (zero network requests).
3.  **CI Update (`.github/workflows/ci.yml`)**:
    - Add a step to `test` job using `actions/checkout` to clone `github/gitignore` into `tests/fixtures/gitignore`.
    - Pin this checkout to the same SHA used by the fixture.
    - This ensures CI is completely deterministic and tests run immediately without network overhead during the test phase.
4.  **Functional Tests (`tests/functional/test_cli.py`)**:
    - Write tests using the `subprocess` module or importing `main`/`async_main` to run the CLI.
    - Tests will use `--local-dir {templates_dir}`.
    - Verify basic generation (e.g., `Python`), listing (`ls`), and output combinations.
5.  **Clean up**:
    - Ignore `tests/fixtures/` in `.gitignore`.

# Verification
- Run `uv run pytest tests/` locally to ensure the auto-download works and tests pass.
- Run it a second time to ensure the cache is hit and no download happens.
- Push to CI and verify the `actions/checkout` step seeds the directory successfully and tests pass.