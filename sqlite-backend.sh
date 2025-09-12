#!/bin/bash

# SQLite Backend Script
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
    print_header "SQLite 版本後端服務"
    
    # Stop any existing containers
    print_info "🛑 停止現有容器..."
    sudo docker stop hr_sqlite_backend 2>/dev/null || true
    sudo docker rm hr_sqlite_backend 2>/dev/null || true
    sudo docker rmi hr-sqlite-backend 2>/dev/null || true
    
    # Build SQLite backend
    print_info "🔨 建構 SQLite 後端..."
    sudo docker build -f backend/Dockerfile.sqlite -t hr-sqlite-backend backend/
    
    # Run SQLite backend
    print_info "🚀 啟動 SQLite 後端服務..."
    sudo docker run -d --name hr_sqlite_backend -p 8006:8000 hr-sqlite-backend
    
    # Wait and check
    print_info "⏳ 等待服務啟動..."
    sleep 8
    
    # Check status
    print_info "📊 檢查服務狀態..."
    sudo docker ps | grep hr_sqlite_backend || print_error "容器未運行"
    
    # Test API
    print_info "🧪 測試 API..."
    if timeout 15 curl -f http://localhost:8006/health > /dev/null 2>&1; then
        print_info "✅ 健康檢查通過"
        
        # Test database
        print_info "🗄️  測試 SQLite 資料庫..."
        curl -s http://localhost:8006/api/v1/test/db
        echo ""
        
        # Show users
        print_info "👥 顯示範例使用者..."
        curl -s http://localhost:8006/api/v1/users
        echo ""
        
        print_info "🌐 SQLite 版本 URL:"
        print_info "   健康檢查: http://localhost:8006/health"
        print_info "   資料庫測試: http://localhost:8006/api/v1/test/db"
        print_info "   用戶列表: http://localhost:8006/api/v1/users"
        print_info "   API 文檔: http://localhost:8006/docs"
        print_info "   Redoc 文檔: http://localhost:8006/redoc"
        
    else
        print_error "❌ API 測試失敗"
        print_info "檢查日誌："
        sudo docker logs hr_sqlite_backend
        return 1
    fi
    
    print_info "📋 查看即時日誌 (按 Ctrl+C 退出)："
    sudo docker logs -f hr_sqlite_backend
}

main "$@"