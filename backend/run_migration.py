#!/usr/bin/env python3
"""
简单的数据库迁移执行脚本
用于在Supabase中执行SQL迁移
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def print_migration_instructions():
    """打印迁移执行说明"""
    print("=" * 60)
    print("数据库迁移执行指南")
    print("=" * 60)
    print()
    print("由于Supabase的安全限制，请手动执行以下SQL语句：")
    print()
    print("1. 登录到您的Supabase项目")
    print("2. 进入 'SQL Editor' 页面")
    print("3. 复制并执行以下SQL语句：")
    print()
    print("-" * 40)
    print("迁移 001: 添加retry_from列")
    print("-" * 40)
    print("""
-- 添加retry_from列
ALTER TABLE jobs 
ADD COLUMN retry_from UUID REFERENCES jobs(id);

-- 添加索引
CREATE INDEX idx_jobs_retry_from ON jobs(retry_from);

-- 添加注释
COMMENT ON COLUMN jobs.retry_from IS '记录重试来源的任务ID，如果是重试任务则指向原始任务';
""")
    print("-" * 40)
    print("迁移 002: 添加retry_count列")
    print("-" * 40)
    print("""
-- 添加retry_count列
ALTER TABLE jobs 
ADD COLUMN retry_count INTEGER DEFAULT 0;

-- 添加索引
CREATE INDEX idx_jobs_retry_count ON jobs(retry_count);

-- 添加注释
COMMENT ON COLUMN jobs.retry_count IS '记录该任务的重试次数，0表示原始任务';
""")
    print("-" * 40)
    print("迁移 003: 添加完成时间戳")
    print("-" * 40)
    print("""
-- 添加completed_at列
ALTER TABLE jobs 
ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE;

-- 添加failed_at列
ALTER TABLE jobs 
ADD COLUMN failed_at TIMESTAMP WITH TIME ZONE;

-- 添加索引
CREATE INDEX idx_jobs_completed_at ON jobs(completed_at);
CREATE INDEX idx_jobs_failed_at ON jobs(failed_at);

-- 添加注释
COMMENT ON COLUMN jobs.completed_at IS '任务完成的时间戳';
COMMENT ON COLUMN jobs.failed_at IS '任务失败的时间戳';
""")
    print("-" * 40)
    print("迁移 004: 添加错误日志列")
    print("-" * 40)
    print("""
-- 添加error_log列
ALTER TABLE jobs 
ADD COLUMN error_log TEXT;

-- 添加注释
COMMENT ON COLUMN jobs.error_log IS '存储任务的错误日志信息，包括异常栈、失败原因、标准输出等';
""")
    print("-" * 40)
    print("验证迁移")
    print("-" * 40)
    print("""
-- 验证列是否添加成功
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'jobs' 
AND column_name IN ('retry_from', 'retry_count', 'completed_at', 'failed_at', 'error_log');
""")
    print()
    print("执行完成后，重试功能将正常工作！")
    print("=" * 60)

if __name__ == "__main__":
    print_migration_instructions() 