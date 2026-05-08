#!/usr/bin/env bash
# Example: Composing a .gitignore from multiple sources

# 1. Start with Python and macOS templates from GitHub
# 2. Add a custom header
# 3. Add a local template for the IDE
vcs-gen gitignore generate \
  Python macOS \
  --include-text "# IDE Settings" \
  --include-text ".vscode/" \
  --include-text ".idea/" \
  --output .gitignore

echo "Generated .gitignore"
