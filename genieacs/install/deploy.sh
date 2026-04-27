#!/bin/bash
# genieacs/install/deploy.sh
cd "$(dirname "$0")/.." # Go to app root folder (genieacs/)
APP_ROOT=$PWD
BACKEND_DIR=$APP_ROOT/genieacs
BIN_DIR=$BACKEND_DIR/bin
export LD_LIBRARY_PATH=$BIN_DIR/lib:$LD_LIBRARY_PATH

# Ensure backend folders exist
mkdir -p $BACKEND_DIR/logs $BACKEND_DIR/data/db $BACKEND_DIR/data/redis

echo "--- [1/3] Stabilizing Databases ---"
if ! nc -z 127.0.0.1 27017; then
    if [ -f "$BACKEND_DIR/data/db/mongod.lock" ]; then
        rm -f $BACKEND_DIR/data/db/mongod.lock
        $BIN_DIR/mongod --dbpath $BACKEND_DIR/data/db --repair
    fi
    $BIN_DIR/mongod --dbpath $BACKEND_DIR/data/db --port 27017 --logpath $BACKEND_DIR/logs/mongo.log --fork --logappend
fi

if ! nc -z 127.0.0.1 6379; then
    $BIN_DIR/redis-server --port 6379 --daemonize yes
fi

echo "--- [2/3] Starting GenieACS Backend ---"
if [ -f "$BACKEND_DIR/genieacs.env" ]; then
    export $(grep -v '^#' $BACKEND_DIR/genieacs.env | xargs)
fi

BUN_BIN=$(which bun || echo "/root/.bun/bin/bun")
cd $BACKEND_DIR

# Keep processes alive, only kill if port conflict
nohup $BUN_BIN run ./node_modules/genieacs/bin/genieacs-cwmp >> logs/cwmp.log 2>&1 &
nohup $BUN_BIN run ./node_modules/genieacs/bin/genieacs-nbi >> logs/nbi.log 2>&1 &
nohup $BUN_BIN run ./node_modules/genieacs/bin/genieacs-fs >> logs/fs.log 2>&1 &
nohup $BUN_BIN run ./node_modules/genieacs/bin/genieacs-ui >> logs/ui.log 2>&1 &

echo "--- [3/3] Starting MCP Gateway ---"
cd $APP_ROOT
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q fastmcp httpx python-dotenv

# Run in foreground to keep systemd happy, but don't use exec yet
python server.py
