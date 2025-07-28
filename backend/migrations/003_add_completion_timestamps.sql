-- Migration: 003_add_completion_timestamps.sql
-- Description: 为jobs表添加completed_at和failed_at列，用于记录任务完成和失败的时间
-- Date: 2024-01-XX

-- 添加completed_at列到jobs表
ALTER TABLE jobs 
ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE;

-- 添加failed_at列到jobs表
ALTER TABLE jobs 
ADD COLUMN failed_at TIMESTAMP WITH TIME ZONE;

-- 添加索引以提高查询性能
CREATE INDEX idx_jobs_completed_at ON jobs(completed_at);
CREATE INDEX idx_jobs_failed_at ON jobs(failed_at);

-- 添加注释
COMMENT ON COLUMN jobs.completed_at IS '任务完成的时间戳';
COMMENT ON COLUMN jobs.failed_at IS '任务失败的时间戳'; 