#!/bin/bash

# 清理端口並啟動後端服務
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

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

main() {
    print_header "清理端口並啟動 HR 後端服務"
    
    # 1. 停止所有相關容器
    print_info "🛑 停止所有 HR 相關容器..."
    sudo docker stop $(sudo docker ps -q --filter "name=hr_") 2>/dev/null || true
    sudo docker rm $(sudo docker ps -aq --filter "name=hr_") 2>/dev/null || true
    
    # 2. 檢查端口 8004 使用情況
    print_info "🔍 檢查端口 8004 使用情況..."
    PORT_PID=$(sudo lsof -ti:8004 2>/dev/null || true)
    if [ ! -z "$PORT_PID" ]; then
        print_warning "⚠️  端口 8004 被 PID $PORT_PID 使用，正在終止..."
        sudo kill -9 $PORT_PID 2>/dev/null || true
        sleep 2
    fi
    
    # 3. 檢查端口 3004 使用情況  
    print_info "🔍 檢查端口 3004 使用情況..."
    PORT_PID=$(sudo lsof -ti:3004 2>/dev/null || true)
    if [ ! -z "$PORT_PID" ]; then
        print_warning "⚠️  端口 3004 被 PID $PORT_PID 使用，正在終止..."
        sudo kill -9 $PORT_PID 2>/dev/null || true
        sleep 2
    fi
    
    # 4. 停止所有 Docker Compose 服務
    print_info "🛑 停止 Docker Compose 服務..."
    sudo docker-compose down --remove-orphans 2>/dev/null || true
    
    # 5. 建立必要目錄
    print_info "📁 建立必要目錄..."
    mkdir -p ./volumes/evidence ./volumes/logs ./volumes/uploads
    chmod 755 ./volumes/evidence ./volumes/logs ./volumes/uploads
    
    # 6. 測試資料庫連接
    print_info "🔍 測試資料庫連接..."
    if mysql -h 192.168.0.222 -P 3306 -u hr_user -p'1VcFIo@wGlLGTkjd' hr_performance -e "SELECT 1;" >/dev/null 2>&1; then
        print_info "✅ 資料庫連接成功"
    else
        print_warning "⚠️  資料庫連接失敗，但繼續啟動服務"
    fi
    
    # 7. 啟動後端服務
    print_info "🔨 啟動後端服務..."
    sudo docker-compose up -d backend
    
    # 8. 等待啟動
    print_info "⏳ 等待後端啟動..."
    sleep 15
    
    # 9. 檢查狀態
    print_info "📊 檢查服務狀態..."
    sudo docker ps | grep hr_performance_backend || print_warning "後端可能未正常啟動"
    
    # 10. 測試 API
    print_info "🧪 測試後端 API..."
    if timeout 15 curl -f http://localhost:8004/health > /dev/null 2>&1; then
        print_info "✅ 後端 API 正常運行"
        
        # 測試資料庫
        print_info "🗄️  測試資料庫 API..."
        curl -s http://localhost:8004/api/v1/test/db | head -3
        echo ""
        
        print_info "🌐 服務已啟動："
        print_info "   後端 API: http://localhost:8004"
        print_info "   健康檢查: http://localhost:8004/health"
        print_info "   API 文檔: http://localhost:8004/docs"
        print_info "   資料庫測試: http://localhost:8004/api/v1/test/db"
        
    else
        print_warning "❌ 後端 API 測試失敗"
        print_info "檢查後端日誌："
        sudo docker logs hr_performance_backend | tail -20
    fi
    
    print_info "📋 查看即時日誌 (按 Ctrl+C 退出)："
    sudo docker logs -f hr_performance_backend
}

main "$@"