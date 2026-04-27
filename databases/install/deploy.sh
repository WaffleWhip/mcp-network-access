#!/bin/bash
# databases/install/deploy.sh
cd "$(dirname "$0")/.." # Go to root folder

echo "--- Preparing Python Environment ---"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

. .venv/bin/activate
echo "--- Installing Dependencies ---"
pip install -q --upgrade pip
pip install -q fastmcp

# Ensure storage structure exists
mkdir -p storage/olt storage/ont skills

echo "--- Starting Database MCP Server ---"
exec python server.py
