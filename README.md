# gitignore-gen

[![CI](https://github.com/mkobit/gitignore-gen/actions/workflows/ci.yml/badge.svg)](https://github.com/mkobit/gitignore-gen/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitignore-gen)](https://pypi.org/project/gitignore-gen/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A zero-dependency tool to compose .gitignore files from remote template repositories.

## Installation

### Ephemeral usage
```bash
GIST_URL="https://gist.github.com/mkobit/gitignore-gen/raw/gitignore_gen.py"
curl -sSfL $GIST_URL | python3 - generate Python macOS Windows Node --output .gitignore
```

### via uv
```bash
uvx gitignore-gen generate Python
```

## Usage Examples

### Listing templates
```bash
# List all available templates
gitignore-gen ls

# List templates matching a regex
gitignore-gen ls --include-regex '.*Python.*'
```

### Generating files
```bash
# Generate a combined file for a typical project
gitignore-gen generate Python macOS Windows Node --output .gitignore

# Appending to an existing file
gitignore-gen generate macOS >> .gitignore
```

### Interactive selection
Highly recommended for a great user experience:
```bash
# 1. Store the script in a variable to avoid multiple downloads
GIST_SCRIPT=$(curl -sSfL $GIST_URL)
# 2. Select interactively using fzf and generate
python3 -c "$GIST_SCRIPT" generate $(python3 -c "$GIST_SCRIPT" ls | fzf --multi)
```

## Features
- **Smart selection**: Supports short names, full paths, and regular expressions.
- **Local sources**: Use templates from a local directory or archive for offline workflows.
- **Concurrent processing**: Built on `asyncio` for fast retrieval and composition.
- **Order-preserving**: Templates appear in the exact order you specify them.
- **Zero dependencies**: Only uses the Python standard library at runtime.
- **Automatic Auth**: Uses `GITHUB_TOKEN` automatically if available to bypass rate limits.

## Storage & caching
Repository archives (.tar.gz) are stored locally to avoid redundant downloads.
The default location is `$XDG_CACHE_HOME/gitignore-gen` or `~/.cache/gitignore-gen`.
In restricted environments, it falls back to `/tmp/gitignore-gen`.

*Note: This tool does not automatically purge old archives. To reclaim space, manually delete the cache directory.*
