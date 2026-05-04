#!/bin/bash
# GenieACS MCP Installer - Location Agnostic
set -e

# Configuration
REPO_URL="https://github.com/WaffleWhip/mcp-network-access.git"
APP_NAME="genieacs"
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

# 2. Determine Target Directory
if [ -f "server.py" ] && [ -d "src" ]; then
    TARGET_DIR=$(pwd)
    echo "--- Local source detected at $TARGET_DIR ---"
else
    TARGET_DIR="/root/poc/$APP_NAME"
    echo "--- Defaulting target to $TARGET_DIR ---"
fi

# 3. Existing Installation Check
if systemctl is-active --quiet $SERVICE_NAME; then
    CURRENT_WD=$(systemctl cat $SERVICE_NAME | grep WorkingDirectory | cut -d'=' -f2)
    echo "WARNING: GenieACS MCP service is already running."
    echo "Current Location: $CURRENT_WD"
    echo "Target Location:  $TARGET_DIR"
    echo ""
    echo "What would you like to do?"
    echo "1) Reinstall (Stop existing and install in $TARGET_DIR)"
    echo "2) Cancel"
    
    if [ -c /dev/tty ]; then
        read -p "Select an option [1-2]: " choice < /dev/tty
    else
        echo "--- Non-interactive session, defaulting to Reinstall ---"
        choice="1"
    fi

    case $choice in
        1)
            echo "--- Stopping existing service ---"
            systemctl stop $SERVICE_NAME 2>/dev/null || true
            systemctl disable $SERVICE_NAME 2>/dev/null || true
            ;;
        *)
            echo "Installation cancelled."
            exit 0
            ;;
    esac
fi

# 4. Source Logic (Fetch if needed)
if [ ! -f "$TARGET_DIR/server.py" ]; then
    mkdir -p "$TARGET_DIR"
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

cd "$TARGET_DIR"

# 5. Build Logic
echo "--- Installing system dependencies ---"
apt-get update -qq
apt-get install -y -qq curl wget git gnupg binutils xz-utils libssl-dev redis-server

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
    echo "--- Installing MongoDB ---"
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
    echo "--- Building environment ---"
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    uv venv .venv
    source .venv/bin/activate
    uv pip install --quiet fastmcp httpx python-dotenv
fi

mkdir -p genieacs/logs genieacs/data/db

# 6. Port Cleanup
echo "--- Cleaning up port $PORT ---"
STALE_PIDS=$(lsof -t -i:$PORT 2>/dev/null || true)
[ -n "$STALE_PIDS" ] && kill -9 $STALE_PIDS 2>/dev/null || true

GENIEACS_PORTS="7547 7557 7567 3000"
for p in $GENIEACS_PORTS; do
    STALE=$(lsof -t -i:$p 2>/dev/null || true)
    [ -n "$STALE" ] && kill -9 $STALE 2>/dev/null || true
done

# 7. Systemd Unit (inline startup, no external scripts)
# Determine actual script dir at runtime using PID
SCRIPT_DIR=$(cd /root/poc/genieacs && pwd)
cat << EOT > /tmp/genieacs-start.sh
#!/bin/bash
WDIR="$SCRIPT_DIR"
GENIEACS_DIR="\$WDIR/genieacs"
export LD_LIBRARY_PATH="\$GENIEACS_DIR/bin/lib:\$LD_LIBRARY_PATH"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:\$HOME/.bun/bin"

# Start MongoDB
[ -f "\$GENIEACS_DIR/bin/lib/mongod" ] && \$GENIEACS_DIR/bin/lib/mongod --dbpath \$GENIEACS_DIR/data/db --port 27017 --logpath \$GENIEACS_DIR/logs/mongo.log --fork --logappend || true
/bin/sleep 3

# Start Redis (skip if already running)
if ! /usr/bin/redis-cli ping >/dev/null 2>&1; then
    /usr/bin/redis-server --port 6379 --daemonize yes --logfile \$GENIEACS_DIR/logs/redis.log 2>/dev/null || true
fi
/bin/sleep 2

# Start GenieACS Services
cd "\$GENIEACS_DIR"
. genieacs.env
BUN_BIN="/root/.bun/bin/bun"
nohup \$BUN_BIN x genieacs-cwmp > \$GENIEACS_DIR/logs/cwmp.log 2>&1 &
nohup \$BUN_BIN x genieacs-nbi > \$GENIEACS_DIR/logs/nbi.log 2>&1 &
nohup \$BUN_BIN x genieacs-fs > \$GENIEACS_DIR/logs/fs.log 2>&1 &
nohup \$BUN_BIN x genieacs-ui > \$GENIEACS_DIR/logs/ui.log 2>&1 &
/bin/sleep 10

# Start MCP Server
cd /root/poc/genieacs
exec /root/poc/genieacs/.venv/bin/python server.py
EOT
chmod +x /tmp/genieacs-start.sh

echo "--- Installing systemd service ---"
cat <<EOT > /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=GenieACS MCP Server
After=network.target redis-server.service

[Service]
Type=simple
User=root
WorkingDirectory=$TARGET_DIR
ExecStart=/bin/bash /tmp/genieacs-start.sh
Restart=always
RestartSec=5
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:\$HOME/.bun/bin"
Environment="HOME=root"

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 8. Verification
echo "--- Verifying Service ---"
sleep 15
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "Success: GenieACS MCP is running on port $PORT."
else
    echo "Error: GenieACS MCP failed to start."
    exit 1
fi
