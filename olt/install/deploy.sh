#!/bin/bash
# olt/install/deploy.sh
cd "$(dirname "$0")/.." # Go to root folder

echo "--- Preparing Python Environment ---"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

. .venv/bin/activate
echo "--- Installing Dependencies ---"
pip install -q --upgrade pip
pip install -q fastmcp telnetlib3

echo "--- Starting OLT Driver MCP Server ---"
exec python server.py
