#!/usr/bin/env bash
# ==============================================================================
# PullSense — 1-Click Local Development Setup Script (Unix/macOS/WSL)
# ==============================================================================

set -e

echo "🚀 Starting PullSense local development setup..."

# 1. Check prerequisites
command -v uv >/dev/null 2>&1 || { echo "❌ 'uv' is required but not installed. Install via: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required. Please install Node.js >= 18"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required."; exit 1; }

echo "✅ Prerequisites verified: uv, node, npm."

# 2. Setup Server environment
if [ ! -f "server/.env" ]; then
    echo "📋 Copying server/.env.example -> server/.env"
    cp server/.env.example server/.env
fi

echo "📦 Installing backend dependencies with uv..."
cd server
uv sync
echo "✅ Backend dependencies installed."

# 3. Setup Client environment
cd ../client
if [ ! -f ".env" ]; then
    echo "📋 Copying client/.env.example -> client/.env"
    cp .env.example .env
fi

echo "📦 Installing frontend dependencies with npm..."
npm install
echo "✅ Frontend dependencies installed."

cd ..

echo "🎉 PullSense setup complete! Run 'make dev' or 'docker compose up' to start the platform."
