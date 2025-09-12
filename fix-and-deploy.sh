#!/bin/bash

# 一鍵修復和部署腳本
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
    print_header "一鍵修復和部署 HR 系統"
    
    # 1. 停止現有容器
    print_info "🛑 停止現有容器..."
    sudo docker stop hr_backend hr_frontend 2>/dev/null || true
    sudo docker rm hr_backend hr_frontend 2>/dev/null || true
    
    # 2. 測試資料庫連接
    print_info "🔍 測試資料庫連接..."
    if mysql -h 192.168.0.222 -P 3306 -u hr_user -p'1VcFIo@wGlLGTkjd' hr_performance -e "SELECT 1" >/dev/null 2>&1; then
        print_info "✅ 資料庫連接成功"
    else
        print_warning "⚠️  資料庫連接失敗，但繼續部署"
    fi
    
    # 3. 建立必要目錄
    print_info "📁 建立本地目錄..."
    mkdir -p ./volumes/evidence ./volumes/logs ./volumes/uploads
    chmod 755 ./volumes/evidence ./volumes/logs ./volumes/uploads
    
    # 4. 只建置和啟動後端（前端有問題暫時跳過）
    print_info "🔨 建置和啟動後端服務..."
    sudo docker-compose down --remove-orphans 2>/dev/null || true
    sudo docker-compose build backend --no-cache
    sudo docker-compose up -d backend
    
    # 5. 等待服務啟動
    print_info "⏳ 等待服務啟動..."
    sleep 20
    
    # 6. 檢查服務狀態
    print_info "📊 檢查服務狀態..."
    sudo docker-compose ps
    
    # 7. 測試 API
    print_info "🧪 測試 API..."
    if timeout 15 curl -f http://localhost:8004/health > /dev/null 2>&1; then
        print_info "✅ 後端服務正常"
        
        # 測試資料庫
        print_info "🗄️  測試資料庫..."
        curl -s http://localhost:8004/api/v1/test/db | head -3
        echo ""
        
    else
        print_error "❌ 後端服務異常"
        print_info "檢查後端日誌："
        sudo docker logs hr_backend | tail -10
    fi
    
    # 8. 測試前端
    if timeout 15 curl -f http://localhost:3004 > /dev/null 2>&1; then
        print_info "✅ 前端服務正常"
    else
        print_error "❌ 前端服務異常"
        print_info "檢查前端日誌："
        sudo docker logs hr_frontend | tail -10
    fi
    
    # 9. 初始化資料庫表格
    print_info "🗄️  初始化資料庫表格..."
    if [ -f "scripts/init-external-mariadb.sh" ]; then
        bash scripts/init-external-mariadb.sh
    else
        print_warning "找不到資料庫初始化腳本"
    fi
    
    print_info "🌐 服務 URL："
    print_info "   前端: http://localhost:3004"
    print_info "   後端: http://localhost:8004"
    print_info "   API 文檔: http://localhost:8004/docs"
    
    print_info "🎉 部署完成！"
}

main "$@"