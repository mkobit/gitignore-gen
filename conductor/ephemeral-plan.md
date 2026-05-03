# Objective
Productionize `gitignore-gen` (renaming to `gitignore-gist` for PyPI), implement a modern release pipeline, convert all tests to `async def`, and establish standard environment setup tools.

# Key Files & Context
- `pyproject.toml`
- `.jules/env_setup.sh`
- `tests/unit/test_selection.py` (convert to async)
- `.github/workflows/release.yml`
- `examples/`

# Implementation Steps
1.  **Rename & Claim Name**:
    - Update `pyproject.toml` to use `name = "gitignore-gist"` (available on PyPI).
2.  **Environment & Locking**:
    - Update `mise.toml` to include `[settings] lock = true`.
    - Run `mise bin` or similar to generate `mise.lock`.
    - Create `.jules/env_setup.sh` modeled after user's workspace, using `uv` for Python and dependency installation.
3.  **Modern Release System**:
    - Adopt `python-semantic-release` (PSR).
    - Configure PSR in `pyproject.toml` to manage versioning via conventional commits.
    - Create `.github/workflows/release.yml` with a `workflow_dispatch` trigger for manual releases.
4.  **Async Test Conversion**:
    - Refactor `tests/unit/test_selection.py` to use `async def` and `@pytest.mark.asyncio`.
5.  **CI Enhancements**:
    - **Coverage**: Add `pytest-cov`, report coverage in CI, and prepare for a Coverage badge.
    - **Single-File Check**: Add a CI step that copies `src/gitignore_gen/cli.py` to a temp location and verifies it runs with zero dependencies.
6.  **README & Examples**:
    - Add GitHub Actions badges (CI status, Coverage).
    - Create an `examples/` directory with a `README.md` showing runnable snippets.
    - Fleshed out examples in main README using the new `gitignore-gist` name.

# Verification
- Run `uv run pytest --cov=src` locally.
- Verify `mise.lock` is generated and tracked.
- Simulate a release dry-run using PSR.
- Verify `.jules/env_setup.sh` correctly initializes a fresh environment.