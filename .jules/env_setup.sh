#!/bin/bash
set -euo pipefail

echo "Setting up gitignore-gen environment..."

if ! command -v mise &> /dev/null; then
    echo "Error: mise not found. Please install mise first."
    exit 1
fi

echo "Installing tools with mise (isolated)..."
mise trust
MISE_GLOBAL_CONFIG_FILE=/dev/null mise install

echo "Installing dependencies with uv..."
uv sync

echo "Environment ready"
