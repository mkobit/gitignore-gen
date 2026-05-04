# gitfiles-gen

[![CI](https://github.com/mkobit/gitignore-gen/actions/workflows/ci.yml/badge.svg)](https://github.com/mkobit/gitignore-gen/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitfiles-gen)](https://pypi.org/project/gitfiles-gen/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/mkobit/gitignore-gen)

A zero-dependency toolkit to compose configuration files for Git and other VCS.

## Why gitfiles-gen?

Unlike other tools that simply fetch a single template, **gitfiles-gen** allows you to build a sophisticated pipeline of templates, local files, and literal text—all processed in strict left-to-right order.

- **Sequential Pipeline**: Compose multiple sources (GitHub, local dirs, archives) in a single command.
- **Zero Runtime Dependencies**: Single-file core using only the Python standard library.
- **High Integrity**: 100% test coverage and strict type safety.
- **Visual Feedback**: Search and preview templates with dry-run support.

## Installation

### Ephemeral usage (No install required)
```bash
SCRIPT_URL="https://gist.github.com/mkobit/gitignore-gen/raw/gitignore_gen.py"
curl -sSfL $SCRIPT_URL | python3 - gitignore generate Python macOS --output .gitignore
```

### via uv
```bash
uvx gitfiles-gen gitignore generate Python
```

## Usage Examples

### Searching & Listing
```bash
# Search for templates with visual feedback
gitfiles-gen gitignore search --include-regex '.*Go.*'

# List all available templates from the default repo
gitfiles-gen gitignore ls
```

### Generating & Dry-run
```bash
# Preview what would be selected without writing any files
gitfiles-gen gitignore generate Python macOS --dry-run

# Generate a combined file for a typical project
gitfiles-gen gitignore generate Python macOS Windows --output .gitignore
```

### Advanced Pipeline
Interleave local templates with upstream ones:
```bash
gitfiles-gen gitignore generate \
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
python3 -c "$SCRIPT_SCRIPT" gitignore generate $(python3 -c "$SCRIPT_SCRIPT" gitignore ls | fzf --multi)
```

## Storage & caching
Repository archives (.tar.gz) are stored locally to avoid redundant downloads.
The default location is `$XDG_CACHE_HOME/gitfiles-gen` or `~/.cache/gitfiles-gen`.
In restricted environments, it falls back to `/tmp/gitfiles-gen`.

*Note: This tool does not automatically purge old archives. To reclaim space, manually delete the cache directory.*
