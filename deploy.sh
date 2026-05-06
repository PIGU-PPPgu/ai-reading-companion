#!/bin/bash
# IntelliTutor 部署脚本
# 用法: ./deploy.sh [--build-only] [--skip-sync]
set -e

DEPLOY_DIR="/home/ubuntu/intellitutor"
WEB_DIR="$DEPLOY_DIR/web"
CONDA_PYTHON="/home/ubuntu/miniconda3/envs/intellitutor/bin/python"
CONDA_PIP="/home/ubuntu/miniconda3/envs/intellitutor/bin/pip"
FRONTEND_PORT=3372
BACKEND_PORT=8001

BUILD_ONLY=false
SKIP_SYNC=false
[[ "$1" == "--build-only" ]] && BUILD_ONLY=true
[[ "$1" == "--skip-sync" ]] && SKIP_SYNC=true

echo "============================================"
echo "🚀 IntelliTutor Deploy"
echo "============================================"

# 1. Sync from local (if not skipped)
if [ "$SKIP_SYNC" = false ]; then
    echo "📡 Syncing backend..."
    rsync -az --delete \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='*.pyc' \
        --exclude='data/' \
        --exclude='.env' \
        --exclude='*.egg-info' \
        ./deeptutor/ $DEPLOY_DIR/deeptutor/

    echo "📡 Syncing web..."
    rsync -az --delete \
        --exclude='node_modules' \
        --exclude='.next' \
        --exclude='.git' \
        ./web/ $WEB_DIR/

    echo "📡 Syncing requirements & scripts..."
    rsync -az ./requirements.txt ./pyproject.toml ./requirements/ ./scripts/ $DEPLOY_DIR/
fi

# 2. Install Python dependencies
echo "📦 Installing Python dependencies..."
$CONDA_PIP install -q json_repair 'python-jose[cryptography]' 'passlib[bcrypt]' aiosqlite 2>/dev/null || true

# 3. Build frontend
echo "🏗️  Building frontend..."
cd $WEB_DIR
npm run build

# 4. Fix permissions (nginx needs to read static files)
echo "🔐 Fixing permissions for nginx..."
chmod -R o+rX $WEB_DIR/.next/static/
chmod -R o+rX $WEB_DIR/public/
chmod o+x /home/ubuntu /home/ubuntu/intellitutor $WEB_DIR $WEB_DIR/.next

# 5. Restart backend
echo "🔄 Restarting backend..."
BACKEND_PID=$(pgrep -f "uvicorn deeptutor.api.main:app.*--port $BACKEND_PORT" || true)
if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
    sleep 2
fi
cd $DEPLOY_DIR
nohup $CONDA_PYTHON -m uvicorn deeptutor.api.main:app \
    --host 0.0.0.0 --port $BACKEND_PORT \
    > /tmp/intellitutor-backend.log 2>&1 &
echo "  Backend PID: $!"

# 6. Restart frontend
echo "🔄 Restarting frontend..."
FRONTEND_PID=$(pgrep -f "next-server" || true)
if [ -n "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null || true
    sleep 2
fi
cd $WEB_DIR
PORT=$FRONTEND_PORT HOSTNAME=0.0.0.0 \
    nohup node .next/standalone/server.js \
    > /tmp/intellitutor-frontend.log 2>&1 &
echo "  Frontend PID: $!"

# 7. Verify
sleep 5
echo ""
echo "============================================"
echo "✅ Verifying..."
BACKEND_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$BACKEND_PORT/)
FRONTEND_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$FRONTEND_PORT/)
CSS_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$FRONTEND_PORT/_next/static/chunks/ 2>/dev/null || echo "skip")

echo "  Backend:  $BACKEND_OK (port $BACKEND_PORT)"
echo "  Frontend: $FRONTEND_OK (port $FRONTEND_PORT)"
echo "============================================"

if [ "$BACKEND_OK" = "200" ] && [ "$FRONTEND_OK" = "200" ]; then
    echo "🎉 Deploy complete!"
else
    echo "⚠️  Something may be wrong, check logs:"
    echo "  Backend:  tail -50 /tmp/intellitutor-backend.log"
    echo "  Frontend: tail -50 /tmp/intellitutor-frontend.log"
fi
