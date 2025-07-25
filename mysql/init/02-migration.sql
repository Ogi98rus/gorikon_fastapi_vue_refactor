-- Миграция для добавления системы ролей и статусов
-- Этот скрипт обновляет существующие таблицы

-- Добавляем новые поля в таблицу users
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role ENUM('user', 'admin', 'moderator', 'banned') DEFAULT 'user' NOT NULL,
ADD COLUMN IF NOT EXISTS status ENUM('active', 'inactive', 'suspended', 'banned') DEFAULT 'active' NOT NULL,
ADD COLUMN IF NOT EXISTS banned_until DATETIME NULL,
ADD COLUMN IF NOT EXISTS ban_reason TEXT NULL;

-- Синхронизируем данные: если is_superuser = true, то role = admin
UPDATE users SET role = 'admin' WHERE is_superuser = 1;

-- Синхронизируем данные: если is_active = false, то status = inactive
UPDATE users SET status = 'inactive' WHERE is_active = 0;

-- Добавляем индексы для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_banned_until ON users(banned_until);

-- Обновляем таблицу generations для улучшенной структуры
ALTER TABLE generations 
ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64) NULL COMMENT 'SHA-256 хеш файла',
ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT TRUE COMMENT 'Доступен ли файл для скачивания',
ADD COLUMN IF NOT EXISTS download_count INT DEFAULT 0 COMMENT 'Количество скачиваний',
ADD COLUMN IF NOT EXISTS expires_at DATETIME NULL COMMENT 'Дата истечения срока хранения';

-- Добавляем индексы для generations
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations(user_id);
CREATE INDEX IF NOT EXISTS idx_generations_type ON generations(generator_type);
CREATE INDEX IF NOT EXISTS idx_generations_created_at ON generations(created_at);
CREATE INDEX IF NOT EXISTS idx_generations_available ON generations(is_available);
CREATE INDEX IF NOT EXISTS idx_generations_expires_at ON generations(expires_at);

-- Создаем триггер для автоматического обновления download_count
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS update_download_count 
BEFORE UPDATE ON generations 
FOR EACH ROW 
BEGIN
    -- Если изменился download_count, обновляем timestamp
    IF NEW.download_count != OLD.download_count THEN
        SET NEW.download_count = NEW.download_count;
    END IF;
END$$

DELIMITER ;

-- Создаем представление для статистики пользователей
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.role,
    u.status,
    u.created_at,
    u.last_login,
    COUNT(g.id) as total_generations,
    COUNT(CASE WHEN g.generator_type = 'math' THEN 1 END) as math_generations,
    COUNT(CASE WHEN g.generator_type = 'ktp' THEN 1 END) as ktp_generations,
    COALESCE(SUM(g.download_count), 0) as total_downloads,
    COALESCE(SUM(g.file_size), 0) as total_file_size
FROM users u
LEFT JOIN generations g ON u.id = g.user_id
GROUP BY u.id, u.email, u.full_name, u.role, u.status, u.created_at, u.last_login;

-- Создаем представление для активных пользователей
CREATE OR REPLACE VIEW active_users AS
SELECT *
FROM users 
WHERE status = 'active' 
  AND (banned_until IS NULL OR banned_until < NOW());

-- Создаем представление для заблокированных пользователей  
CREATE OR REPLACE VIEW banned_users AS
SELECT *
FROM users 
WHERE status = 'banned' 
  OR (banned_until IS NOT NULL AND banned_until > NOW());

-- Обновляем комментарии для таблиц
ALTER TABLE users COMMENT = 'Пользователи системы с ролями и статусами';
ALTER TABLE generations COMMENT = 'История генераций пользователей';
ALTER TABLE user_sessions COMMENT = 'Активные сессии пользователей';

-- Создаем процедуру для очистки устаревших данных
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS cleanup_expired_data()
BEGIN
    -- Удаляем истекшие генерации
    UPDATE generations 
    SET is_available = FALSE 
    WHERE expires_at IS NOT NULL 
      AND expires_at < NOW() 
      AND is_available = TRUE;
    
    -- Удаляем старые сессии (старше 30 дней)
    DELETE FROM user_sessions 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
    
    -- Разблокируем пользователей с истекшим сроком блокировки
    UPDATE users 
    SET status = 'active', banned_until = NULL, ban_reason = NULL
    WHERE banned_until IS NOT NULL 
      AND banned_until < NOW() 
      AND status = 'banned';
      
    -- Логируем операцию очистки
    INSERT INTO generations (
        user_id, generator_type, parameters, file_name, original_file_name, 
        file_path, file_size, examples_generated, ip_address, user_agent
    ) VALUES (
        NULL, 'system', '{"action": "cleanup"}', 'cleanup.log', 'System Cleanup', 
        '/var/log/cleanup.log', 0, 0, '127.0.0.1', 'MySQL-Cleanup-Procedure'
    );
END$$

DELIMITER ;

-- Создаем событие для автоматической очистки (выполняется каждый день в 02:00)
CREATE EVENT IF NOT EXISTS daily_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '02:00:00')
DO
  CALL cleanup_expired_data();

-- Включаем планировщик событий
SET GLOBAL event_scheduler = ON;

-- Финальная проверка целостности
-- Убеждаемся что все пользователи имеют корректные роли и статусы
UPDATE users SET role = 'user' WHERE role IS NULL;
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Логируем завершение миграции
SELECT 'Migration completed successfully' as status, NOW() as timestamp; 