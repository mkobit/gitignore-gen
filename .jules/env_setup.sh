#!/usr/bin/env bash
# Jules environment setup for gitignore-gist repository
# Docs: https://jules.google/docs/environment/

set -euo pipefail

echo "Setting up gitignore-gist environment..."

# Diagnostic Info
echo "--- Diagnostic Information ---"
echo "User: $(whoami)"
GIT_COMMIT_HASH=$(git rev-parse HEAD)
GIT_COMMIT_DATE=$(git log -1 --format=%cI)
export GIT_COMMIT_HASH
export GIT_COMMIT_DATE
echo "Git commit hash: ${GIT_COMMIT_HASH}"
echo "Git commit date: ${GIT_COMMIT_DATE}"
echo "------------------------------"

export MISE_DEBUG=1

# Step 1: Install/Setup mise and repo tools.
if ! command -v mise &>/dev/null; then
    echo "Installing mise..."
    curl -s https://mise.run | /usr/bin/env bash
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing tools with mise..."
mise trust
mise install
eval "$(mise activate bash)"
mise doctor

# Step 2: Install python dependencies
echo "Installing python dependencies with uv..."
# Using --frozen to ensure deterministic builds from uv.lock
uv sync --all-packages --frozen

echo "Environment ready"
