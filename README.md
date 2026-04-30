# gitignore-gen

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

## Features
- Smart template selection (short names, full paths, regex)
- Local source support (directories and archives)
- Concurrent processing via asyncio
- Order-preserving composition
- automatic GITHUB_TOKEN authentication
