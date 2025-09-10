#!/bin/bash

# HR Performance System - 系統管理腳本
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

# Show system status
status() {
    print_header "系統狀態"
    
    print_info "Docker 容器狀態:"
    sudo docker-compose ps
    
    echo ""
    print_info "系統資源使用:"
    df -h | head -1
    df -h | grep -E '/$|/volume' || true
    
    echo ""
    print_info "記憶體使用:"
    free -h || true
    
    echo ""
    print_info "系統負載:"
    uptime
}

# Show logs
logs() {
    SERVICE="$1"
    if [ -z "$SERVICE" ]; then
        print_info "顯示所有服務日誌..."
        sudo docker-compose logs -f --tail=100
    else
        print_info "顯示 $SERVICE 服務日誌..."
        sudo docker-compose logs -f --tail=100 "$SERVICE"
    fi
}

# Restart services
restart() {
    SERVICE="$1"
    if [ -z "$SERVICE" ]; then
        print_header "重啟所有服務"
        sudo docker-compose restart
    else
        print_header "重啟 $SERVICE 服務"
        sudo docker-compose restart "$SERVICE"
    fi
    print_info "✅ 重啟完成"
}

# Stop services
stop() {
    print_header "停止服務"
    sudo docker-compose down
    print_info "✅ 所有服務已停止"
}

# Start services
start() {
    print_header "啟動服務"
    sudo docker-compose up -d
    print_info "等待服務啟動..."
    sleep 10
    print_info "✅ 所有服務已啟動"
}

# Clean up
cleanup() {
    print_header "清理系統"
    
    print_info "清理未使用的 Docker 映像檔..."
    sudo docker image prune -f
    
    print_info "清理未使用的容器..."
    sudo docker container prune -f
    
    print_info "清理未使用的網路..."
    sudo docker network prune -f
    
    print_info "清理未使用的資料卷..."
    sudo docker volume prune -f
    
    print_info "✅ 清理完成"
}

# Database operations
db_backup() {
    print_header "備份資料庫"
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-3306}
    DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-hr_root_password_2024}
    DB_NAME=${DB_NAME:-hr_performance}
    
    BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="backup/hr_performance_${BACKUP_DATE}.sql"
    
    mkdir -p backup
    
    if command -v mysql &> /dev/null; then
        print_info "備份資料庫到: $BACKUP_FILE"
        mysqldump -h "$DB_HOST" -P "$DB_PORT" -u root -p"$DB_ROOT_PASSWORD" \
            --single-transaction --routines --triggers "$DB_NAME" > "$BACKUP_FILE"
        
        gzip "$BACKUP_FILE"
        print_info "✅ 資料庫備份完成: ${BACKUP_FILE}.gz"
    else
        print_warning "❌ MySQL 客戶端未安裝，無法備份資料庫"
    fi
}

# Show help
show_help() {
    echo "HR Performance System - 系統管理腳本"
    echo ""
    echo "用法: $0 <command> [options]"
    echo ""
    echo "指令:"
    echo "  status                    顯示系統狀態"
    echo "  logs [service]           顯示日誌"
    echo "  restart [service]        重啟服務"
    echo "  start                    啟動所有服務"
    echo "  stop                     停止所有服務"
    echo "  cleanup                  清理系統"
    echo "  backup                   備份資料庫"
    echo "  help                     顯示此幫助"
    echo ""
    echo "範例:"
    echo "  $0 status                # 顯示系統狀態"
    echo "  $0 logs backend          # 顯示後端日誌"
    echo "  $0 restart frontend      # 重啟前端服務"
    echo "  $0 backup                # 備份資料庫"
}

# Main execution
main() {
    case "$1" in
        "status")
            status
            ;;
        "logs")
            logs "$2"
            ;;
        "restart")
            restart "$2"
            ;;
        "start")
            start
            ;;
        "stop")
            stop
            ;;
        "cleanup")
            cleanup
            ;;
        "backup")
            db_backup
            ;;
        "help"|"")
            show_help
            ;;
        *)
            print_error "未知指令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"