#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

print_status()  { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC}   $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error()   { echo -e "${RED}[ERR]${NC}  $1"; }

# ── Start PostgreSQL via Docker ───────────────────────────────────────────────
start_postgres() {
    print_status "Starting PostgreSQL (Docker)..."
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi

    # Start only postgres container
    docker compose -f "$ROOT_DIR/docker-compose.yml" up postgres -d 2>&1 | grep -v "^time="

    # Wait until healthy
    print_status "Waiting for PostgreSQL to be ready..."
    for i in $(seq 1 20); do
        if docker exec sme_postgres pg_isready -U sme_user -d sme_financial_health -q 2>/dev/null; then
            print_success "PostgreSQL is ready on port 5433"
            return 0
        fi
        sleep 1
    done
    print_error "PostgreSQL did not become ready in time."
    exit 1
}

# ── Start Backend ─────────────────────────────────────────────────────────────
start_backend() {
    print_status "Starting backend (FastAPI)..."

    cd "$ROOT_DIR/backend"

    # Activate venv
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt --quiet
    else
        source venv/bin/activate
    fi

    # Fix bcrypt compatibility
    pip install "bcrypt==3.2.2" --quiet 2>/dev/null

    # Export PYTHONPATH so ml/ and backend/ are always accessible
    export PYTHONPATH="$ROOT_DIR:$ROOT_DIR/backend:$PYTHONPATH"

    # Create DB tables
    python -c "
import sys; sys.path.insert(0, '.'); sys.path.insert(0, '$ROOT_DIR')
from app.models.schemas import Base
from app.database import engine
Base.metadata.create_all(bind=engine)
print('DB tables ready')
" 2>&1 | grep -v "^INFO\|^WARNING"

    # Kill any old backend
    pkill -f "uvicorn app.main" 2>/dev/null || true
    sleep 1

    # Start uvicorn from backend/ directory
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
        > /tmp/finexri_backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/finexri_backend.pid

    # Wait for it to respond
    for i in $(seq 1 15); do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend running → http://localhost:8000  (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
    done
    print_error "Backend did not start. Check logs: tail -50 /tmp/finexri_backend.log"
    exit 1
}

# ── Start Frontend ────────────────────────────────────────────────────────────
start_frontend() {
    print_status "Starting frontend (React)..."

    cd "$ROOT_DIR/frontend"

    if [ ! -d "node_modules" ]; then
        print_status "Installing npm dependencies..."
        npm install --legacy-peer-deps --silent
    fi

    # Kill any old frontend
    pkill -f "react-scripts/scripts/start" 2>/dev/null || true
    sleep 1

    nohup npm start > /tmp/finexri_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/finexri_frontend.pid
    print_success "Frontend starting → http://localhost:3000  (PID: $FRONTEND_PID)"
}

# ── Stop all ──────────────────────────────────────────────────────────────────
stop_all() {
    print_status "Stopping all services..."
    
    [ -f /tmp/finexri_backend.pid ]  && kill "$(cat /tmp/finexri_backend.pid)"  2>/dev/null || true
    [ -f /tmp/finexri_frontend.pid ] && kill "$(cat /tmp/finexri_frontend.pid)" 2>/dev/null || true
    pkill -f "uvicorn app.main" 2>/dev/null || true
    pkill -f "react-scripts/scripts/start" 2>/dev/null || true
    
    cd "$ROOT_DIR" && docker compose stop postgres 2>/dev/null || true
    
    rm -f /tmp/finexri_backend.pid /tmp/finexri_frontend.pid
    print_success "All services stopped"
}

# ── Setup ─────────────────────────────────────────────────────────────────────
setup() {
    print_status "Setting up Finexri platform..."

    cd "$ROOT_DIR/backend"
    [ ! -d "venv" ] && python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    pip install "bcrypt==3.2.2" --quiet
    print_success "Backend deps installed"

    cd "$ROOT_DIR/frontend"
    npm install --legacy-peer-deps --silent
    print_success "Frontend deps installed"

    print_success "Setup complete! Run: ./start.sh start"
}

# ── Show logs ─────────────────────────────────────────────────────────────────
logs() {
    case "${2:-backend}" in
        backend)  tail -50 /tmp/finexri_backend.log ;;
        frontend) tail -50 /tmp/finexri_frontend.log ;;
    esac
}

# ── Help ──────────────────────────────────────────────────────────────────────
show_help() {
    echo ""
    echo "  finexri startup script"
    echo ""
    echo "  Usage: ./start.sh [command]"
    echo ""
    echo "  Commands:"
    echo "    start     → Start postgres (Docker) + backend + frontend"
    echo "    stop      → Stop all services"
    echo "    backend   → Start postgres + backend only"
    echo "    frontend  → Start frontend only"
    echo "    setup     → Install all dependencies"
    echo "    logs      → Show backend logs (./start.sh logs frontend for frontend)"
    echo ""
}

trap 'echo ""; stop_all; exit 0' INT

case "${1:-help}" in
    start)
        start_postgres
        start_backend
        start_frontend
        echo ""
        print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_success " Finexri is running!"
        print_success " Frontend  → http://localhost:3000"
        print_success " Backend   → http://localhost:8000"
        print_success " API Docs  → http://localhost:8000/docs"
        print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        print_warning "Press Ctrl+C to stop all services"
        wait
        ;;
    backend)
        start_postgres
        start_backend
        print_warning "Press Ctrl+C to stop"
        wait
        ;;
    frontend)
        start_frontend
        print_warning "Press Ctrl+C to stop"
        wait
        ;;
    stop)   stop_all ;;
    setup)  setup ;;
    logs)   logs "$@" ;;
    *)      show_help ;;
esac
