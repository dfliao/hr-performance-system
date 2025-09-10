#!/bin/bash

# HR Performance System - 快速更新腳本
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

# Pull latest code (if using git)
pull_latest() {
    print_header "更新程式碼"
    
    if [ -d ".git" ]; then
        print_info "從 Git 拉取最新程式碼..."
        git pull origin main || git pull origin master
        print_info "✅ 程式碼更新完成"
    else
        print_warning "⚠️  未檢測到 Git 倉庫，請手動更新程式碼"
    fi
}

# Stop services
stop_services() {
    print_header "停止服務"
    print_info "停止所有容器..."
    sudo docker-compose down
    print_info "✅ 服務已停止"
}

# Build images
build_images() {
    print_header "重新建置映像檔"
    print_info "建置後端映像檔..."
    sudo docker-compose build backend
    
    print_info "建置前端映像檔..."
    sudo docker-compose build frontend
    
    print_info "✅ 映像檔建置完成"
}

# Start services
start_services() {
    print_header "啟動服務"
    print_info "啟動所有服務..."
    sudo docker-compose up -d
    
    print_info "等待服務啟動..."
    sleep 15
    print_info "✅ 服務啟動完成"
}

# Check service health
check_health() {
    print_header "檢查服務健康狀態"
    
    # Check backend
    print_info "檢查後端服務..."
    if curl -s http://localhost:8004/health > /dev/null; then
        print_info "✅ 後端服務正常"
    else
        print_warning "❌ 後端服務異常"
    fi
    
    # Check frontend
    print_info "檢查前端服務..."
    if curl -s http://localhost:3004 > /dev/null; then
        print_info "✅ 前端服務正常"
    else
        print_warning "❌ 前端服務異常"
    fi
}

# Show status
show_status() {
    print_header "服務狀態"
    sudo docker-compose ps
    
    echo ""
    print_info "🌐 系統存取位址："
    print_info "   前端: http://localhost:3004"
    print_info "   後端 API: http://localhost:8004"
    print_info "   API 文檔: http://localhost:8004/docs"
}

# Main execution
main() {
    print_header "HR Performance System - 快速更新"
    
    pull_latest
    stop_services
    build_images
    start_services
    check_health
    show_status
    
    print_info "🎉 更新完成！"
}

main "$@"