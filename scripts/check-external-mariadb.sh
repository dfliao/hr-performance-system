#!/bin/bash

# External MariaDB Database Status Check Script
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

# Check MariaDB server status
check_mariadb_server() {
    print_header "檢查外部 MariaDB 伺服器狀態"
    
    print_info "連接資訊: ${DB_HOST}:${DB_PORT}"
    
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT 1;" > /dev/null 2>&1; then
        print_info "✅ MariaDB 伺服器運行正常"
        DB_CONNECTED=true
        
        # Get server version and status
        DB_VERSION=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" -s -N 2>/dev/null)
        UPTIME=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SHOW STATUS LIKE 'Uptime';" -s -N 2>/dev/null | awk '{print $2}')
        
        print_info "📊 MariaDB 版本: $DB_VERSION"
        print_info "⏰ 運行時間: $(($UPTIME / 3600)) 小時 $(($UPTIME % 3600 / 60)) 分鐘"
    else
        print_error "❌ 無法連接到 MariaDB 伺服器"
        DB_CONNECTED=false
    fi
}

# Check database exists
check_database_exists() {
    print_header "檢查 HR 資料庫"
    
    if [ "$DB_CONNECTED" = true ]; then
        if mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SHOW DATABASES LIKE '$DB_NAME';" | grep -q "$DB_NAME"; then
            print_info "✅ 資料庫 '$DB_NAME' 存在"
            DB_EXISTS=true
        else
            print_warning "❌ 資料庫 '$DB_NAME' 不存在"
            DB_EXISTS=false
        fi
    fi
}

# Check user exists and permissions
check_user_permissions() {
    print_header "檢查資料庫使用者"
    
    if [ "$DB_CONNECTED" = true ]; then
        if mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT User FROM mysql.user WHERE User='$DB_USER';" | grep -q "$DB_USER"; then
            print_info "✅ 使用者 '$DB_USER' 存在"
            
            # Test user connection
            if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" > /dev/null 2>&1; then
                print_info "✅ 使用者連接測試成功"
                USER_CONNECTED=true
            else
                print_error "❌ 使用者連接失敗"
                USER_CONNECTED=false
            fi
        else
            print_warning "❌ 使用者 '$DB_USER' 不存在"
            USER_CONNECTED=false
        fi
    fi
}

# Check Docker containers
check_containers() {
    print_header "檢查 Docker 容器狀態"
    
    if sudo docker-compose ps | grep -q "backend.*Up"; then
        print_info "✅ 後端容器運行中"
        BACKEND_RUNNING=true
    else
        print_warning "❌ 後端容器未運行"
        BACKEND_RUNNING=false
    fi
    
    if sudo docker-compose ps | grep -q "redis.*Up"; then
        print_info "✅ Redis 容器運行中"
        REDIS_RUNNING=true
    else
        print_warning "❌ Redis 容器未運行"
        REDIS_RUNNING=false
    fi
    
    if sudo docker-compose ps | grep -q "frontend.*Up"; then
        print_info "✅ 前端容器運行中"
        FRONTEND_RUNNING=true
    else
        print_warning "❌ 前端容器未運行"
        FRONTEND_RUNNING=false
    fi
}

# Check migration status
check_migration_status() {
    print_header "檢查資料庫遷移狀態"
    
    if [ "$BACKEND_RUNNING" = true ]; then
        if sudo docker-compose exec backend alembic current 2>/dev/null | grep -q "head"; then
            print_info "✅ 資料庫已遷移到最新版本"
            MIGRATED=true
        else
            print_warning "❌ 資料庫尚未遷移或遷移不完整"
            MIGRATED=false
        fi
    else
        print_warning "❌ 無法檢查遷移狀態（後端容器未運行）"
        MIGRATED=false
    fi
}

