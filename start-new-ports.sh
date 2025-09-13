#!/bin/bash

# 使用新端口啟動 HR 系統 (8008/3008)
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
    print_header "使用新端口啟動 HR 系統 (8008/3008)"
    
    # 1. 停止現有容器
    print_info "🛑 停止現有容器..."
    sudo docker-compose down --remove-orphans 2>/dev/null || true
    
    # 2. 清理端口
    print_info "🔍 清理端口 8008 和 3008..."
    
    # 檢查端口 8008
    PORT_PID=$(sudo lsof -ti:8008 2>/dev/null || true)
    if [ ! -z "$PORT_PID" ]; then
        print_warning "⚠️  終止佔用端口 8008 的程序 PID $PORT_PID"
        sudo kill -9 $PORT_PID 2>/dev/null || true
    fi
    
    # 檢查端口 3008
    PORT_PID=$(sudo lsof -ti:3008 2>/dev/null || true)
    if [ ! -z "$PORT_PID" ]; then
        print_warning "⚠️  終止佔用端口 3008 的程序 PID $PORT_PID"
        sudo kill -9 $PORT_PID 2>/dev/null || true
    fi
    
    sleep 3
    
    # 3. 建立必要目錄
    print_info "📁 建立必要目錄..."
    mkdir -p ./volumes/evidence ./volumes/logs ./volumes/uploads
    chmod 755 ./volumes/evidence ./volumes/logs ./volumes/uploads
    
    # 4. 測試資料庫連接
    print_info "🔍 測試資料庫連接..."
    if mysql -h 192.168.0.222 -P 3306 -u hr_user -p'1VcFIo@wGlLGTkjd' hr_performance -e "SELECT 1;" >/dev/null 2>&1; then
        print_info "✅ 資料庫連接成功"
    else
        print_warning "⚠️  資料庫連接失敗，但繼續啟動後端"
    fi
    
    # 5. 啟動後端服務
    print_info "🚀 啟動後端服務 (端口 8008)..."
    sudo docker-compose up -d backend
    
    # 6. 等待啟動
    print_info "⏳ 等待後端啟動..."
    sleep 15
    
    # 7. 檢查後端狀態
    print_info "📊 檢查後端狀態..."
    if sudo docker ps | grep hr_performance_backend > /dev/null; then
        print_info "✅ 後端容器運行中"
    else
        print_error "❌ 後端容器未運行"
        return 1
    fi
    
    # 8. 測試後端 API
    print_info "🧪 測試後端 API..."
    if timeout 15 curl -f http://localhost:8008/health > /dev/null 2>&1; then
        print_info "✅ 後端 API 正常"
        
        # 測試資料庫 API
        print_info "🗄️  測試資料庫 API..."
        curl -s http://localhost:8008/api/v1/test/db | head -3
        echo ""
        
        print_info "🌐 後端服務已啟動："
        print_info "   後端 API: http://localhost:8008"
        print_info "   健康檢查: http://localhost:8008/health"
        print_info "   API 文檔: http://localhost:8008/docs"
        print_info "   資料庫測試: http://localhost:8008/api/v1/test/db"
        print_info "   用戶列表: http://localhost:8008/api/v1/users"
        
    else
        print_error "❌ 後端 API 測試失敗"
        print_info "檢查後端日誌："
        sudo docker logs hr_performance_backend | tail -20
        return 1
    fi
    
    print_info "🎉 後端服務成功啟動在新端口 8008!"
    print_info "📋 查看即時日誌 (按 Ctrl+C 退出)："
    sudo docker logs -f hr_performance_backend
}

main "$@"