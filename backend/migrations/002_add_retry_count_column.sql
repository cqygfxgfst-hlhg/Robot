-- Migration: 002_add_retry_count_column.sql
-- Description: 为jobs表添加retry_count列，用于记录重试次数
-- Date: 2024-01-XX

-- 添加retry_count列到jobs表
ALTER TABLE jobs 
ADD COLUMN retry_count INTEGER DEFAULT 0;

-- 添加索引以提高查询性能
CREATE INDEX idx_jobs_retry_count ON jobs(retry_count);

-- 添加注释
COMMENT ON COLUMN jobs.retry_count IS '记录该任务的重试次数，0表示原始任务'; 