#!/bin/bash
# databases/install/build.sh - Install dependencies
set -e
cd "$(dirname "$0")/.." # Go up from install/ to project root

# Install system dependencies if missing
if ! command -v uv &> /dev/null; then
    echo "--- Installing system dependencies ---"
    apt-get update -qq
    apt-get install -y -qq curl
    echo "--- Installing uv locally ---"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "--- Creating venv and installing dependencies ---"
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install --quiet fastmcp

echo "--- Build complete ---"