-- Migration: 005_add_user_id_column.sql
-- Description: 为jobs表添加user_id列，用于实现用户数据隔离
-- Date: 2024-01-XX

-- 添加user_id列到jobs表
ALTER TABLE jobs 
ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'anonymous';

-- 添加索引以提高查询性能
CREATE INDEX idx_jobs_user_id ON jobs(user_id);

-- 添加注释
COMMENT ON COLUMN jobs.user_id IS '用户ID，用于数据隔离，来自Clerk用户系统';

-- 创建复合索引，优化用户查询
CREATE INDEX idx_jobs_user_created ON jobs(user_id, created_at DESC); 