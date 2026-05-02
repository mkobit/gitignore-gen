# Objective
Bootstrap `gitignore-gen` as a robust, zero-runtime-dependency Python project using `asyncio`, managed by `uv` (with `mise` provisioning `uv`), with comprehensive testing and secure GitHub Actions CI. Connect it to the `git@github.com:mkobit/gitignore-gen.git` remote.

# Key Files & Context
- `pyproject.toml`
- `mise.toml`
- `.python-version`
- `src/gitignore_gen/cli.py`
- `tests/unit/test_selection.py`
- `tests/functional/test_cli.py`
- `.github/workflows/ci.yml`

# Implementation Steps
1.  **Repository Initialization**:
    - Initialize a git repository.
    - Add the `git@github.com:mkobit/gitignore-gen.git` remote.
    - Create a `.gitignore` for Python and `uv` artifacts.
2.  **Project Configuration (`pyproject.toml` & `mise.toml`)**:
    - Define a `pyproject.toml` establishing `gitignore-gen` as a command-line tool.
    - Enforce `requires-python = ">=3.10"`.
    - Move all 30+ Ruff linter groups, formatting settings, and `ty`/`pyright` configurations into the `[tool.ruff]` and `[tool.pyright]` sections.
    - Specify dev dependencies: `pytest`, `pytest-asyncio`, `ruff`, `ty`, `pyright`.
    - Create a `mise.toml` to provision `uv` only.
    - Create a `.python-version` file for `uv` to manage the Python environment.
3.  **Code Restructuring & Asyncio (`src/gitignore_gen/cli.py`)**:
    - Move the standalone script to `src/gitignore_gen/cli.py`.
    - Transition the core fetching and execution pipeline to use `asyncio`.
    - Wrap blocking `urllib` network calls and `tarfile` extractions in `asyncio.to_thread` to maintain zero external runtime dependencies while gaining concurrency benefits.
4.  **Testing Framework (`tests/`)**:
    - **Unit Tests**: Validate `TemplateMember` abstractions and `_select_templates` logic independently in `tests/unit/`.
    - **Functional Tests**: Execute the CLI end-to-end in `tests/functional/`.
5.  **Secure CI/CD Setup (`.github/workflows/ci.yml`)**:
    - Create `.github/workflows/ci.yml` using first-party actions pinned to exact SHAs.
    - Matrix testing across Ubuntu/macOS and Python 3.10-3.12 managed via `astral-sh/setup-uv`.

# Verification
- Run `uv sync` to build the environment and install Python.
- Run `uv run ruff check .` and `uv run ty check src/`.
- Run `uv run pytest tests/`.
- Commit and push to the new remote.