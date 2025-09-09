#!/bin/bash

# HR Performance System - Quick Deploy Script
# Usage: ./scripts/deploy.sh [dev|prod|update|restart|stop|logs]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="hr-performance-system"
GIT_REPO="https://github.com/dfliao/hr-performance-system.git"

# Function to print colored output
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

# Check if we're in the project directory
check_project_dir() {
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
}

# Update code from git
update_code() {
    print_header "更新程式碼"
    print_info "從 Git 拉取最新程式碼..."
    
    git fetch origin
    git reset --hard origin/main
    git pull origin main
    
    print_info "✅ 程式碼更新完成"
}

# Deploy development environment
deploy_dev() {
    print_header "部署開發環境"
    
    print_info "停止現有容器..."
    docker-compose down || true
    
    print_info "建置並啟動開發環境..."
    docker-compose up -d --build
    
    sleep 10
    check_services "dev"
}

# Deploy production environment
deploy_prod() {
    print_header "部署生產環境"
    
    print_info "停止現有容器..."
    docker-compose -f docker-compose.prod.yml down || true
    
    print_info "建置並啟動生產環境..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    sleep 15
    check_services "prod"
}

# Update and restart services
update_and_restart() {
    print_header "更新並重啟服務"
    
    update_code
    
    # Determine which environment is running
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_info "檢測到生產環境正在運行..."
        deploy_prod
    else
        print_info "使用開發環境..."
        deploy_dev
    fi
}

# Restart services
restart_services() {
    print_header "重啟服務"
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_info "重啟生產環境服務..."
        docker-compose -f docker-compose.prod.yml restart
        sleep 10
        check_services "prod"
    else
        print_info "重啟開發環境服務..."
        docker-compose restart
        sleep 10
        check_services "dev"
    fi
}

# Stop all services
stop_services() {
    print_header "停止所有服務"
    
    print_info "停止生產環境服務..."
    docker-compose -f docker-compose.prod.yml down || true
    
    print_info "停止開發環境服務..."
    docker-compose down || true
    
    print_info "✅ 所有服務已停止"
}

# Show logs
show_logs() {
    print_header "顯示服務日誌"
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_info "顯示生產環境日誌..."
        docker-compose -f docker-compose.prod.yml logs -f --tail=100
    else
        print_info "顯示開發環境日誌..."
        docker-compose logs -f --tail=100
    fi
}

# Check service health
check_services() {
    local env=$1
    print_header "檢查服務狀態"
    
    # Determine ports based on environment
    if [ "$env" = "prod" ]; then
        FRONTEND_PORT=3004
        BACKEND_PORT=8004
    else
        FRONTEND_PORT=3004
        BACKEND_PORT=8004
    fi
    
    # Check backend
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
        print_info "✅ 後端服務正常 (Port $BACKEND_PORT)"
    else
        print_warning "❌ 後端服務異常 (Port $BACKEND_PORT)"
    fi
    
    # Check frontend
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
        print_info "✅ 前端服務正常 (Port $FRONTEND_PORT)"
    else
        print_warning "❌ 前端服務異常 (Port $FRONTEND_PORT)"
    fi
    
    # Show running containers
    print_info "運行中的容器："
    if [ "$env" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml ps
    else
        docker-compose ps
    fi
    
    print_info "服務 URL："
    print_info "  前端: http://localhost:$FRONTEND_PORT"
    print_info "  後端 API: http://localhost:$BACKEND_PORT"
    print_info "  API 文檔: http://localhost:$BACKEND_PORT/docs"
}

# Initialize database
init_database() {
    print_header "初始化資料庫"
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_info "在生產環境中初始化資料庫..."
        docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
        docker-compose -f docker-compose.prod.yml exec backend python scripts/create_sample_data.py
    else
        print_info "在開發環境中初始化資料庫..."
        docker-compose exec backend alembic upgrade head
        docker-compose exec backend python scripts/create_sample_data.py
    fi
    
    print_info "✅ 資料庫初始化完成"
}

# Backup database
backup_database() {
    print_header "備份資料庫"
    
    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/hr_performance_backup_$TIMESTAMP.sql"
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres hr_performance > "$BACKUP_FILE"
    else
        docker-compose exec postgres pg_dump -U postgres hr_performance > "$BACKUP_FILE"
    fi
    
    print_info "✅ 資料庫備份完成: $BACKUP_FILE"
}

# Clean up Docker resources
cleanup() {
    print_header "清理 Docker 資源"
    
    print_info "清理未使用的容器..."
    docker container prune -f
    
    print_info "清理未使用的映像..."
    docker image prune -f
    
    print_info "清理未使用的卷..."
    docker volume prune -f
    
    print_info "清理未使用的網路..."
    docker network prune -f
    
    print_info "✅ 清理完成"
}

# Show usage
show_usage() {
    echo "HR Performance System 部署工具"
    echo ""
    echo "用法: $0 [command]"
    echo ""
    echo "指令:"
    echo "  dev        - 部署開發環境"
    echo "  prod       - 部署生產環境"
    echo "  update     - 更新程式碼並重啟服務"
    echo "  restart    - 重啟現有服務"
    echo "  stop       - 停止所有服務"
    echo "  logs       - 顯示服務日誌"
    echo "  status     - 檢查服務狀態"
    echo "  init-db    - 初始化資料庫"
    echo "  backup-db  - 備份資料庫"
    echo "  cleanup    - 清理 Docker 資源"
    echo "  help       - 顯示此說明"
    echo ""
    echo "範例:"
    echo "  $0 prod              # 部署生產環境"
    echo "  $0 update            # 更新並重啟"
    echo "  $0 logs              # 查看日誌"
}

# Main execution
main() {
    check_project_dir
    
    case "$1" in
        "dev")
            deploy_dev
            ;;
        "prod")
            deploy_prod
            ;;
        "update")
            update_and_restart
            ;;
        "restart")
            restart_services
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "status")
            if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
                check_services "prod"
            else
                check_services "dev"
            fi
            ;;
        "init-db")
            init_database
            ;;
        "backup-db")
            backup_database
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        "")
            print_info "沒有指定指令，顯示使用說明..."
            show_usage
            ;;
        *)
            print_error "未知指令: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"