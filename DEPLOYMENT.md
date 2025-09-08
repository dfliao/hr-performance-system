# HR Performance System - 部署指南

這份文件說明如何將 HR 績效管理系統部署到生產環境。

## 🚀 快速部署（推薦）

### 使用 Docker Compose 部署

1. **克隆專案**
   ```bash
   git clone https://github.com/dfliao/hr-performance-system.git
   cd hr-performance-system
   ```

2. **配置環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，設定正確的配置
   ```

3. **啟動服務**
   ```bash
   # 開發環境
   ./scripts/dev-setup.sh
   
   # 生產環境
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **初始化數據**
   ```bash
   # 運行數據庫遷移
   docker-compose exec backend alembic upgrade head
   
   # 創建示例數據（可選）
   docker-compose exec backend python scripts/create_sample_data.py
   ```

## 🏗️ 詳細部署步驟

### 系統需求

- **CPU**: 2 核心以上
- **記憶體**: 4GB 以上
- **硬碟**: 20GB 可用空間
- **作業系統**: Linux (Ubuntu 20.04+, CentOS 8+) 或 Synology DSM 7.0+
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+

### 1. 環境準備

#### 在 Synology NAS 上部署

1. **啟用 Container Manager**
   - 套件中心 → 安裝 Container Manager
   - 開啟 SSH (控制台 → 終端機和 SNMP → 啟動 SSH 功能)

2. **創建專案目錄**
   ```bash
   sudo mkdir -p /volume1/docker/hr-performance-system
   cd /volume1/docker/hr-performance-system
   ```

#### 在 Linux 伺服器上部署

1. **安裝 Docker**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # 重新登入以使用 docker 命令
   ```

2. **安裝 Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

### 2. 下載和配置

1. **下載專案檔案**
   ```bash
   # 方法 1: Git clone（推薦）
   git clone https://github.com/dfliao/hr-performance-system.git
   cd hr-performance-system
   
   # 方法 2: 下載 ZIP
   wget https://github.com/dfliao/hr-performance-system/archive/main.zip
   unzip main.zip
   cd hr-performance-system-main
   ```

2. **配置環境變數**
   ```bash
   cp .env.example .env
   nano .env  # 或使用其他編輯器
   ```

   **重要配置項目：**
   ```env
   # 數據庫配置
   POSTGRES_PASSWORD=your-secure-password
   DATABASE_URL=postgresql://postgres:your-secure-password@postgres:5432/hr_performance
   
   # JWT 密鑰（請生成強密鑰）
   SECRET_KEY=your-very-long-and-secure-secret-key
   
   # Synology 整合
   SYNOLOGY_DRIVE_PATH=/volume1/共享資料夾/hr-evidence
   SYNOLOGY_DRIVE_URL=https://your-synology.local:5001
   LDAP_SERVER_URL=ldap://your-synology.local:389
   
   # 外部服務
   REDMINE_URL=https://your-redmine.local
   CHAT_WEBHOOK_URL=https://your-chat.local/webhooks/performance
   
   # 檔案上傳限制
   MAX_FILE_SIZE=10485760  # 10MB
   ```

3. **創建數據目錄**
   ```bash
   mkdir -p data/postgres data/redis data/uploads logs
   chmod 755 data logs
   ```

### 3. 啟動系統

1. **啟動服務**
   ```bash
   # 開發環境（帶有開發工具）
   docker-compose up -d
   
   # 生產環境（優化配置）
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **檢查服務狀態**
   ```bash
   docker-compose ps
   docker-compose logs -f  # 查看日志
   ```

3. **初始化數據庫**
   ```bash
   # 等待數據庫啟動（約 30 秒）
   sleep 30
   
   # 運行遷移
   docker-compose exec backend alembic upgrade head
   
   # 創建示例數據
   docker-compose exec backend python scripts/create_sample_data.py
   ```

### 4. 驗證部署

1. **檢查服務健康狀態**
   ```bash
   curl http://localhost/health
   curl http://localhost/api/health
   ```

2. **訪問系統**
   - 前端界面: http://your-server-ip
   - API 文檔: http://your-server-ip/docs
   - 管理界面: 使用預設帳號 admin/admin123

3. **檢查日志**
   ```bash
   # 查看所有服務日志
   docker-compose logs
   
   # 查看特定服務日志
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs nginx
   ```

