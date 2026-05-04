#!/bin/bash
# genieacs/install.sh - One-Line GenieACS MCP Installer
set -e

# Configuration
REPO_URL="https://github.com/WaffleWhip/mcp-network-access.git"
TARGET_DIR=$(pwd)
SERVICE_NAME="mcp-genieacs"
PORT=8001

echo "=========================================="
echo "   GenieACS MCP Setup & Deployment"
echo "=========================================="

# 1. Root Check
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root"
  exit 1
fi

# 2. Existing Installation Check
if systemctl is-active --quiet $SERVICE_NAME; then
    CURRENT_WD=$(systemctl cat $SERVICE_NAME | grep WorkingDirectory | cut -d'=' -f2)
    echo "⚠️  WARNING: GenieACS MCP service is already running."
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
    if [ -d "$TEMP_DIR/genieacs" ]; then
        cp -r "$TEMP_DIR/genieacs/." "$TARGET_DIR/"
        rm -rf "$TEMP_DIR"
    else
        echo "Error: 'genieacs' directory not found in repository."
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# 4. Build Logic (Merged from build.sh)
echo "--- Installing system dependencies ---"
apt-get update -qq
apt-get install -y -qq curl wget git gnupg ar xz-utils libssl-dev redis-server

# Fix libssl1.1 for Debian 13 (required by MongoDB)
if ! dpkg -l | grep -q libssl1.1; then
    echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list
    apt-get update -qq
    apt-get install -y -qq libssl1.1
    rm /etc/apt/sources.list.d/bullseye.list
    apt-get update -qq
fi

# Install bun
if ! command -v bun &> /dev/null && [ ! -f "$HOME/.bun/bin/bun" ]; then
    curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$PATH"

# Setup GenieACS core
if [ ! -d "genieacs" ]; then
    echo "--- Fetching GenieACS core ---"
    mkdir -p genieacs
    curl -LsSf https://github.com/genieacs/genieacs/archive/refs/heads/master.tar.gz | tar xz -C genieacs --strip=1
fi

# Install MongoDB 4.4
mkdir -p genieacs/bin/lib
if [ ! -f "genieacs/bin/lib/mongod" ]; then
    echo "--- Installing MongoDB 4.4 ---"
    curl -LsSf https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2004-4.4.26.tgz -o /tmp/mongo.tgz
    tar -xzf /tmp/mongo.tgz -C /tmp
    cp /tmp/mongodb-linux-x86_64-ubuntu2004-4.4.26/bin/mongod genieacs/bin/lib/
    cp /tmp/mongodb-linux-x86_64-ubuntu2004-4.4.26/bin/mongos genieacs/bin/lib/
fi

# Install npm packages
echo "--- Installing npm packages ---"
cd genieacs && bun install --silent && cd ..

# Setup MCP venv
if [ ! -d ".venv" ]; then
    echo "--- Building MCP environment ---"
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    uv venv .venv
    source .venv/bin/activate
    uv pip install --quiet fastmcp httpx python-dotenv
fi

# Create dirs
mkdir -p genieacs/logs genieacs/data/db

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
Description=GenieACS MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$TARGET_DIR
ExecStart=/bin/bash $TARGET_DIR/start.sh
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
sleep 15
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Success: GenieACS MCP is running on port $PORT."
else
    echo "❌ Error: GenieACS MCP failed to start."
    exit 1
fi
