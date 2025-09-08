# HR Performance Management System (HR 績效管理系統)

## 系統概述

基於事件驅動架構的績效管理系統，整合 Synology 基礎設施（LDAP、Redmine、Chat、Drive、n8n 自動化）。

## 主要功能

### ✅ 已完成功能
- 🎯 **事件管理系統**：建立、編輯、審核績效事件
- 🧮 **智能計分引擎**：基於可配置規則的自動計算與排名
- 📊 **儀表板系統**：即時績效數據和趨勢分析
- 📈 **報表系統**：個人績效卡片、部門摘要和比較分析
- 🔐 **身份驗證**：LDAP 整合與角色權限控制 (Admin/Manager/Employee/Auditor)
- 📁 **檔案處理**：證據檔案上傳至 Synology Drive，支援多格式
- 🗄️ **資料庫管理**：完整的 Alembic 遷移系統
- 🔍 **審計追蹤**：完整操作歷史與風險評估

### 🚧 開發中功能
- 📥 **批次匯入**：CSV/Excel 批量事件上傳
- 🔗 **完整整合**：Redmine 任務同步、Chat 通知
- 🤖 **n8n 自動化**：工作流程自動化整合
- 🔄 **多級審核**：客製化審核流程

## 技術架構

### 後端 (FastAPI + Python)
- **API 層**：FastAPI 與自動 OpenAPI 文件
- **資料庫**：MariaDB 與 SQLModel ORM
- **身份驗證**：LDAP 整合與 JWT 令牌
- **檔案存儲**：Synology Drive 整合

### 前端 (Vue.js 3 + TypeScript)
- **框架**：Vue 3 與 Composition API
- **UI 庫**：Element Plus 企業級 UI 元件
- **狀態管理**：Pinia 集中式狀態管理
- **建置工具**：Vite 快速開發

### 資料庫架構
- `users`：LDAP 同步的使用者資料
- `departments`：組織架構
- `events`：績效事件與計分
- `rules`：可配置計分規則
- `scores`：計算後的績效分數
- `audit_logs`：完整操作追蹤

## 快速開始

### 開發環境

```bash
# 後端開發
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端開發
cd frontend
npm install
npm run dev
```

### Docker 部署（Synology）

```bash
# 建置並部署
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

## 整合點

### Synology LDAP
- 身份驗證後端
- 使用者和部門同步
- 基於角色的存取控制

### Redmine 整合
- 任務完成自動建立事件
- 專案對應績效事件
- 截止日期監控懲罰事件

### Synology Drive
- 證據檔案存儲
- 簽名 URL 安全存取
- 自動清理政策

## 安全與合規

- LDAP/Active Directory 整合
- JWT 令牌 API 身份驗證
- 基於角色的存取控制
- 所有操作的審計日誌

## 開發指南

請參閱 `CLAUDE.md` 檔案以獲取完整的開發指導和命令參考。

## 聯絡資訊

- 專案負責人：DF Liao
- 組織：GOGOPEAKS.COM
- 技術支援：IT 部門