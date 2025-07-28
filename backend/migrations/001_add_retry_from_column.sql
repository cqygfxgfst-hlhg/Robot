-- Migration: 001_add_retry_from_column.sql
-- Description: 为jobs表添加retry_from列，用于记录重试来源
-- Date: 2024-01-XX

-- 添加retry_from列到jobs表
ALTER TABLE jobs 
ADD COLUMN retry_from UUID REFERENCES jobs(id);

-- 添加索引以提高查询性能
CREATE INDEX idx_jobs_retry_from ON jobs(retry_from);

-- 添加注释
COMMENT ON COLUMN jobs.retry_from IS '记录重试来源的任务ID，如果是重试任务则指向原始任务'; 