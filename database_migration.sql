-- Smart Sort V2 数据库迁移脚本
-- 请在Railway数据库控制台中执行以下SQL语句

-- 1. 检查smart_score字段是否已存在
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'news' AND column_name = 'smart_score';

-- 2. 如果字段不存在，添加smart_score字段
ALTER TABLE news 
ADD COLUMN smart_score DOUBLE PRECISION DEFAULT 0.0;

-- 3. 验证字段是否添加成功
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'news' AND column_name = 'smart_score';

-- 4. 查看news表结构（可选）
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'news'
ORDER BY ordinal_position; 