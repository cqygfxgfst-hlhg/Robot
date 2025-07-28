#!/usr/bin/env python3
"""
测试数据库字段是否存在
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("错误: 请设置 SUPABASE_URL 和 SUPABASE_ANON_KEY 环境变量")
    exit(1)

# 创建 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_db_fields():
    """测试数据库字段是否存在"""
    print("🔍 检查数据库字段...")
    
    try:
        # 尝试查询所有字段
        response = supabase.table("jobs").select("*").limit(1).execute()
        
        if response.data:
            job = response.data[0]
            print("✅ 成功查询到任务数据")
            print(f"任务字段: {list(job.keys())}")
            
            # 检查特定字段
            required_fields = ['completed_at', 'failed_at', 'retry_from', 'retry_count']
            missing_fields = []
            
            for field in required_fields:
                if field in job:
                    print(f"✅ {field}: 存在")
                else:
                    print(f"❌ {field}: 不存在")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n⚠️  缺少字段: {missing_fields}")
                print("请执行数据库迁移来添加这些字段")
            else:
                print("\n🎉 所有字段都存在！")
                
        else:
            print("⚠️  没有找到任务数据，但表结构可能正常")
            
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        print("可能的原因:")
        print("1. 数据库连接问题")
        print("2. 表不存在")
        print("3. 权限问题")

def test_timestamp_update():
    """测试时间戳更新功能"""
    print("\n🔍 测试时间戳更新功能...")
    
    try:
        from app.services.supabase_service import SupabaseService
        
        # 创建一个测试任务
        from datetime import datetime
        import uuid
        
        test_job_id = str(uuid.uuid4())
        test_job_data = {
            "id": test_job_id,
            "model_name": "test_model",
            "dataset_url": "test_dataset",
            "parameters": {"test": "data"},
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # 创建任务
        SupabaseService.create_job(test_job_data)
        print(f"✅ 创建测试任务: {test_job_id}")
        
        # 测试标记为完成
        SupabaseService.mark_job_completed(test_job_id)
        print("✅ 标记任务为完成")
        
        # 查询任务
        job = SupabaseService.get_job(test_job_id)
        if job and job.get('completed_at'):
            print(f"✅ 完成时间已记录: {job['completed_at']}")
        else:
            print("❌ 完成时间未记录")
        
        # 清理测试数据
        # 注意：这里只是测试，实际生产环境中可能需要保留数据
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("数据库字段测试")
    print("=" * 50)
    
    test_db_fields()
    test_timestamp_update()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50) 