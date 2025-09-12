#!/bin/bash

# Start Backend Only Script
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
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

main() {
    print_header "僅啟動後端服務"
    
    # Stop all services
    print_info "🛑 停止所有服務..."
    sudo docker-compose down
    
    # Remove backend image
    print_info "🗑️  清理後端映像..."
    sudo docker rmi hr-performance-system-backend 2>/dev/null || true
    
    # Build backend only
    print_info "🔨 建構後端..."
    sudo docker-compose build backend
    
    # Start backend only
    print_info "🚀 啟動後端服務..."
    sudo docker-compose up -d backend
    
    # Wait and check
    print_info "⏳ 等待服務啟動..."
    sleep 10
    
    # Check status
    print_info "📊 檢查服務狀態..."
    sudo docker-compose ps
    
    print_info "📋 顯示後端日誌..."
    sudo docker-compose logs backend
    
    print_info "🌐 後端服務："
    print_info "   API: http://localhost:8004"
    print_info "   文檔: http://localhost:8004/docs"
}

main "$@"