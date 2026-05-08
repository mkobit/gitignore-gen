#!/usr/bin/env bash
# Example: Using vcs-gen for .gitattributes

# Since there is no default repo for gitattributes, 
# you can use your own or just inject text.

vcs-gen gitattributes generate \
  --include-text "# Handle line endings" \
  --include-text "* text=auto" \
  --include-text "# Force binary files" \
  --include-text "*.png binary" \
  --include-text "*.jpg binary" \
  --output .gitattributes

echo "Generated .gitattributes"
