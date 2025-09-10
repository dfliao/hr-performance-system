#!/bin/bash

# HR Performance System - 一鍵部署腳本
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

# Check prerequisites
check_prerequisites() {
    print_header "檢查系統需求"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安裝"
        exit 1
    fi
    print_info "✅ Docker 已安裝"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安裝"
        exit 1
    fi
    print_info "✅ Docker Compose 已安裝"
}

# Setup environment
setup_environment() {
    print_header "設定環境"
    
    if [ ! -f ".env" ]; then
        print_info "創建 .env 檔案..."
        cp .env.example .env
        print_warning "⚠️  請編輯 .env 檔案設定正確的資料庫連接參數"
    else
        print_info "✅ .env 檔案已存在"
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p backup
    mkdir -p evidence
    print_info "✅ 目錄結構已建立"
}

# Deploy application
deploy_app() {
    print_header "部署應用程式"
    
    print_info "停止現有服務..."
    sudo docker-compose down || true
    
    print_info "建置映像檔..."
    sudo docker-compose build
    
    print_info "啟動服務..."
    sudo docker-compose up -d
    
    print_info "等待服務啟動..."
    sleep 20
    
    print_info "✅ 應用程式部署完成"
}

# Initialize database
init_database() {
    print_header "初始化資料庫"
    
    if [ -f "scripts/init-external-mariadb.sh" ]; then
        print_info "執行資料庫初始化..."
        ./scripts/init-external-mariadb.sh
    else
        print_warning "⚠️  資料庫初始化腳本不存在，跳過此步驟"
    fi
}

# Verify deployment
verify_deployment() {
    print_header "驗證部署"
    
    # Check services
    print_info "檢查服務狀態..."
    sudo docker-compose ps
    
    echo ""
    
    # Check backend health
    sleep 5
    if curl -s http://localhost:8004/health > /dev/null 2>&1; then
        print_info "✅ 後端服務正常"
    else
        print_warning "❌ 後端服務異常，查看日誌: sudo docker-compose logs backend"
    fi
    
    # Check frontend
    if curl -s http://localhost:3004 > /dev/null 2>&1; then
        print_info "✅ 前端服務正常"
    else
        print_warning "❌ 前端服務異常，查看日誌: sudo docker-compose logs frontend"
    fi
}

# Show final information
show_final_info() {
    print_header "部署完成"
    
    print_info "🎉 HR Performance System 部署完成！"
    echo ""
    print_info "🌐 系統存取位址："
    print_info "   前端: http://$(hostname):3004"
    print_info "   後端 API: http://$(hostname):8004"
    print_info "   API 文檔: http://$(hostname):8004/docs"
    echo ""
    print_info "🔧 管理指令："
    print_info "   查看狀態: ./scripts/manage.sh status"
    print_info "   查看日誌: ./scripts/manage.sh logs"
    print_info "   重啟服務: ./scripts/manage.sh restart"
    echo ""
    print_info "👤 預設管理員帳號："
    print_info "   使用者名稱: admin"
    print_info "   密碼: admin123"
    echo ""
    print_info "💡 提示: 如需初始化資料庫，請先設定 .env 中的資料庫連接資訊"
}

# Main execution
main() {
    print_header "HR Performance System - 一鍵部署"
    
    check_prerequisites
    setup_environment
    deploy_app
    
    if [ "$1" != "--skip-db" ]; then
        init_database
    fi
    
    verify_deployment
    show_final_info
}

main "$@"