#!/usr/bin/env bash
# Example: Using a local directory for templates

# 1. Create a dummy local template directory
mkdir -p my-templates
echo "*.log" > my-templates/Logging.gitignore
echo "*.tmp" >> my-templates/Logging.gitignore

# 2. Use it in the pipeline
vcs-gen gitignore generate \
  Python \
  --local-dir ./my-templates Logging \
  --dry-run

# Cleanup
rm -rf my-templates
