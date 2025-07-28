# 数据库迁移指南

## 概述
本目录包含数据库schema变更的迁移脚本。由于Supabase的安全限制，某些SQL操作需要通过Supabase Dashboard手动执行。

## 迁移文件

### 1. 001_add_retry_from_column.sql
**目的**: 为jobs表添加retry_from列，用于记录重试来源
**状态**: 待执行

### 2. 002_add_retry_count_column.sql  
**目的**: 为jobs表添加retry_count列，用于记录重试次数
**状态**: 待执行

### 3. 003_add_completion_timestamps.sql
**目的**: 为jobs表添加completed_at和failed_at列，用于记录任务完成和失败的时间
**状态**: 待执行

### 4. 004_add_error_log_column.sql
**目的**: 为jobs表添加error_log列，用于存储任务的错误日志信息
**状态**: 待执行

### 5. 005_add_user_id_column.sql
**目的**: 为jobs表添加user_id列，用于实现用户数据隔离
**状态**: 待执行

## 执行方式

### 方式一：通过Supabase Dashboard（推荐）

1. 登录到您的Supabase项目
2. 进入 "SQL Editor" 页面
3. 依次执行以下SQL语句：

```sql
-- 迁移 001: 添加retry_from列
ALTER TABLE jobs 
ADD COLUMN retry_from UUID REFERENCES jobs(id);

-- 添加索引
CREATE INDEX idx_jobs_retry_from ON jobs(retry_from);

-- 添加注释
COMMENT ON COLUMN jobs.retry_from IS '记录重试来源的任务ID，如果是重试任务则指向原始任务';

-- 迁移 002: 添加retry_count列
ALTER TABLE jobs 
ADD COLUMN retry_count INTEGER DEFAULT 0;

-- 添加索引
CREATE INDEX idx_jobs_retry_count ON jobs(retry_count);

-- 添加注释
COMMENT ON COLUMN jobs.retry_count IS '记录该任务的重试次数，0表示原始任务';

-- 迁移 003: 添加完成时间戳
ALTER TABLE jobs 
ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE jobs 
ADD COLUMN failed_at TIMESTAMP WITH TIME ZONE;

-- 添加索引
CREATE INDEX idx_jobs_completed_at ON jobs(completed_at);
CREATE INDEX idx_jobs_failed_at ON jobs(failed_at);

-- 添加注释
COMMENT ON COLUMN jobs.completed_at IS '任务完成的时间戳';
COMMENT ON COLUMN jobs.failed_at IS '任务失败的时间戳';

-- 迁移 004: 添加错误日志列
ALTER TABLE jobs 
ADD COLUMN error_log TEXT;

-- 添加注释
COMMENT ON COLUMN jobs.error_log IS '存储任务的错误日志信息，包括异常栈、失败原因、标准输出等';

-- 迁移 005: 添加用户ID列
ALTER TABLE jobs 
ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'anonymous';

-- 添加索引
CREATE INDEX idx_jobs_user_id ON jobs(user_id);

-- 添加注释
COMMENT ON COLUMN jobs.user_id IS '用户ID，用于数据隔离，来自Clerk用户系统';

-- 创建复合索引，优化用户查询
CREATE INDEX idx_jobs_user_created ON jobs(user_id, created_at DESC);

### 方式二：通过Python脚本

如果您的Supabase项目配置了自定义函数，可以运行：

```bash
cd backend/migrations
python migrate.py
```

## 验证迁移

执行迁移后，可以通过以下方式验证：

1. 在Supabase Dashboard中查看表结构
2. 运行以下查询确认列已添加：

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'jobs' 
AND column_name IN ('retry_from', 'retry_count', 'completed_at', 'failed_at', 'error_log', 'user_id');
```

## 回滚方案

如果需要回滚迁移，执行以下SQL：

```sql
-- 删除索引
DROP INDEX IF EXISTS idx_jobs_retry_from;
DROP INDEX IF EXISTS idx_jobs_retry_count;
DROP INDEX IF EXISTS idx_jobs_completed_at;
DROP INDEX IF EXISTS idx_jobs_failed_at;

-- 删除列
ALTER TABLE jobs DROP COLUMN IF EXISTS retry_from;
ALTER TABLE jobs DROP COLUMN IF EXISTS retry_count;
ALTER TABLE jobs DROP COLUMN IF EXISTS completed_at;
ALTER TABLE jobs DROP COLUMN IF EXISTS failed_at;
ALTER TABLE jobs DROP COLUMN IF EXISTS error_log;
ALTER TABLE jobs DROP COLUMN IF EXISTS user_id;
```

## 注意事项

1. 执行迁移前请备份数据库
2. 确保在非生产环境先测试迁移脚本
3. 迁移执行后，需要重启后端服务以使用新的字段
4. 如果遇到权限问题，请检查Supabase项目的RLS策略 