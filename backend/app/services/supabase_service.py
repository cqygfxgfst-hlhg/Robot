# backend/app/services/supabase_service.py

import os
from supabase import create_client, Client
from typing import Dict, Any, Optional

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# 创建 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseService:
    """Supabase 数据库服务类"""
    
    @staticmethod
    def create_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的训练任务记录"""
        try:
            # 确保包含user_id
            if "user_id" not in job_data:
                raise ValueError("user_id is required")
            
            response = supabase.table("jobs").insert(job_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating job: {e}")
            raise
    
    @staticmethod
    def update_job_status(job_id: str, status: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """更新任务状态"""
        try:
            update_data = {"status": status}
            if additional_data:
                update_data.update(additional_data)
            
            response = supabase.table("jobs").update(update_data).eq("id", job_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating job status: {e}")
            raise
    
    @staticmethod
    def get_job(job_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """获取任务信息，支持用户隔离"""
        try:
            query = supabase.table("jobs").select("*").eq("id", job_id)
            
            # 如果提供了user_id，添加用户隔离
            if user_id:
                query = query.eq("user_id", user_id)
            
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting job: {e}")
            return None
    
    @staticmethod
    def list_jobs(user_id: str, limit: int = 10) -> list:
        """获取指定用户的任务列表"""
        try:
            response = supabase.table("jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error listing jobs: {e}")
            return []
    
    @staticmethod
    def get_job_by_sqs_message_id(sqs_message_id: str) -> Optional[Dict[str, Any]]:
        """通过 SQS message ID 获取任务信息"""
        try:
            response = supabase.table("jobs").select("*").eq("sqs_message_id", sqs_message_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting job by SQS message ID: {e}")
            return None
    
    @staticmethod
    def get_retry_jobs(original_job_id: str) -> list:
        """获取指定任务的所有重试任务"""
        try:
            response = supabase.table("jobs").select("*").eq("retry_from", original_job_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting retry jobs: {e}")
            return []
    
    @staticmethod
    def get_job_with_retries(job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息，包括其重试历史"""
        try:
            # 获取原始任务
            job = SupabaseService.get_job(job_id)
            if not job:
                return None
            
            # 获取重试任务
            retry_jobs = SupabaseService.get_retry_jobs(job_id)
            
            # 组合结果
            job["retry_history"] = retry_jobs
            return job
        except Exception as e:
            print(f"Error getting job with retries: {e}")
            return None
    
    @staticmethod
    def mark_job_completed(job_id: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """标记任务为完成状态并记录完成时间"""
        try:
            from datetime import datetime
            update_data = {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            if additional_data:
                update_data.update(additional_data)
            
            response = supabase.table("jobs").update(update_data).eq("id", job_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error marking job as completed: {e}")
            raise
    
    @staticmethod
    def mark_job_failed(job_id: str, error_log: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """标记任务为失败状态并记录失败时间和错误日志"""
        try:
            from datetime import datetime
            update_data = {
                "status": "failed",
                "failed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # 添加错误日志
            if error_log:
                update_data["error_log"] = error_log
            
            if additional_data:
                update_data.update(additional_data)
            
            response = supabase.table("jobs").update(update_data).eq("id", job_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error marking job as failed: {e}")
            raise 