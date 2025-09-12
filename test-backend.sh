#!/bin/bash

# Test Backend Only Script
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
    print_header "測試最小化後端服務"
    
    # Stop any existing test containers
    print_info "🛑 停止現有測試容器..."
    sudo docker stop hr_test_backend 2>/dev/null || true
    sudo docker rm hr_test_backend 2>/dev/null || true
    sudo docker rmi hr-test-backend 2>/dev/null || true
    
    # Build test backend
    print_info "🔨 建構測試後端..."
    sudo docker build -f backend/Dockerfile.test -t hr-test-backend backend/
    
    # Run test backend
    print_info "🚀 啟動測試後端服務..."
    sudo docker run -d --name hr_test_backend -p 8004:8000 hr-test-backend
    
    # Wait and check
    print_info "⏳ 等待服務啟動..."
    sleep 5
    
    # Check status
    print_info "📊 檢查服務狀態..."
    sudo docker ps | grep hr_test_backend || print_error "容器未運行"
    
    # Test API
    print_info "🧪 測試 API..."
    if curl -f http://localhost:8004/health > /dev/null 2>&1; then
        print_info "✅ 健康檢查通過"
        print_info "🌐 測試 URL:"
        print_info "   健康檢查: http://localhost:8004/health"
        print_info "   根路徑: http://localhost:8004/"
        print_info "   測試端點: http://localhost:8004/api/v1/test"
        
        # Show some test results
        print_info "📋 API 回應："
        curl -s http://localhost:8004/ | head -3
        echo ""
    else
        print_error "❌ API 測試失敗"
        print_info "檢查日誌："
        sudo docker logs hr_test_backend
        return 1
    fi
}

main "$@"