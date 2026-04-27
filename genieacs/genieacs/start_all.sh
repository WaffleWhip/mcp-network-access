#!/bin/bash
# Move to the directory where the script is located
cd "$(dirname "$0")"
BASE_DIR=$PWD
BIN_DIR=$BASE_DIR/bin
LIB_DIR=$BIN_DIR/lib

echo "--- Starting Isolated GenieACS Stack (Real) ---"

# Set Library Path for MongoDB
export LD_LIBRARY_PATH=$LIB_DIR:$LD_LIBRARY_PATH

# 1. Start MongoDB
echo "Starting MongoDB..."
$BIN_DIR/mongod --dbpath ./data/db --port 27017 --logpath ./logs/mongo.log --fork --logappend

# 2. Start Redis
echo "Starting Redis..."
$BIN_DIR/redis-server --port 6379 --daemonize yes --logfile $BASE_DIR/logs/redis.log

# Wait for DBs to initialize
echo "Waiting for databases to initialize..."
sleep 5

# 3. Start GenieACS Services
echo "Starting GenieACS Services..."
export $(grep -v '^#' genieacs.env | xargs)

# Run via Bun (using local binaries from node_modules)
nohup bun x genieacs-cwmp > ./logs/cwmp.log 2>&1 &
nohup bun x genieacs-nbi > ./logs/nbi.log 2>&1 &
nohup bun x genieacs-fs > ./logs/fs.log 2>&1 &
nohup bun x genieacs-ui > ./logs/ui.log 2>&1 &

echo "Waiting for GenieACS to warm up..."
sleep 10

# 4. Start MCP Server
echo "Starting GenieACS MCP Server (Bridge)..."
# Ensure the .env points to our local NBI
sed -i 's|GENIEACS_URL=.*|GENIEACS_URL=http://127.0.0.1:7557|' .env

. .venv/bin/activate
# Run MCP on 0.0.0.0 so external clients can reach it
python server.py
