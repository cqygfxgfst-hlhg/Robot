# backend/app/api/jobs.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.sqs_service import enqueue_job
from app.services.supabase_service import SupabaseService
from app.dependencies.auth import get_current_user_id
import uuid
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["jobs"])

class JobRequest(BaseModel):
    model_name: str
    dataset_url: str
    parameters: dict

class JobResponse(BaseModel):
    message_id: str

@router.post("", response_model=JobResponse)
def submit_job(req: JobRequest, user_id: str = Depends(get_current_user_id)):
    print(f"Job API called - Model: {req.model_name}, Dataset: {req.dataset_url}, User: {user_id}")
    
    # 生成唯一任务ID
    job_id = str(uuid.uuid4())
    
    # 创建任务记录
    job_data = {
        "id": job_id,
        "user_id": user_id,  # 添加用户ID
        "model_name": req.model_name,
        "dataset_url": req.dataset_url,
        "parameters": req.parameters,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        # 保存到 Supabase
        SupabaseService.create_job(job_data)
        print(f"Job created in database with ID: {job_id}")
        
        # 添加到 SQS 队列
        payload = {
            "job_id": job_id,
            "model_name": req.model_name,
            "dataset_url": req.dataset_url,
            "parameters": req.parameters,
            "type": "training"
        }
        
        # 添加到 SQS 队列
        msg_id = enqueue_job(payload)
        print(f"Job enqueued successfully with message_id: {msg_id}")
        
        # 更新数据库中的 SQS message ID
        SupabaseService.update_job_status(
            job_id, 
            "queued", 
            {"sqs_message_id": msg_id}
        )
        
        return JobResponse(message_id=job_id)
    except Exception as e:
        print(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 添加一个简单的测试端点来验证路由是否工作
@router.get("/test")
def test_job_endpoint():
    print("Test endpoint called!")
    return {"message": "Job API is working"}

@router.get("")
def list_jobs(user_id: str = Depends(get_current_user_id)):
    """获取当前用户的任务列表"""
    try:
        jobs = SupabaseService.list_jobs(user_id, limit=20)
        return {"jobs": jobs}
    except Exception as e:
        print(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}")
def get_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """获取特定任务信息（用户隔离）"""
    try:
        job = SupabaseService.get_job(job_id, user_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        print(f"Error getting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sqs/{sqs_message_id}")
def get_job_by_sqs_message_id(sqs_message_id: str):
    """通过 SQS message ID 获取任务信息"""
    try:
        job = SupabaseService.get_job_by_sqs_message_id(sqs_message_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        print(f"Error getting job by SQS message ID: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/retry")
def retry_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """重试已失败或已完成的任务（用户隔离）"""
    try:
        # 获取原始任务信息（用户隔离）
        job = SupabaseService.get_job(job_id, user_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # 检查任务状态是否允许重试
        if job["status"] not in ["failed", "completed"]:
            raise HTTPException(status_code=400, detail="Only failed or completed jobs can be retried")
        
        # 生成新的任务ID（保留原始任务信息）
        new_job_id = str(uuid.uuid4())
        
        # 获取原始任务的重试次数
        original_retry_count = job.get("retry_count", 0)
        
        # 创建新的任务记录
        new_job_data = {
            "id": new_job_id,
            "user_id": user_id,  # 保持用户ID一致
            "model_name": job["model_name"],
            "dataset_url": job["dataset_url"],
            "parameters": job["parameters"],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "retry_from": job_id,  # 记录重试来源
            "retry_count": original_retry_count + 1  # 增加重试次数
        }
        
        # 保存到 Supabase
        SupabaseService.create_job(new_job_data)
        print(f"Retry job created in database with ID: {new_job_id}")
        
        # 添加到 SQS 队列
        payload = {
            "job_id": new_job_id,
            "model_name": job["model_name"],
            "dataset_url": job["dataset_url"],
            "parameters": job["parameters"],
            "type": "training"
        }
        
        # 添加到 SQS 队列
        msg_id = enqueue_job(payload)
        print(f"Retry job enqueued successfully with message_id: {msg_id}")
        
        # 更新数据库中的 SQS message ID
        SupabaseService.update_job_status(
            new_job_id, 
            "queued", 
            {"sqs_message_id": msg_id}
        )
        
        return {"message": "Job retry initiated", "new_job_id": new_job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrying job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/error-log")
def get_job_error_log(job_id: str, user_id: str = Depends(get_current_user_id)):
    """获取任务的错误日志（用户隔离）"""
    try:
        job = SupabaseService.get_job(job_id, user_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job["status"] != "failed":
            raise HTTPException(status_code=400, detail="Only failed jobs have error logs")
        
        return {
            "job_id": job_id,
            "error_log": job.get("error_log", "No error log available"),
            "failed_at": job.get("failed_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting job error log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
