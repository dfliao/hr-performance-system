#!/bin/bash

# MariaDB Database Initialization Script
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

# Check environment
check_environment() {
    if sudo docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "db.*Up"; then
        print_info "檢測到生產環境"
        COMPOSE_FILE="-f docker-compose.prod.yml"
        ENV="production"
    elif sudo docker-compose ps 2>/dev/null | grep -q "db.*Up"; then
        print_info "檢測到開發環境"
        COMPOSE_FILE=""
        ENV="development"
    else
        print_error "未檢測到運行中的 MariaDB 容器"
        print_info "正在啟動資料庫容器..."
        
        if [ -f "docker-compose.prod.yml" ]; then
            print_info "使用生產環境配置..."
            sudo docker-compose -f docker-compose.prod.yml up -d db
            COMPOSE_FILE="-f docker-compose.prod.yml"
            ENV="production"
        else
            print_info "使用開發環境配置..."
            sudo docker-compose up -d db
            COMPOSE_FILE=""
            ENV="development"
        fi
        
        print_info "等待資料庫啟動..."
        sleep 15
    fi
}

# Wait for database to be ready
wait_for_database() {
    print_info "等待資料庫準備就緒..."
    
    for i in {1..30}; do
        if sudo docker-compose $COMPOSE_FILE exec db mysqladmin ping -h localhost --silent > /dev/null 2>&1; then
            print_info "✅ 資料庫已準備就緒"
            return 0
        fi
        
        print_info "等待資料庫啟動... ($i/30)"
        sleep 2
    done
    
    print_error "❌ 資料庫啟動超時"
    exit 1
}

# Check database exists
check_database() {
    print_header "檢查資料庫"
    
    if sudo docker-compose $COMPOSE_FILE exec db mysql -u root -phr_root_password_2024 -e "SHOW DATABASES LIKE 'hr_performance';" | grep -q hr_performance; then
        print_info "✅ 資料庫 'hr_performance' 已存在"
    else
        print_info "建立資料庫 'hr_performance'..."
        sudo docker-compose $COMPOSE_FILE exec db mysql -u root -phr_root_password_2024 -e "CREATE DATABASE IF NOT EXISTS hr_performance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        print_info "✅ 資料庫建立完成"
    fi
}

# Run migrations
run_migrations() {
    print_header "執行資料庫遷移"
    
    print_info "等待後端服務啟動..."
    
    # Start backend if not running
    if ! sudo docker-compose $COMPOSE_FILE ps | grep -q "backend.*Up"; then
        print_info "啟動後端服務..."
        sudo docker-compose $COMPOSE_FILE up -d backend
        sleep 20
    fi
    
    # Run migrations
    print_info "執行 Alembic 遷移..."
    if sudo docker-compose $COMPOSE_FILE exec backend alembic upgrade head; then
        print_info "✅ 資料庫遷移完成"
    else
        print_error "❌ 資料庫遷移失敗"
        print_info "嘗試手動初始化..."
        
        # Try to create tables manually using SQLModel
        if sudo docker-compose $COMPOSE_FILE exec backend python -c "
from app.models import *
from app.core.database import engine
from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)
print('Tables created successfully')
"; then
            print_info "✅ 資料表建立完成"
        else
            print_error "❌ 無法建立資料表"
            exit 1
        fi
    fi
}

# Create sample data
create_sample_data() {
    print_header "建立範例資料"
    
    if sudo docker-compose $COMPOSE_FILE exec backend python scripts/create_sample_data.py; then
        print_info "✅ 範例資料建立完成"
    else
        print_warning "⚠️  範例資料建立失敗（可能已存在）"
    fi
}

# Verify initialization
verify_initialization() {
    print_header "驗證初始化結果"
    
    # Check tables
    EXPECTED_TABLES=("departments" "users" "projects" "rule_packs" "rules" "periods" "events" "scores" "audit_logs")
    MISSING_TABLES=()
    
    for table in "${EXPECTED_TABLES[@]}"; do
        if sudo docker-compose $COMPOSE_FILE exec db mysql -u root -phr_root_password_2024 hr_performance -e "SHOW TABLES LIKE '$table';" | grep -q "$table"; then
            print_info "✅ 資料表 '$table' 存在"
        else
            MISSING_TABLES+=("$table")
        fi
    done
    
    if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
        print_info "✅ 所有資料表建立成功"
    else
        print_error "❌ 缺少資料表: ${MISSING_TABLES[*]}"
        return 1
    fi
    
    # Check sample data
    USER_COUNT=$(sudo docker-compose $COMPOSE_FILE exec db mysql -u root -phr_root_password_2024 hr_performance -e "SELECT COUNT(*) FROM users;" -s -N | tr -d ' ')
    DEPT_COUNT=$(sudo docker-compose $COMPOSE_FILE exec db mysql -u root -phr_root_password_2024 hr_performance -e "SELECT COUNT(*) FROM departments;" -s -N | tr -d ' ')
    
    print_info "👥 使用者數量: $USER_COUNT"
    print_info "🏢 部門數量: $DEPT_COUNT"
    
    if [ "$USER_COUNT" -gt 0 ] && [ "$DEPT_COUNT" -gt 0 ]; then
        print_info "✅ 範例資料載入成功"
    else
        print_warning "⚠️  範例資料可能未正確載入"
    fi
}

# Show final status
show_final_status() {
    print_header "初始化完成"
    
    print_info "🎉 MariaDB 資料庫初始化完成！"
    echo ""
    print_info "🌐 系統存取位址："
    print_info "   前端: http://localhost:3004"
    print_info "   後端 API: http://localhost:8004"
    print_info "   API 文檔: http://localhost:8004/docs"
    echo ""
    print_info "👤 預設管理員帳號："
    print_info "   使用者名稱: admin"
    print_info "   密碼: admin123"
    echo ""
    print_info "🔧 其他管理指令："
    print_info "   檢查狀態: ./scripts/check-mariadb.sh"
    print_info "   查看日誌: sudo docker-compose $COMPOSE_FILE logs -f"
    print_info "   重啟服務: ./quick-deploy.sh restart"
}

# Main execution
main() {
    print_header "HR Performance System - MariaDB 初始化"
    
    check_environment
    wait_for_database
    check_database
    run_migrations
    create_sample_data
    verify_initialization
    show_final_status
}

main "$@"