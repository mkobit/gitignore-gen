# gitignore-compose

[![CI](https://github.com/mkobit/gitignore-gen/actions/workflows/ci.yml/badge.svg)](https://github.com/mkobit/gitignore-gen/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitignore-compose)](https://pypi.org/project/gitignore-compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/mkobit/gitignore-gen)

A zero-dependency tool to compose .gitignore files from remote template repositories.

## Why gitignore-compose?

Unlike other tools that simply fetch a single template, **gitignore-compose** allows you to build a sophisticated pipeline of templates, local files, and literal text—all processed in strict left-to-right order.

- **Sequential Pipeline**: Compose multiple sources (GitHub, local dirs, archives) in a single command.
- **Zero Runtime Dependencies**: Single-file core using only the Python standard library.
- **High Integrity**: 100% test coverage and strict type safety.
- **Visual Feedback**: Search and preview templates with dry-run support.

## Installation

### Ephemeral usage (No install required)
```bash
SCRIPT_URL="https://gist.github.com/mkobit/gitignore-gen/raw/gitignore_gen.py"
curl -sSfL $SCRIPT_URL | python3 - generate Python macOS --output .gitignore
```

### via uv
```bash
uvx gitignore-compose generate Python
```

## Usage Examples

### Searching & Listing
```bash
# Search for templates with visual feedback
gitignore-compose search --include-regex '.*Go.*'

# List all available templates from the default repo
gitignore-compose ls
```

### Generating & Dry-run
```bash
# Preview what would be selected without writing any files
gitignore-compose generate Python macOS --dry-run

# Generate a combined file for a typical project
gitignore-compose generate Python macOS Windows --output .gitignore
```

### Advanced Pipeline
Interleave local templates with upstream ones:
```bash
gitignore-compose generate \
  --repo github/gitignore Python macOS \
  --include-text "# Developer Customizations" \
  --local-dir ./my-templates Python
```

## Interactive selection
Highly recommended for a great user experience:
```bash
# 1. Store the script in a variable
SCRIPT_SCRIPT=$(curl -sSfL $SCRIPT_URL)
# 2. Select interactively using fzf and generate
python3 -c "$SCRIPT_SCRIPT" generate $(python3 -c "$SCRIPT_SCRIPT" ls | fzf --multi)
```

## Coverage Report
The project maintains a strict quality gate with 100% test coverage.

| File | Statements | Missing | Coverage |
|------|------------|---------|----------|
| `src/gitignore_gen/cli.py` | 413 | 0 | 100% |
| **Total** | **414** | **0** | **100%** |

## Storage & caching
Repository archives (.tar.gz) are stored locally to avoid redundant downloads.
The default location is `$XDG_CACHE_HOME/gitignore-gen` or `~/.cache/gitignore-gen`.
In restricted environments, it falls back to `/tmp/gitignore-gen`.

*Note: This tool does not automatically purge old archives. To reclaim space, manually delete the cache directory.*
