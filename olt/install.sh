#!/bin/bash
# OLT MCP Installer - Systemd + UV
set -e

# Configuration
APP_NAME="olt"
SERVICE_NAME="mcp-olt"
PORT=8002
REPO_URL="https://github.com/WaffleWhip/mcp-network-access.git"

echo "=========================================="
echo "   OLT MCP Setup & Deployment"
echo "=========================================="

# 1. Root Check
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root"
  exit 1
fi

# 2. Determine Target Directory
if [ -f "server.py" ] && [ -d "src" ]; then
    SOURCE_DIR=$(pwd)
    TARGET_DIR=$(pwd)
    echo "--- Local source detected at $SOURCE_DIR ---"
else
    TARGET_DIR="/root/poc/$APP_NAME"
    echo "--- Using default target: $TARGET_DIR ---"
fi

mkdir -p "$TARGET_DIR"

# 3. Stop existing service and kill any process on port
echo "--- Stopping existing service and cleaning port $PORT ---"
systemctl stop $SERVICE_NAME 2>/dev/null || true
systemctl disable $SERVICE_NAME 2>/dev/null || true
fuser -k $PORT/tcp 2>/dev/null || true
sleep 2

# 4. Fetch from GitHub if target is empty (production install via curl)
if [ ! -f "$TARGET_DIR/server.py" ]; then
    echo "--- Fetching source from GitHub into $TARGET_DIR ---"
    apt-get update -qq && apt-get install -y -qq git curl
    TEMP_DIR=$(mktemp -d)
    git clone --quiet $REPO_URL "$TEMP_DIR"
    if [ -d "$TEMP_DIR/$APP_NAME" ]; then
        cp -r "$TEMP_DIR/$APP_NAME/." "$TARGET_DIR/"
        rm -rf "$TEMP_DIR"
    else
        echo "Error: '$APP_NAME' directory not found in repository."
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# 5. Copy source files if running from local (testing with local files)
if [ -n "$SOURCE_DIR" ] && [ "$SOURCE_DIR" != "$TARGET_DIR" ]; then
    echo "--- Copying local source to $TARGET_DIR ---"
    cp -r "$SOURCE_DIR/." "$TARGET_DIR/"
fi

cd "$TARGET_DIR"

# 6. Environment Setup with UV
echo "--- Setting up Python environment with UV ---"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create venv if not exists or if packages missing
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/python" ]; then
    echo "--- Creating venv ---"
    uv venv .venv
fi

echo "--- Installing dependencies ---"
source .venv/bin/activate
uv pip install --quiet fastmcp telnetlib3 uvicorn

# 7. Systemd Unit
echo "--- Installing systemd service ---"
cat <<EOF > /etc/systemd/system/$SERVICE_NAME.service
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 8. Reload systemd and start
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 9. Verification
echo "--- Verifying Service ---"
sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "=========================================="
    echo "   SUCCESS: OLT MCP is running"
    echo "   Port: $PORT"
    echo "   Location: $TARGET_DIR"
    echo "=========================================="
    systemctl status $SERVICE_NAME --no-pager
else
    echo "Error: OLT MCP failed to start."
    echo "--- Last 20 lines of journal ---"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi
