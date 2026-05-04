#!/bin/bash
# olt/install.sh - Interactive OLT MCP Installer
set -e

# Configuration
REPO_URL="https://github.com/WaffleWhip/mcp-network-access.git"
TARGET_DIR="/root/poc/olt"
SERVICE_NAME="mcp-olt"
PORT=8002

echo "=========================================="
echo "   OLT Manager MCP Setup & Deployment"
echo "=========================================="

# 1. Root Check
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root"
  exit 1
fi

# 2. Existing Installation Check
if [ -d "$TARGET_DIR" ] || systemctl is-active --quiet $SERVICE_NAME; then
    echo "⚠️  WARNING: OLT MCP is already installed or running."
    echo "Current Location: $TARGET_DIR"
    echo ""
    echo "What would you like to do?"
    echo "1) Fresh Install (DELETE everything and start over)"
    echo "2) Cancel"
    read -p "Select an option [1-2]: " choice

    case $choice in
        1)
            echo "--- Removing existing installation... ---"
            # Safety: Check if we are running the script from the directory we are about to delete
            CURRENT_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
            if [[ "$CURRENT_SCRIPT_DIR" == "$TARGET_DIR"* ]]; then
                echo "⚠️  ERROR: Cannot perform Fresh Install while running script from inside $TARGET_DIR."
                echo "Please copy this script to /tmp and run it from there."
                echo "Example: cp install.sh /tmp/ && bash /tmp/install.sh"
                exit 1
            fi
            systemctl stop $SERVICE_NAME 2>/dev/null || true
            systemctl disable $SERVICE_NAME 2>/dev/null || true
            rm -f /etc/systemd/system/$SERVICE_NAME.service
            systemctl daemon-reload
            rm -rf "$TARGET_DIR"
            echo "✓ Cleanup complete."
            ;;
        *)
            echo "Installation cancelled."
            exit 0
            ;;
    esac
fi

# 3. Directory & Source Logic
mkdir -p "$TARGET_DIR"
if [ ! -f "$TARGET_DIR/server.py" ]; then
    echo "--- Fetching source ---"
    if [ -f "server.py" ]; then
        cp -r . "$TARGET_DIR/"
    else
        apt-get update -qq && apt-get install -y -qq git curl
        cd /tmp
        rm -rf mcp-network-access
        git clone --quiet $REPO_URL
        if [ -d "mcp-network-access/olt" ]; then
            cp -r mcp-network-access/olt/. "$TARGET_DIR/"
        else
            echo "Error: 'olt' directory not found in repository."
            exit 1
        fi
    fi
fi

cd "$TARGET_DIR"

# 4. Environment Setup (Venv)
if [ ! -d ".venv" ]; then
    echo "--- Creating Virtual Environment ---"
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    uv venv .venv
    source .venv/bin/activate
    uv pip install fastmcp telnetlib3
fi

# 5. Port Cleanup
echo "--- Cleaning up port $PORT ---"
STALE_PIDS=$(lsof -t -i:$PORT || true)
if [ -n "$STALE_PIDS" ]; then
    kill -9 $STALE_PIDS || true
fi

# 6. Systemd Unit
echo "--- Installing systemd service ---"
cat <<EOT | tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null
[Unit]
Description=OLT Manager MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$TARGET_DIR
ExecStart=$TARGET_DIR/.venv/bin/python server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 7. Verification
echo "--- Verifying Service ---"
sleep 5
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Success: $SERVICE_NAME is running on port $PORT."
else
    echo "❌ Error: $SERVICE_NAME failed to start."
    exit 1
fi
