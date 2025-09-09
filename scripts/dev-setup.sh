#!/bin/bash

# HR Performance System - Development Setup Script
echo "🚀 Setting up HR Performance System for development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Check if we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed (for local frontend development)
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed. You won't be able to run frontend development server."
fi

# Check if Python is installed (for local backend development)  
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 is not installed. You won't be able to run backend development server."
fi

print_header "1. Creating development environment"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_status "✅ .env file created. Please review and update the configuration."
else
    print_status "✅ .env file already exists"
fi

# Create data directories
print_status "Creating data directories..."
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/uploads
mkdir -p logs

print_header "2. Setting up database"

# Start database services
print_status "Starting database and Redis services..."
docker-compose up -d postgres redis

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
docker-compose exec backend alembic upgrade head || {
    print_warning "Migration failed. This might be expected if it's the first run."
}

print_header "3. Setting up backend"

# Install Python dependencies (if running locally)
if command -v python3 &> /dev/null && [ -f "backend/requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Created Python virtual environment"
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    print_status "✅ Backend dependencies installed"
fi

print_header "4. Setting up frontend"

# Install Node.js dependencies (if running locally)
if command -v node &> /dev/null && [ -f "frontend/package.json" ]; then
    print_status "Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
    print_status "✅ Frontend dependencies installed"
fi

print_header "5. Starting all services"

# Start all services
print_status "Starting all services with Docker Compose..."
docker-compose up -d

print_status "Waiting for services to be ready..."
sleep 15

print_header "6. Creating sample data"

# Create sample data (optional)
print_status "Creating sample data..."
docker-compose exec backend python scripts/create_sample_data.py || {
    print_warning "Sample data creation failed. This might be expected if data already exists."
}

print_header "7. Development Setup Complete!"

echo ""
print_status "🎉 Development environment is ready!"
echo ""
echo "📋 Service URLs:"
echo "   - Frontend: http://localhost:3004"
echo "   - Backend API: http://localhost:8004"
echo "   - API Documentation: http://localhost:8004/docs"
echo "   - Database: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "🔧 Development Commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Rebuild services: docker-compose build"
echo "   - Run migrations: docker-compose exec backend alembic upgrade head"
echo "   - Access database: docker-compose exec postgres psql -U postgres -d hr_performance"
echo ""
echo "👤 Default Login:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo ""

# Check if services are responding
print_status "Checking service health..."

# Check backend health
if curl -s http://localhost:8004/health > /dev/null; then
    print_status "✅ Backend is responding"
else
    print_warning "❌ Backend is not responding. Check logs with: docker-compose logs backend"
fi

# Check frontend health
if curl -s http://localhost:3004 > /dev/null; then
    print_status "✅ Frontend is responding"
else
    print_warning "❌ Frontend is not responding. Check logs with: docker-compose logs frontend"
fi

print_status "Setup complete! Happy coding! 🎯"