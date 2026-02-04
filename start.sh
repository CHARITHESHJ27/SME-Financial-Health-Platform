#!/bin/bash

# SME Financial Health Platform - Startup Script
# This script helps you quickly start the development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    # Check npm
    if ! command_exists npm; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend || exit 1
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    # shellcheck source=/dev/null
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp ../.env.example .env
        print_warning "Please update the .env file with your configuration"
    fi
    
    cd .. || exit 1
    print_success "Backend setup completed"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend || exit 1
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    cd .. || exit 1
    print_success "Frontend setup completed"
}

# Function to load sample data
load_sample_data() {
    print_status "Loading sample data..."
    
    cd backend || exit 1
    # shellcheck source=/dev/null
    source venv/bin/activate
    
    # Run data loader script
    python ../scripts/data_loader.py
    
    cd .. || exit 1
    print_success "Sample data loaded successfully"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    cd backend || exit 1
    # shellcheck source=/dev/null
    source venv/bin/activate
    
    # Start the FastAPI server
    cd app || exit 1
    python main.py &
    BACKEND_PID=$!
    
    cd ../.. || exit 1
    print_success "Backend server started (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend || exit 1
    
    # Start the React development server
    npm start &
    FRONTEND_PID=$!
    
    cd .. || exit 1
    print_success "Frontend server started (PID: $FRONTEND_PID)"
}

# Function to stop servers
stop_servers() {
    print_status "Stopping servers..."
    
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
        print_success "Backend server stopped"
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        print_success "Frontend server stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
}

# Function to show help
show_help() {
    echo "SME Financial Health Platform - Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup the development environment"
    echo "  start     - Start both backend and frontend servers"
    echo "  backend   - Start only the backend server"
    echo "  frontend  - Start only the frontend server"
    echo "  data      - Load sample data into the database"
    echo "  stop      - Stop all running servers"
    echo "  clean     - Clean up build artifacts and dependencies"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # First time setup"
    echo "  $0 start     # Start both servers"
    echo "  $0 data      # Load sample data"
    echo ""
}

# Function to clean up
clean_environment() {
    print_status "Cleaning up environment..."
    
    # Stop any running servers
    stop_servers
    
    # Remove Python virtual environment
    if [ -d "backend/venv" ]; then
        rm -rf backend/venv
        print_success "Removed Python virtual environment"
    fi
    
    # Remove Node.js dependencies
    if [ -d "frontend/node_modules" ]; then
        rm -rf frontend/node_modules
        print_success "Removed Node.js dependencies"
    fi
    
    # Remove database file (if SQLite)
    if [ -f "backend/sme_financial_health.db" ]; then
        rm backend/sme_financial_health.db
        print_success "Removed SQLite database"
    fi
    
    print_success "Environment cleaned up"
}

# Trap to handle script interruption
trap 'stop_servers; exit 130' INT

# Main script logic
case "${1:-help}" in
    "setup")
        check_prerequisites
        setup_backend
        setup_frontend
        print_success "Setup completed! Run '$0 start' to start the servers."
        ;;
    "start")
        check_prerequisites
        start_backend
        sleep 3  # Wait for backend to start
        start_frontend
        
        print_success "Both servers are starting up..."
        print_status "Backend: http://localhost:8000"
        print_status "Frontend: http://localhost:3000"
        print_status "API Docs: http://localhost:8000/docs"
        print_warning "Press Ctrl+C to stop both servers"
        
        # Wait for user to stop
        wait
        ;;
    "backend")
        check_prerequisites
        start_backend
        print_status "Backend running at: http://localhost:8000"
        print_status "API Docs: http://localhost:8000/docs"
        print_warning "Press Ctrl+C to stop the server"
        wait
        ;;
    "frontend")
        check_prerequisites
        start_frontend
        print_status "Frontend running at: http://localhost:3000"
        print_warning "Press Ctrl+C to stop the server"
        wait
        ;;
    "data")
        load_sample_data
        ;;
    "stop")
        stop_servers
        ;;
    "clean")
        clean_environment
        ;;
    "help"|*)
        show_help
        ;;
esac