#!/bin/bash
# genieacs/install/systemd.sh
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
SERVICE_NAME="mcp-genieacs"

cat <<EOT | tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=GenieACS MCP Stack
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=/bin/bash $DIR/install/deploy.sh
Restart=always
RestartSec=15
KillMode=process

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME
