#!/bin/bash

# 快速啟動後端服務
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

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

main() {
    print_header "快速啟動 HR 後端服務"
    
    # 1. 停止現有後端容器
    print_info "🛑 停止現有後端容器..."
    sudo docker stop hr_performance_backend 2>/dev/null || true
    sudo docker rm hr_performance_backend 2>/dev/null || true
    
    # 2. 建立必要目錄
    print_info "📁 建立必要目錄..."
    mkdir -p ./volumes/evidence ./volumes/logs ./volumes/uploads
    chmod 755 ./volumes/evidence ./volumes/logs ./volumes/uploads
    
    # 3. 建置並啟動後端
    print_info "🔨 建置並啟動後端..."
    sudo docker-compose build backend --no-cache
    sudo docker-compose up -d backend
    
    # 4. 等待啟動
    print_info "⏳ 等待後端啟動..."
    sleep 15
    
    # 5. 檢查狀態
    print_info "📊 檢查後端狀態..."
    sudo docker ps | grep hr_performance_backend || echo "❌ 後端未運行"
    
    # 6. 測試 API
    print_info "🧪 測試後端 API..."
    if timeout 10 curl -f http://localhost:8008/health > /dev/null 2>&1; then
        print_info "✅ 後端 API 正常"
        
        # 測試資料庫
        print_info "🗄️  測試資料庫連接..."
        curl -s http://localhost:8008/api/v1/test/db
        echo ""
        
        print_info "🌐 後端服務已啟動："
        print_info "   後端 API: http://localhost:8008"
        print_info "   健康檢查: http://localhost:8008/health"
        print_info "   API 文檔: http://localhost:8008/docs"
        
    else
        print_info "❌ 後端啟動失敗，檢查日誌："
        sudo docker logs hr_performance_backend | tail -20
    fi
    
    print_info "📋 查看即時日誌 (按 Ctrl+C 退出)："
    sudo docker logs -f hr_performance_backend
}

main "$@"