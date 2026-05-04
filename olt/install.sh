#!/bin/bash
# olt/install.sh - Flexible OLT MCP Installer
set -e

# Configuration
REPO_URL="https://github.com/WaffleWhip/mcp-network-access.git"
TARGET_DIR=$(pwd)
SERVICE_NAME="mcp-olt"
PORT=8002

echo "=========================================="
echo "   OLT MCP Setup & Deployment"
echo "=========================================="

# 1. Root Check
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root"
  exit 1
fi

# 2. Existing Installation Check (Interactive)
if systemctl is-active --quiet $SERVICE_NAME; then
    CURRENT_WD=$(systemctl cat $SERVICE_NAME | grep WorkingDirectory | cut -d'=' -f2)
    echo "⚠️  WARNING: OLT MCP service is already running."
    echo "Current Location: $CURRENT_WD"
    echo ""
    echo "What would you like to do?"
    echo "1) Fresh Install (DELETE existing and install in $TARGET_DIR)"
    echo "2) Cancel"
    read -p "Select an option [1-2]: " choice

    case $choice in
        1)
            echo "--- Stopping existing service... ---"
            systemctl stop $SERVICE_NAME 2>/dev/null || true
            systemctl disable $SERVICE_NAME 2>/dev/null || true
            ;;
        *)
            echo "Installation cancelled."
            exit 0
            ;;
    esac
fi

# 3. Source Logic
if [ ! -f "server.py" ]; then
    echo "--- Fetching source from GitHub ---"
    apt-get update -qq && apt-get install -y -qq git curl
    TEMP_DIR=$(mktemp -d)
    git clone --quiet $REPO_URL "$TEMP_DIR"
    if [ -d "$TEMP_DIR/olt" ]; then
        cp -r "$TEMP_DIR/olt/." "$TARGET_DIR/"
        rm -rf "$TEMP_DIR"
    else
        echo "Error: 'olt' directory not found in repository."
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

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
Description=OLT MCP Server
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
    echo "✅ Success: OLT MCP is running on port $PORT."
    echo "Location: $TARGET_DIR"
else
    echo "❌ Error: OLT MCP failed to start."
    exit 1
fi
