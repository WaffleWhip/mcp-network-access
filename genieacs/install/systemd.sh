#!/bin/bash
# genieacs/install/systemd.sh - Unified Install & Verification
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
SERVICE_NAME="mcp-genieacs"
PORT=8001

echo "=== Systemd Setup: $SERVICE_NAME (Port $PORT) ==="

# 1. Automatic Build if missing
if [ ! -d "$DIR/.venv" ] || [ ! -f "$DIR/genieacs/bin/lib/mongod" ]; then
    echo "--- Dependencies missing. Running build script... ---"
    bash "$DIR/install/build.sh"
fi

# 2. Kill stale processes on port
echo "--- Cleaning up port $PORT ---"
STALE_PIDS=$(lsof -t -i:$PORT || true)
if [ -n "$STALE_PIDS" ]; then
    echo "Killing stale PIDs: $STALE_PIDS"
    kill -9 $STALE_PIDS || true
fi

# 3. Create Systemd Unit
echo "--- Installing systemd service ---"
cat <<EOT | tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=GenieACS MCP Server
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

# 4. Reload and Start
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 5. Verification
echo "--- Verifying Service ---"
sleep 15
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "Success: $SERVICE_NAME is running."
    ss -tulpn | grep :$PORT || echo "Warning: Port $PORT not listening yet."
else
    echo "Error: $SERVICE_NAME failed to start. Check 'journalctl -u $SERVICE_NAME'"
    exit 1
fi

echo "=== Done ==="
