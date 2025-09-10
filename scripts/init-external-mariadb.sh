#!/bin/bash

# External MariaDB Database Initialization Script
set -e

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Set default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-hr_root_password_2024}
DB_NAME=${DB_NAME:-hr_performance}
DB_USER=${DB_USER:-hr_user}
DB_PASSWORD=${DB_PASSWORD:-hr_password_2024}

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

# Check if MariaDB client is available
check_mysql_client() {
    print_header "檢查 MySQL 客戶端"
    
    if command -v mysql &> /dev/null; then
        print_info "✅ MySQL 客戶端已安裝"
    else
        print_error "❌ MySQL 客戶端未安裝"
        print_info "請安裝 MySQL 客戶端："
        print_info "  Ubuntu/Debian: apt-get install mysql-client"
        print_info "  CentOS/RHEL: yum install mysql"
        print_info "  macOS: brew install mysql-client"
        exit 1
    fi
}

# Test database connection
test_connection() {
    print_header "測試資料庫連接"
    
    print_info "連接到 MariaDB: ${DB_HOST}:${DB_PORT}"
    
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" > /dev/null 2>&1; then
        print_info "✅ 資料庫連接成功"
        DB_VERSION=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" -s -N 2>/dev/null)
        print_info "📊 MariaDB 版本: $DB_VERSION"
    else
        print_error "❌ 無法連接到資料庫"
        print_info "請檢查："
        print_info "  1. MariaDB 服務是否運行"
        print_info "  2. 連接參數是否正確 (host: $DB_HOST, port: $DB_PORT)"
        print_info "  3. root 密碼是否正確"
        exit 1
    fi
}

# Create database and user
create_database_and_user() {
    print_header "建立資料庫和使用者"
    
    # Create database
    print_info "檢查資料庫 '$DB_NAME'..."
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SHOW DATABASES LIKE '$DB_NAME';" | grep -q "$DB_NAME"; then
        print_info "✅ 資料庫 '$DB_NAME' 已存在"
    else
        print_info "建立資料庫 '$DB_NAME'..."
        mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "
            CREATE DATABASE $DB_NAME 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci;
        "
        print_info "✅ 資料庫建立完成"
    fi
    
    # Create user
    print_info "檢查使用者 '$DB_USER'..."
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT User FROM mysql.user WHERE User='$DB_USER';" | grep -q "$DB_USER"; then
        print_info "✅ 使用者 '$DB_USER' 已存在"
    else
        print_info "建立使用者 '$DB_USER'..."
        mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "
            CREATE USER '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
            GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
            FLUSH PRIVILEGES;
        "
        print_info "✅ 使用者建立完成"
    fi
    
    # Test user connection
    print_info "測試使用者連接..."
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT 1;" > /dev/null 2>&1; then
        print_info "✅ 使用者連接測試成功"
    else
        print_error "❌ 使用者連接測試失敗"
        exit 1
    fi
}

# Start required services
start_services() {
    print_header "啟動必要服務"
    
    print_info "啟動 Redis..."
    sudo docker-compose up -d redis
    sleep 5
    
    print_info "建立後端容器..."
    sudo docker-compose build backend
    
    print_info "啟動後端服務..."
    sudo docker-compose up -d backend
    sleep 15
}

# Run migrations
run_migrations() {
    print_header "執行資料庫遷移"
    
    print_info "執行 Alembic 遷移..."
    if sudo docker-compose exec backend alembic upgrade head; then
        print_info "✅ 資料庫遷移完成"
    else
        print_error "❌ 資料庫遷移失敗"
        print_info "嘗試手動初始化..."
        
        # Try to create tables manually using SQLModel
        if sudo docker-compose exec backend python -c "
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
    
    if sudo docker-compose exec backend python scripts/create_sample_data.py; then
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
        if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES LIKE '$table';" | grep -q "$table"; then
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
    USER_COUNT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT COUNT(*) FROM users;" -s -N)
    DEPT_COUNT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT COUNT(*) FROM departments;" -s -N)
    
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
    
    print_info "🎉 外部 MariaDB 初始化完成！"
    echo ""
    print_info "🌐 系統存取位址："
    print_info "   前端: http://localhost:3004"
    print_info "   後端 API: http://localhost:8004"
    print_info "   API 文檔: http://localhost:8004/docs"
    echo ""
    print_info "📊 資料庫資訊："
    print_info "   主機: $DB_HOST:$DB_PORT"
    print_info "   資料庫: $DB_NAME"
    print_info "   使用者: $DB_USER"
    echo ""
    print_info "👤 預設管理員帳號："
    print_info "   使用者名稱: admin"
    print_info "   密碼: admin123"
    echo ""
    print_info "🔧 其他管理指令："
    print_info "   檢查狀態: ./scripts/check-external-mariadb.sh"
    print_info "   查看日誌: sudo docker-compose logs -f"
    print_info "   重啟服務: ./quick-deploy.sh restart"
}

# Main execution
main() {
    print_header "HR Performance System - 外部 MariaDB 初始化"
    
    print_info "📋 連接配置："
    print_info "   主機: $DB_HOST"
    print_info "   埠號: $DB_PORT"
    print_info "   資料庫: $DB_NAME"
    print_info "   使用者: $DB_USER"
    echo ""
    
    check_mysql_client
    test_connection
    create_database_and_user
    start_services
    run_migrations
    create_sample_data
    verify_initialization
    show_final_status
}

main "$@"