# Check tables exist
check_tables() {
    print_header "檢查資料表"
    
    if [ "$DB_EXISTS" = true ] && [ "$USER_CONNECTED" = true ]; then
        EXPECTED_TABLES=("departments" "users" "projects" "rule_packs" "rules" "periods" "events" "scores" "audit_logs")
        MISSING_TABLES=()
        
        for table in "${EXPECTED_TABLES[@]}"; do
            if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES LIKE '$table';" | grep -q "$table"; then
                print_info "✅ 資料表 '$table' 存在"
            else
                print_error "❌ 資料表 '$table' 不存在"
                MISSING_TABLES+=("$table")
            fi
        done
        
        if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
            print_info "✅ 所有必要的資料表都存在"
            TABLES_EXIST=true
        else
            print_error "❌ 缺少 ${#MISSING_TABLES[@]} 個資料表"
            TABLES_EXIST=false
        fi
    fi
}

# Check table record counts
check_data() {
    print_header "檢查資料表記錄數量"
    
    if [ "$TABLES_EXIST" = true ]; then
        TABLES_TO_CHECK=("departments" "users" "rule_packs" "rules" "events" "scores")
        
        for table in "${TABLES_TO_CHECK[@]}"; do
            COUNT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT COUNT(*) FROM $table;" -s -N 2>/dev/null || echo "0")
            
            if [ "$COUNT" -gt 0 ]; then
                print_info "✅ $table: $COUNT 筆記錄"
            else
                print_warning "⚠️  $table: 0 筆記錄（可能需要初始化樣本資料）"
            fi
        done
    fi
}

# Provide recommendations
provide_recommendations() {
    print_header "建議操作"
    
    if [ "$DB_CONNECTED" = false ]; then
        echo "🔧 MariaDB 連接問題："
        echo "   1. 檢查 MariaDB 服務是否運行"
        echo "   2. 確認連接參數正確：$DB_HOST:$DB_PORT"
        echo "   3. 檢查防火牆設定"
        echo ""
    fi
    
    if [ "$DB_EXISTS" = false ]; then
        echo "🔧 需要創建資料庫："
        echo "   mysql -h $DB_HOST -P $DB_PORT -u root -p -e \"CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\""
        echo ""
    fi
    
    if [ "$USER_CONNECTED" = false ]; then
        echo "🔧 需要創建資料庫使用者："
        echo "   mysql -h $DB_HOST -P $DB_PORT -u root -p -e \"CREATE USER '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';\""
        echo "   mysql -h $DB_HOST -P $DB_PORT -u root -p -e \"GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%'; FLUSH PRIVILEGES;\""
        echo ""
    fi
    
    if [ "$BACKEND_RUNNING" = false ]; then
        echo "🔧 啟動後端服務："
        echo "   sudo docker-compose up -d backend"
        echo ""
    fi
    
    if [ "$MIGRATED" = false ]; then
        echo "🔧 執行資料庫遷移："
        echo "   sudo docker-compose exec backend alembic upgrade head"
        echo ""
    fi
    
    if [ "$TABLES_EXIST" = true ]; then
        echo "🔧 如果需要初始化樣本資料："
        echo "   sudo docker-compose exec backend python scripts/create_sample_data.py"
        echo ""
    fi
    
    if [ "$TABLES_EXIST" = true ] && [ "$MIGRATED" = true ]; then
        echo "✅ 系統狀態良好，可以開始使用！"
        echo ""
        echo "🌐 系統存取位址："
        echo "   前端: http://localhost:3004"
        echo "   後端: http://localhost:8004"
        echo "   API 文檔: http://localhost:8004/docs"
        echo ""
        echo "👤 預設管理員帳號："
        echo "   使用者名稱: admin"
        echo "   密碼: admin123"
    fi
}

# Main execution
main() {
    print_header "HR Performance System - 外部 MariaDB 狀態檢查"
    
    print_info "📋 檢查配置："
    print_info "   MariaDB 主機: $DB_HOST:$DB_PORT"
    print_info "   資料庫名稱: $DB_NAME"
    print_info "   資料庫使用者: $DB_USER"
    echo ""
    
    check_mariadb_server
    check_database_exists
    check_user_permissions
    check_containers
    check_migration_status
    check_tables
    check_data
    provide_recommendations
}

main "$@"