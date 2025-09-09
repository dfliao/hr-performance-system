#!/bin/bash

# HR Performance System - 快速部署指令
# 使用方法: ./quick-deploy.sh [update|restart|status|logs]

# 簡單的顏色輸出
print_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# 更新並重啟
update_and_restart() {
    print_info "🔄 更新程式碼並重啟服務..."
    
    # 拉取最新程式碼
    git pull origin main
    
    # 停止現有服務
    sudo docker-compose down
    
    # 重新建置並啟動
    sudo docker-compose up -d --build
    
    # 等待服務啟動
    sleep 15
    
    # 檢查狀態
    check_status
}

# 重啟服務
restart_services() {
    print_info "🔄 重啟服務..."
    sudo docker-compose restart
    sleep 10
    check_status
}

# 檢查狀態
check_status() {
    print_info "📊 檢查服務狀態..."
    
    # 顯示容器狀態
    sudo docker-compose ps
    
    # 檢查服務健康狀態
    echo ""
    if curl -s http://localhost:8004/health > /dev/null; then
        print_info "✅ 後端服務正常 (http://localhost:8004)"
    else
        print_warning "❌ 後端服務異常"
    fi
    
    if curl -s http://localhost:3004 > /dev/null; then
        print_info "✅ 前端服務正常 (http://localhost:3004)"
    else
        print_warning "❌ 前端服務異常"
    fi
    
    echo ""
    print_info "🌐 服務 URL："
    print_info "   前端: http://localhost:3004"
    print_info "   後端: http://localhost:8004"
    print_info "   文檔: http://localhost:8004/docs"
}

# 顯示日誌
show_logs() {
    print_info "📋 顯示服務日誌..."
    sudo docker-compose logs -f --tail=50
}

# 快速修復
quick_fix() {
    print_info "🔧 執行快速修復..."
    
    # 停止所有服務
    sudo docker-compose down
    
    # 清理
    sudo docker system prune -f
    
    # 重新啟動
    sudo docker-compose up -d --build
    
    sleep 20
    check_status
}

# 生產環境部署
deploy_prod() {
    print_info "🚀 部署生產環境..."
    
    # 停止開發環境
    sudo docker-compose down
    
    # 啟動生產環境
    sudo docker-compose -f docker-compose.prod.yml up -d --build
    
    sleep 20
    
    # 檢查生產環境狀態
    print_info "📊 生產環境狀態："
    sudo docker-compose -f docker-compose.prod.yml ps
    
    if curl -s http://localhost:8004/health > /dev/null; then
        print_info "✅ 生產環境後端正常"
    else
        print_warning "❌ 生產環境後端異常"
    fi
    
    if curl -s http://localhost:3004 > /dev/null; then
        print_info "✅ 生產環境前端正常"
    else
        print_warning "❌ 生產環境前端異常"
    fi
}

# 主要執行邏輯
case "$1" in
    "update")
        update_and_restart
        ;;
    "restart")
        restart_services
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs
        ;;
    "fix")
        quick_fix
        ;;
    "prod")
        deploy_prod
        ;;
    *)
        echo "HR Performance System 快速部署工具"
        echo ""
        echo "使用方法: $0 [指令]"
        echo ""
        echo "可用指令:"
        echo "  update   - 更新程式碼並重啟服務"
        echo "  restart  - 重啟現有服務"
        echo "  status   - 檢查服務狀態"
        echo "  logs     - 顯示即時日誌"
        echo "  fix      - 快速修復（重置所有服務）"
        echo "  prod     - 切換到生產環境"
        echo ""
        echo "範例:"
        echo "  $0 update    # 更新並重啟"
        echo "  $0 status    # 檢查狀態"
        echo "  $0 logs      # 查看日誌"
        echo ""
        ;;
esac