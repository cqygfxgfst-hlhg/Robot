#!/usr/bin/env python3
"""
数据库迁移脚本
用于执行Supabase数据库的schema变更
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("错误: 请设置 SUPABASE_URL 和 SUPABASE_ANON_KEY 环境变量")
    sys.exit(1)

# 创建 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def read_sql_file(file_path: str) -> str:
    """读取SQL文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return None

def execute_migration(migration_name: str, sql_content: str) -> bool:
    """执行单个迁移"""
    print(f"执行迁移: {migration_name}")
    try:
        # 使用Supabase的rpc功能执行SQL
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        print(f"✅ 迁移 {migration_name} 执行成功")
        return True
    except Exception as e:
        print(f"❌ 迁移 {migration_name} 执行失败: {str(e)}")
        return False

def check_column_exists(table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    try:
        # 查询表结构
        result = supabase.table(table_name).select(column_name).limit(1).execute()
        return True
    except Exception:
        return False

def run_migrations():
    """运行所有迁移"""
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    print("开始执行数据库迁移...")
    print(f"找到 {len(migration_files)} 个迁移文件")
    
    success_count = 0
    
    for migration_file in migration_files:
        migration_name = migration_file.name
        
        # 检查是否已经执行过
        if migration_name == "001_add_retry_from_column.sql":
            if check_column_exists("jobs", "retry_from"):
                print(f"⏭️  迁移 {migration_name} 已存在，跳过")
                success_count += 1
                continue
        elif migration_name == "002_add_retry_count_column.sql":
            if check_column_exists("jobs", "retry_count"):
                print(f"⏭️  迁移 {migration_name} 已存在，跳过")
                success_count += 1
                continue
        
        # 读取并执行迁移
        sql_content = read_sql_file(migration_file)
        if sql_content:
            if execute_migration(migration_name, sql_content):
                success_count += 1
    
    print(f"\n迁移完成: {success_count}/{len(migration_files)} 个迁移成功执行")
    
    if success_count == len(migration_files):
        print("🎉 所有迁移执行成功！")
    else:
        print("⚠️  部分迁移执行失败，请检查错误信息")

if __name__ == "__main__":
    run_migrations() 