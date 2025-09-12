#!/bin/bash

# Quick Redeploy Script for HR Performance System
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

# Main execution
main() {
    print_header "HR Performance System - 快速重新部署"
    
    # Pull latest code
    print_info "📥 拉取最新代碼..."
    if git pull origin main; then
        print_info "✅ 代碼更新完成"
    else
        print_error "❌ 代碼更新失敗"
        exit 1
    fi
    
    # Stop backend container
    print_info "🛑 停止後端容器..."
    sudo docker-compose down backend
    
    # Remove old backend image
    print_info "🗑️  清理舊映像..."
    if sudo docker rmi hr-performance-system_backend 2>/dev/null; then
        print_info "✅ 舊映像已清理"
    else
        print_warning "⚠️  沒有找到舊映像或清理失敗"
    fi
    
    # Rebuild backend
    print_info "🔨 重新建構後端..."
    if sudo docker-compose build backend; then
        print_info "✅ 後端建構完成"
    else
        print_error "❌ 後端建構失敗"
        exit 1
    fi
    
    # Start backend service
    print_info "🚀 啟動後端服務..."
    if sudo docker-compose up -d backend; then
        print_info "✅ 後端服務啟動完成"
    else
        print_error "❌ 後端服務啟動失敗"
        exit 1
    fi
    
    # Wait a moment for service to start
    print_info "⏳ 等待服務啟動..."
    sleep 5
    
    # Show logs
    print_info "📋 顯示後端日誌 (按 Ctrl+C 退出)："
    echo ""
    sudo docker-compose logs -f backend
}

main "$@"