#!/bin/bash
# genieacs/install/build.sh - Build full GenieACS stack + MCP wrapper
set -e
set -o pipefail
GENIEACS_DIR="/root/poc/genieacs"
cd "$(dirname "$0")/.." # Go up from install/ to project root

echo "=== GenieACS Build Script ==="

# System deps
echo "--- Installing system dependencies ---"
apt-get update -qq
apt-get install -y -qq curl wget git gnupg

# Install bun
echo "--- Installing bun ---"
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.local/bin:$PATH"

export PATH="$HOME/.local/bin:$PATH"

# Clone GenieACS if not exists
if [ ! -d "$GENIEACS_DIR/genieacs" ]; then
    echo "--- Cloning GenieACS ---"
    mkdir -p "$GENIEACS_DIR"
    git clone https://github.com/nickysemenza/genieacs.git "$GENIEACS_DIR/genieacs"
fi

cd "$GENIEACS_DIR/genieacs"

# Install MongoDB binaries
echo "--- Installing MongoDB ---"
if ! command -v mongod &> /dev/null; then
    curl -LsSf https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel80-7.0.5.tgz -o /tmp/mongo.tgz
    tar -xzf /tmp/mongo.tgz -C /tmp
    mkdir -p bin/lib
    cp /tmp/mongodb-linux-x86_64-rhel80-7.0.5/bin/* bin/lib/ 2>/dev/null || true
    rm -f /tmp/mongo.tgz
fi

# Install Redis
echo "--- Installing Redis ---"
if ! command -v redis-server &> /dev/null; then
    cd /tmp
    curl -LsSf https://github.com/redis/redis/archive/refs/tags/7.2.4.tar.gz -o redis.tar.gz
    tar -xzf redis.tar.gz
    cd redis-7.2.4
    make -j$(nproc) BUILD_TLS=no
    cp src/redis-server src/redis-cli "$GENIEACS_DIR/genieacs/bin/"
    cd - > /dev/null
fi

# Install GenieACS npm packages
echo "--- Installing GenieACS npm packages ---"
bun install --silent

# Create genieacs env file
cat <<'EOT' > genieacs.env
GENIEACS_MONGODB_CONNECTION_URL=mongodb://127.0.0.1:27017/genieacs
GENIEACS_REDIS_CONNECTION_URL=redis://127.0.0.1:6379/0
GENIEACS_CWMP_PORT=7547
GENIEACS_NBI_PORT=7557
GENIEACS_FS_PORT=7567
GENIEACS_UI_PORT=3000
GENIEACS_UI_JWT_SECRET=mcp_secret_key_change_me
EOT

# Create logs dir
mkdir -p logs data/db

# MCP wrapper venv
echo "--- Building MCP wrapper ---"
cd /root/genieacs
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv pip install --quiet fastmcp httpx python-dotenv

echo "=== Build complete ==="