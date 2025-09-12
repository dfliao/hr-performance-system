-- HR Performance System - MariaDB User Setup
-- 請透過 phpMyAdmin 或 MariaDB 控制台執行這些 SQL 指令

-- 1. 建立資料庫 (如果不存在)
CREATE DATABASE IF NOT EXISTS hr_performance 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 建立使用者並設定權限
-- 允許從任何 IP 連接
CREATE USER IF NOT EXISTS 'hr_user'@'%' IDENTIFIED BY 'hr_password_2024';

-- 或者只允許從特定網段連接
-- CREATE USER IF NOT EXISTS 'hr_user'@'192.168.%' IDENTIFIED BY 'hr_password_2024';

-- 3. 授予權限
GRANT ALL PRIVILEGES ON hr_performance.* TO 'hr_user'@'%';

-- 4. 刷新權限
FLUSH PRIVILEGES;

-- 5. 驗證使用者建立成功
SELECT User, Host FROM mysql.user WHERE User = 'hr_user';

-- 6. 測試權限
SHOW GRANTS FOR 'hr_user'@'%';