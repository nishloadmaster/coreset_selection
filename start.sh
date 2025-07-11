#!/bin/bash

# AI Model Improver - Startup Script
# This script handles starting the application in different environments

set -e

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

# Function to check if port is available
port_available() {
    ! nc -z localhost $1 2>/dev/null
}

# Function to wait for service to be ready
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            print_success "$service is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to start backend
start_backend() {
    local mode=$1
    
    print_status "Starting backend in $mode mode..."
    
    if [ "$mode" = "docker" ]; then
        if ! command_exists docker; then
            print_error "Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        if ! command_exists docker-compose; then
            print_error "Docker Compose is not installed. Please install Docker Compose first."
            exit 1
        fi
        
        cd backend
        docker-compose up --build -d
        cd ..
        
        wait_for_service "Backend" 8050
    else
        cd backend
        
        if ! command_exists python3; then
            print_error "Python 3 is not installed. Please install Python 3 first."
            exit 1
        fi
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            print_status "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Install dependencies
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        
        # Start the server
        print_status "Starting FastAPI server..."
        uvicorn main:app --host 0.0.0.0 --port 8050 --reload &
        
        cd ..
        wait_for_service "Backend" 8050
    fi
}

# Function to start frontend
start_frontend() {
    local mode=$1
    
    print_status "Starting frontend in $mode mode..."
    
    if [ "$mode" = "docker" ]; then
        cd frontend
        docker-compose up --build -d
        cd ..
        
        wait_for_service "Frontend" 3058
    else
        cd frontend
        
        if ! command_exists node; then
            print_error "Node.js is not installed. Please install Node.js first."
            exit 1
        fi
        
        if ! command_exists npm; then
            print_error "npm is not installed. Please install npm first."
            exit 1
        fi
        
        # Install dependencies
        print_status "Installing Node.js dependencies..."
        npm install
        
        # Start development server
        print_status "Starting Vite development server..."
        npm run dev &
        
        cd ..
        wait_for_service "Frontend" 3058
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop Docker containers if running
    if command_exists docker && docker ps | grep -q "ai-model-improver"; then
        docker-compose down
        print_success "Docker services stopped"
    fi
    
    # Kill background processes
    pkill -f "uvicorn main:app" || true
    pkill -f "vite" || true
    
    print_success "All services stopped"
}

# Function to show status
show_status() {
    print_status "Checking service status..."
    
    echo ""
    echo "=== Service Status ==="
    
    # Check backend
    if nc -z localhost 8050 2>/dev/null; then
        print_success "Backend: Running on port 8050"
    else
        print_error "Backend: Not running"
    fi
    
    # Check frontend
    if nc -z localhost 3058 2>/dev/null; then
        print_success "Frontend: Running on port 3058"
    else
        print_error "Frontend: Not running"
    fi
    
    echo ""
    echo "=== URLs ==="
    echo "Frontend: http://localhost:3058"
    echo "Backend API: http://localhost:8050"
    echo "API Docs: http://localhost:8050/docs"
    echo ""
}

# Function to show help
show_help() {
    echo "AI Model Improver - Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [dev|docker|prod]  Start the application"
    echo "  stop                     Stop all services"
    echo "  status                   Show service status"
    echo "  restart [dev|docker|prod] Restart the application"
    echo "  logs                     Show service logs"
    echo "  help                     Show this help message"
    echo ""
    echo "Options:"
    echo "  dev                      Development mode (default)"
    echo "  docker                   Docker mode"
    echo "  prod                     Production mode"
    echo ""
    echo "Examples:"
    echo "  $0 start                 Start in development mode"
    echo "  $0 start docker          Start using Docker"
    echo "  $0 start prod            Start in production mode"
    echo "  $0 stop                  Stop all services"
    echo "  $0 status                Show current status"
    echo ""
}

# Function to show logs
show_logs() {
    print_status "Showing service logs..."
    
    if command_exists docker && docker ps | grep -q "ai-model-improver"; then
        docker-compose logs -f
    else
        print_warning "No Docker containers running. Showing local process logs..."
        echo "Backend logs (if running):"
        ps aux | grep "uvicorn" | grep -v grep || echo "No backend process found"
        echo ""
        echo "Frontend logs (if running):"
        ps aux | grep "vite" | grep -v grep || echo "No frontend process found"
    fi
}

# Main script logic
case "${1:-start}" in
    "start")
        mode="${2:-dev}"
        
        print_status "Starting AI Model Improver in $mode mode..."
        
        # Check prerequisites
        if [ "$mode" = "docker" ] || [ "$mode" = "prod" ]; then
            if ! command_exists docker; then
                print_error "Docker is required for $mode mode. Please install Docker first."
                exit 1
            fi
        fi
        
        # Start services
        start_backend $mode
        start_frontend $mode
        
        print_success "AI Model Improver started successfully!"
        show_status
        ;;
        
    "stop")
        stop_services
        ;;
        
    "restart")
        mode="${2:-dev}"
        print_status "Restarting AI Model Improver..."
        stop_services
        sleep 2
        $0 start $mode
        ;;
        
    "status")
        show_status
        ;;
        
    "logs")
        show_logs
        ;;
        
    "help"|"-h"|"--help")
        show_help
        ;;
        
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 