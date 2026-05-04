#!/bin/bash
# genieacs/start.sh - Start GenieACS stack + MCP server
set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
GENIEACS_DIR="$BASE_DIR/genieacs"
BIN_DIR="$GENIEACS_DIR/bin"
LIB_DIR="$BIN_DIR/lib"

echo "--- Starting GenieACS Stack in $BASE_DIR ---"

# Set Library Path for MongoDB
export LD_LIBRARY_PATH=$LIB_DIR:$LD_LIBRARY_PATH

# 1. Start MongoDB
MONGOD_BIN="$LIB_DIR/mongod"
if [ -f "$MONGOD_BIN" ]; then
    $MONGOD_BIN --dbpath "$GENIEACS_DIR/data/db" --port 27017 --logpath "$GENIEACS_DIR/logs/mongo.log" --fork --logappend || true
fi

# 2. Start Redis
REDIS_BIN=$(command -v redis-server || echo "$BIN_DIR/redis-server")
if [ -x "$REDIS_BIN" ]; then
    $REDIS_BIN --port 6379 --daemonize yes --logfile "$GENIEACS_DIR/logs/redis.log" || true
fi

# Wait for DBs
sleep 5

# 3. Start GenieACS Services
cd "$GENIEACS_DIR"
export $(grep -v '^#' genieacs.env | xargs)
BUN_BIN=$(command -v bun || echo "$HOME/.bun/bin/bun")

nohup "$BUN_BIN" run bin/genieacs-cwmp.ts > ./logs/cwmp.log 2>&1 &
nohup "$BUN_BIN" run bin/genieacs-nbi.ts > ./logs/nbi.log 2>&1 &
nohup "$BUN_BIN" run bin/genieacs-fs.ts > ./logs/fs.log 2>&1 &
nohup "$BUN_BIN" run bin/genieacs-ui.ts > ./logs/ui.log 2>&1 &
cd "$BASE_DIR"

sleep 10

# 4. Start MCP Server
echo "Starting GenieACS MCP Server..."
source .venv/bin/activate
exec python server.py
