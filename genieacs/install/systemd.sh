#!/bin/bash
# genieacs/install/systemd.sh - Install service
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
SERVICE_NAME="mcp-genieacs"

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

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME
