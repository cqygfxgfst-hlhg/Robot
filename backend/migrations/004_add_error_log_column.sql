-- Migration: 004_add_error_log_column.sql
-- Description: 为jobs表添加error_log列，用于存储任务的错误日志信息
-- Date: 2024-01-XX

-- 添加error_log列到jobs表
ALTER TABLE jobs 
ADD COLUMN error_log TEXT;

-- 添加注释
COMMENT ON COLUMN jobs.error_log IS '存储任务的错误日志信息，包括异常栈、失败原因、标准输出等'; 