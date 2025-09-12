#!/bin/bash

# Simple Backend with Database Script
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
    print_header "簡化版後端服務 (含資料庫)"
    
    # Stop any existing containers
    print_info "🛑 停止現有容器..."
    sudo docker stop hr_simple_backend 2>/dev/null || true
    sudo docker rm hr_simple_backend 2>/dev/null || true
    sudo docker rmi hr-simple-backend 2>/dev/null || true
    
    # Build simple backend
    print_info "🔨 建構簡化後端..."
    sudo docker build -f backend/Dockerfile.simple -t hr-simple-backend backend/
    
    # Run simple backend
    print_info "🚀 啟動簡化後端服務..."
    sudo docker run -d --name hr_simple_backend -p 8005:8000 hr-simple-backend
    
    # Wait and check
    print_info "⏳ 等待服務啟動..."
    sleep 10
    
    # Check status
    print_info "📊 檢查服務狀態..."
    sudo docker ps | grep hr_simple_backend || print_error "容器未運行"
    
    # Test API
    print_info "🧪 測試 API..."
    if curl -f http://localhost:8005/health > /dev/null 2>&1; then
        print_info "✅ 健康檢查通過"
        
        # Test database
        print_info "🗄️  測試資料庫連接..."
        curl -s http://localhost:8005/api/v1/test/db | head -3
        
        print_info "🌐 簡化版 URL:"
        print_info "   健康檢查: http://localhost:8005/health"
        print_info "   資料庫測試: http://localhost:8005/api/v1/test/db"
        print_info "   用戶列表: http://localhost:8005/api/v1/users"
        print_info "   API 文檔: http://localhost:8005/docs"
        
    else
        print_error "❌ API 測試失敗"
        print_info "檢查日誌："
        sudo docker logs hr_simple_backend
        return 1
    fi
    
    print_info "📋 查看即時日誌 (按 Ctrl+C 退出)："
    sudo docker logs -f hr_simple_backend
}

main "$@"