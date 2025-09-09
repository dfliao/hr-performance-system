#!/bin/bash

# Database Status Check Script
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

# Check if containers are running
check_containers() {
    print_header "檢查 Docker 容器狀態"
    
    if docker-compose ps | grep -q "postgres.*Up"; then
        print_info "✅ PostgreSQL 容器正在運行"
        POSTGRES_RUNNING=true
    elif docker-compose -f docker-compose.prod.yml ps | grep -q "postgres.*Up"; then
        print_info "✅ PostgreSQL 容器正在運行 (生產環境)"
        POSTGRES_RUNNING=true
        PROD_ENV=true
    else
        print_error "❌ PostgreSQL 容器未運行"
        POSTGRES_RUNNING=false
    fi
    
    if [ "$POSTGRES_RUNNING" = true ]; then
        if [ "$PROD_ENV" = true ]; then
            COMPOSE_FILE="-f docker-compose.prod.yml"
        else
            COMPOSE_FILE=""
        fi
    fi
}

# Check database connection
check_db_connection() {
    print_header "檢查資料庫連接"
    
    if [ "$POSTGRES_RUNNING" = true ]; then
        if docker-compose $COMPOSE_FILE exec postgres pg_isready -U postgres > /dev/null 2>&1; then
            print_info "✅ 資料庫連接正常"
            DB_CONNECTED=true
        else
            print_error "❌ 無法連接到資料庫"
            DB_CONNECTED=false
        fi
    else
        print_error "❌ PostgreSQL 容器未運行，無法檢查連接"
        DB_CONNECTED=false
    fi
}

# Check if database exists
check_database_exists() {
    print_header "檢查資料庫是否存在"
    
    if [ "$DB_CONNECTED" = true ]; then
        if docker-compose $COMPOSE_FILE exec postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -qw hr_performance; then
            print_info "✅ 資料庫 'hr_performance' 存在"
            DB_EXISTS=true
        else
            print_warning "❌ 資料庫 'hr_performance' 不存在"
            DB_EXISTS=false
        fi
    fi
}

# Check migration status
check_migration_status() {
    print_header "檢查 Alembic 遷移狀態"
    
    if [ "$POSTGRES_RUNNING" = true ]; then
        if docker-compose $COMPOSE_FILE exec backend alembic current 2>/dev/null | grep -q "001"; then
            print_info "✅ 資料庫已遷移到版本 001"
            MIGRATED=true
        else
            print_warning "❌ 資料庫尚未遷移或遷移不完整"
            MIGRATED=false
        fi
    fi
}

# Check tables exist
check_tables() {
    print_header "檢查資料表是否存在"
    
    if [ "$DB_EXISTS" = true ]; then
        EXPECTED_TABLES=("departments" "users" "projects" "rule_packs" "rules" "periods" "events" "scores" "audit_logs")
        MISSING_TABLES=()
        
        for table in "${EXPECTED_TABLES[@]}"; do
            if docker-compose $COMPOSE_FILE exec postgres psql -U postgres -d hr_performance -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '$table');" | grep -q "t"; then
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
            COUNT=$(docker-compose $COMPOSE_FILE exec postgres psql -U postgres -d hr_performance -t -c "SELECT COUNT(*) FROM $table;" | tr -d ' ')
            
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
    
    if [ "$POSTGRES_RUNNING" = false ]; then
        echo "🔧 需要啟動 PostgreSQL 容器："
        echo "   docker-compose up -d postgres"
        echo "   或"
        echo "   docker-compose -f docker-compose.prod.yml up -d postgres"
        echo ""
    fi
    
    if [ "$DB_CONNECTED" = false ] && [ "$POSTGRES_RUNNING" = true ]; then
        echo "🔧 資料庫連接問題，請檢查："
        echo "   docker-compose logs postgres"
        echo ""
    fi
    
    if [ "$DB_EXISTS" = false ]; then
        echo "🔧 需要創建資料庫："
        echo "   docker-compose $COMPOSE_FILE exec postgres createdb -U postgres hr_performance"
        echo ""
    fi
    
    if [ "$MIGRATED" = false ]; then
        echo "🔧 需要執行資料庫遷移："
        echo "   docker-compose $COMPOSE_FILE exec backend alembic upgrade head"
        echo ""
    fi
    
    if [ "$TABLES_EXIST" = true ]; then
        echo "🔧 如果需要初始化樣本資料："
        echo "   docker-compose $COMPOSE_FILE exec backend python scripts/create_sample_data.py"
        echo ""
    fi
    
    if [ "$TABLES_EXIST" = true ] && [ "$MIGRATED" = true ]; then
        echo "✅ 資料庫狀態良好，可以開始使用系統！"
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
    print_header "HR Performance System - 資料庫狀態檢查"
    
    check_containers
    check_db_connection
    check_database_exists
    check_migration_status
    check_tables
    check_data
    provide_recommendations
}

main "$@"