## 🔧 維護和監控

### 日常維護

1. **備份數據庫**
   ```bash
   # 創建備份
   docker-compose exec postgres pg_dump -U postgres hr_performance > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # 自動備份腳本（加入 crontab）
   0 2 * * * cd /path/to/hr-performance-system && docker-compose exec postgres pg_dump -U postgres hr_performance > backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
   ```

2. **更新系統**
   ```bash
   # 拉取最新代碼
   git pull origin main
   
   # 重建和啟動服務
   docker-compose build --no-cache
   docker-compose up -d
   
   # 運行遷移（如果有新的）
   docker-compose exec backend alembic upgrade head
   ```

3. **清理日志和臨時檔案**
   ```bash
   # 清理 Docker 系統
   docker system prune -f
   
   # 輪替日志檔案
   docker-compose exec nginx nginx -s reload
   ```

### 監控和警報

1. **檢查系統資源**
   ```bash
   docker stats  # 即時資源使用情況
   df -h         # 磁碟使用情況
   free -h       # 記憶體使用情況
   ```

2. **健康檢查**
   ```bash
   # 檢查所有服務是否正常
   docker-compose ps | grep -v "Up"
   
   # API 健康檢查
   curl -f http://localhost/health || echo "Health check failed"
   ```

### 效能優化

1. **數據庫優化**
   ```sql
   -- 連接到數據庫
   docker-compose exec postgres psql -U postgres hr_performance
   
   -- 檢查數據庫大小
   SELECT pg_size_pretty(pg_database_size('hr_performance'));
   
   -- 重建索引
   REINDEX DATABASE hr_performance;
   
   -- 清理統計信息
   VACUUM ANALYZE;
   ```

2. **快取配置**
   ```bash
   # Redis 記憶體使用情況
   docker-compose exec redis redis-cli info memory
   
   # 清理快取
   docker-compose exec redis redis-cli flushall
   ```

## 🛡️ 安全配置

### 1. SSL/TLS 配置

1. **獲取 SSL 證書**
   ```bash
   # 使用 Let's Encrypt（需要公網域名）
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

2. **配置 HTTPS**
   - 編輯 `nginx/nginx.conf`
   - 取消註釋 HTTPS server 區塊
   - 配置證書路徑

### 2. 防火牆配置

```bash
# Ubuntu/Debian
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable

# 限制資料庫直接訪問
sudo ufw deny 5432
sudo ufw deny 6379
```

### 3. 定期安全檢查

1. **更新密鑰**
   ```bash
   # 定期更換 JWT 密鑰
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **審計日志**
   ```bash
   # 檢查審計日志
   docker-compose exec backend python scripts/audit_report.py
   ```

## 📊 故障排除

### 常見問題

1. **服務無法啟動**
   ```bash
   # 檢查日志
   docker-compose logs servicename
   
   # 檢查端口佔用
   sudo netstat -tlnp | grep :80
   
   # 重置服務
   docker-compose down
   docker-compose up -d
   ```

2. **數據庫連接失敗**
   ```bash
   # 檢查數據庫狀態
   docker-compose exec postgres pg_isready
   
   # 檢查連接配置
   docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"
   ```

3. **檔案上傳失敗**
   ```bash
   # 檢查目錄權限
   ls -la data/uploads/
   
   # 修正權限
   chmod 755 data/uploads/
   ```

4. **前端白屏**
   ```bash
   # 檢查前端建置
   docker-compose logs frontend
   
   # 重建前端
   docker-compose build frontend --no-cache
   ```

### 效能問題診斷

```bash
# 檢查服務回應時間
time curl http://localhost/api/health

# 檢查數據庫查詢效能
docker-compose exec postgres psql -U postgres hr_performance -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# 檢查記憶體使用
docker stats --no-stream
```

## 📞 支援和協助

如需技術支援：

1. **查看日志**: `docker-compose logs`
2. **檢查配置**: 確認 `.env` 檔案設定
3. **參考文檔**: 查看 `README.md` 和 `CLAUDE.md`
4. **提交問題**: 在 GitHub 建立 issue

---

## 🏷️ 版本資訊

- **系統版本**: 1.0.0
- **最後更新**: 2025-01-08
- **支援的作業系統**: Linux, macOS, Windows (Docker)
- **建議的最小配置**: 2 CPU, 4GB RAM, 20GB 存儲