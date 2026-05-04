#!/bin/bash
# genieacs/install/build.sh - Build full GenieACS stack + MCP wrapper
set -e
set -o pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.." # Go up from install/ to project root

echo "=== GenieACS Build Script (Debian 13 Optimized) ==="

# 1. System deps + libssl1.1 for MongoDB
echo "--- Installing system dependencies ---"
apt-get update -qq
apt-get install -y -qq curl wget git gnupg ar xz-utils libssl-dev

# Fix libssl1.1 for Debian 13 (required by MongoDB 4.4/5.0)
if ! dpkg -l | grep -q libssl1.1; then
    echo "--- Installing libssl1.1 (legacy) ---"
    echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list
    apt-get update -qq
    apt-get install -y -qq libssl1.1
    rm /etc/apt/sources.list.d/bullseye.list
    apt-get update -qq
fi

# 2. Install bun
echo "--- Installing bun ---"
if ! command -v bun &> /dev/null && [ ! -f "$HOME/.bun/bin/bun" ]; then
    curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$PATH"

# 3. Clone/Setup GenieACS
if [ ! -d "genieacs" ]; then
    echo "--- Fetching GenieACS ---"
    mkdir -p genieacs
    curl -LsSf https://github.com/genieacs/genieacs/archive/refs/heads/master.tar.gz | tar xz -C genieacs --strip=1
fi

cd genieacs

# 4. Install MongoDB 4.4 (Legacy compat, no AVX requirement)
echo "--- Installing MongoDB 4.4 ---"
mkdir -p bin/lib
if [ ! -f "bin/lib/mongod" ]; then
    curl -LsSf https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2004-4.4.26.tgz -o /tmp/mongo.tgz
    tar -xzf /tmp/mongo.tgz -C /tmp
    cp /tmp/mongodb-linux-x86_64-ubuntu2004-4.4.26/bin/mongod bin/lib/
    cp /tmp/mongodb-linux-x86_64-ubuntu2004-4.4.26/bin/mongos bin/lib/
fi

# 5. Install Redis
echo "--- Checking Redis ---"
if ! command -v redis-server &> /dev/null; then
    apt-get install -y -qq redis-server
fi

# 6. Install GenieACS npm packages
echo "--- Installing GenieACS npm packages ---"
bun install --silent

# 7. Create genieacs env file
if [ ! -f "genieacs.env" ]; then
    cat <<'EOT' > genieacs.env
GENIEACS_MONGODB_CONNECTION_URL=mongodb://127.0.0.1:27017/genieacs
GENIEACS_REDIS_CONNECTION_URL=redis://127.0.0.1:6379/0
GENIEACS_CWMP_PORT=7547
GENIEACS_NBI_PORT=7557
GENIEACS_FS_PORT=7567
GENIEACS_UI_PORT=3000
GENIEACS_UI_JWT_SECRET=mcp_secret_key_change_me
EOT
fi

# 8. Create logs dir
mkdir -p logs data/db

# 9. MCP wrapper venv
echo "--- Building MCP wrapper ---"
cd .. # Back to genieacs/
if [ ! -d ".venv" ]; then
    uv venv .venv
fi
source .venv/bin/activate
uv pip install --quiet fastmcp httpx python-dotenv

echo "=== Build complete ==="
