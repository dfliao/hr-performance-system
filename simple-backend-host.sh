#!/bin/bash

# Simple Backend with Host Network Script
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
    print_header "簡化版後端服務 (使用主機網路)"
    
    # Stop any existing containers
    print_info "🛑 停止現有容器..."
    sudo docker stop hr_simple_backend_host 2>/dev/null || true
    sudo docker rm hr_simple_backend_host 2>/dev/null || true
    
    # Test database connectivity from host first
    print_info "🔍 測試主機到資料庫的連接..."
    if command -v mysql >/dev/null 2>&1; then
        if timeout 10 mysql -h 192.168.0.222 -P 3306 -u hr_user -phr_password_2024 hr_performance -e "SELECT 1" >/dev/null 2>&1; then
            print_info "✅ 主機可以連接到資料庫"
        else
            print_warning "⚠️  主機無法連接到資料庫，但我們繼續嘗試"
        fi
    else
        print_warning "⚠️  找不到 mysql 客戶端，跳過連接測試"
    fi
    
    # Build if not exists
    if [[ "$(sudo docker images -q hr-simple-backend 2> /dev/null)" == "" ]]; then
        print_info "🔨 建構簡化後端..."
        sudo docker build -f backend/Dockerfile.simple -t hr-simple-backend backend/
    else
        print_info "📦 使用現有映像..."
    fi
    
    # Run simple backend with host network
    print_info "🚀 啟動簡化後端服務 (主機網路模式)..."
    sudo docker run -d --name hr_simple_backend_host --network host hr-simple-backend
    
    # Wait and check
    print_info "⏳ 等待服務啟動..."
    sleep 15
    
    # Check status
    print_info "📊 檢查服務狀態..."
    sudo docker ps | grep hr_simple_backend_host || print_error "容器未運行"
    
    # Test API
    print_info "🧪 測試 API..."
    if timeout 10 curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_info "✅ 健康檢查通過"
        
        # Test database
        print_info "🗄️  測試資料庫連接..."
        timeout 10 curl -s http://localhost:8000/api/v1/test/db | head -3
        
        print_info "🌐 簡化版 URL (主機網路):"
        print_info "   健康檢查: http://localhost:8000/health"
        print_info "   資料庫測試: http://localhost:8000/api/v1/test/db"
        print_info "   用戶列表: http://localhost:8000/api/v1/users"
        print_info "   API 文檔: http://localhost:8000/docs"
        
    else
        print_error "❌ API 測試失敗"
        print_info "檢查日誌："
        sudo docker logs hr_simple_backend_host | tail -20
        return 1
    fi
    
    print_info "📋 查看即時日誌 (按 Ctrl+C 退出)："
    sudo docker logs -f hr_simple_backend_host
}

main "$@"