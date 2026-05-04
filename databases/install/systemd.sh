#!/bin/bash
# databases/install/systemd.sh - Independent Database MCP Installer
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
SERVICE_NAME="mcp-databases"
PORT=8003

echo "=== Standalone Setup: $SERVICE_NAME (Port $PORT) ==="

# 1. Environment Setup
if [ ! -d "$DIR/.venv" ]; then
    echo "--- Creating Virtual Environment ---"
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    cd "$DIR"
    uv venv .venv
    source .venv/bin/activate
    uv pip install fastmcp
fi

# 2. Port Cleanup
echo "--- Cleaning up port $PORT ---"
STALE_PIDS=$(lsof -t -i:$PORT || true)
if [ -n "$STALE_PIDS" ]; then
    kill -9 $STALE_PIDS || true
fi

# 3. Systemd Unit
echo "--- Installing systemd service ---"
cat <<EOT | tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=Database MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=/bin/bash $DIR/install/start.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 4. Verification
echo "--- Verifying Service ---"
sleep 5
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "Success: $SERVICE_NAME is running on port $PORT."
else
    echo "Error: $SERVICE_NAME failed to start."
    exit 1
fi
