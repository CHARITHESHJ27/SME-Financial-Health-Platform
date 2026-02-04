#!/bin/bash

# Deployment configuration script for SME Financial Health Platform

set -e

echo "🚀 SME Financial Health Platform Deployment"

# Check if PostgreSQL is available
check_postgres() {
    echo "Checking PostgreSQL availability..."
    if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
        echo "✅ PostgreSQL is available"
        return 0
    else
        echo "❌ PostgreSQL is not available"
        return 1
    fi
}

# Setup environment based on availability
setup_environment() {
    if check_postgres; then
        echo "Using PostgreSQL configuration"
        if [ -f ".env.production" ]; then
            cp .env.production .env
            echo "✅ Production environment configured"
        fi
    else
        echo "Using SQLite fallback configuration"
        # Ensure SQLite configuration is in .env
        if ! grep -q "sqlite" .env; then
            echo "DATABASE_URL=sqlite:///./sme_financial_health.db" > .env.temp
            grep -v "DATABASE_URL" .env >> .env.temp || true
            mv .env.temp .env
        fi
        echo "✅ SQLite fallback configured"
    fi
}

# Install dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Run the application
start_application() {
    echo "Starting SME Financial Health Platform..."
    
    # Set environment variables for production
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export PORT=${PORT:-8000}
    export HOST=${HOST:-0.0.0.0}
    
    # Start with uvicorn
    uvicorn app.main:app --host $HOST --port $PORT --workers 1
}

# Main execution
main() {
    cd "$(dirname "$0")"
    
    case "${1:-start}" in
        "setup")
            setup_environment
            install_dependencies
            ;;
        "start")
            setup_environment
            start_application
            ;;
        "check")
            check_postgres
            ;;
        *)
            echo "Usage: $0 {setup|start|check}"
            echo "  setup - Configure environment and install dependencies"
            echo "  start - Start the application"
            echo "  check - Check PostgreSQL availability"
            exit 1
            ;;
    esac
}

main "$@"