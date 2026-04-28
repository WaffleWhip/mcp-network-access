#!/bin/bash
# genieacs/install/start.sh - Start GenieACS stack + MCP server
set -e
cd "$(dirname "$0")/.." # Go up from install/ to project root

# Source: /root/poc/genieacs/genieacs/start_all.sh
BASE_DIR=$PWD
GENIEACS_DIR="/root/poc/genieacs/genieacs"
BIN_DIR=$GENIEACS_DIR/bin
LIB_DIR=$BIN_DIR/lib

echo "--- Starting GenieACS Stack ---"

# Set Library Path for MongoDB
export LD_LIBRARY_PATH=$LIB_DIR:$LD_LIBRARY_PATH

# 1. Start MongoDB
echo "Starting MongoDB..."
if [ -f "$BIN_DIR/mongod" ]; then
    $BIN_DIR/mongod --dbpath $GENIEACS_DIR/data/db --port 27017 --logpath $GENIEACS_DIR/logs/mongo.log --fork --logappend 2>/dev/null || true
fi

# 2. Start Redis
echo "Starting Redis..."
if [ -f "$BIN_DIR/redis-server" ]; then
    $BIN_DIR/redis-server --port 6379 --daemonize yes --logfile $GENIEACS_DIR/logs/redis.log 2>/dev/null || true
fi

# Wait for DBs
sleep 3

# 3. Start GenieACS Services
echo "Starting GenieACS Services..."
cd $GENIEACS_DIR
export $(grep -v '^#' genieacs.env | xargs)
nohup bun x genieacs-cwmp > ./logs/cwmp.log 2>&1 &
nohup bun x genieacs-nbi > ./logs/nbi.log 2>&1 &
nohup bun x genieacs-fs > ./logs/fs.log 2>&1 &
nohup bun x genieacs-ui > ./logs/ui.log 2>&1 &
cd $BASE_DIR

sleep 5

# 4. Start MCP Server
echo "Starting GenieACS MCP Server..."
source .venv/bin/activate
exec python server.py