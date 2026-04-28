#!/bin/bash
# databases/install/start.sh - Start MCP server
set -e
cd "$(dirname "$0")/.." # Go up from install/ to project root

source .venv/bin/activate
echo "--- Starting Database MCP Server ---"
exec python server.py
