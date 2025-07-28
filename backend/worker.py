# backend/worker.py

import os
import json
import time
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

from app.services.sqs_service import SQS_QUEUE_URL
from app.services.modal_service import app, train
from app.services.supabase_service import SupabaseService

# 初始化 SQS 客户端
sqs = boto3.client("sqs", region_name=os.getenv("AWS_DEFAULT_REGION"))

def poll_and_process():
    while True:
        resp = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        messages = resp.get("Messages", [])
        if not messages:
            continue

        for msg in messages:
            body = json.loads(msg["Body"])
            receipt_handle = msg["ReceiptHandle"]
            sqs_message_id = msg["MessageId"]

            # 打印收到的所有参数
            print(f"[Worker] 收到 SQS 消息: {json.dumps(body, ensure_ascii=False, indent=2)}")

            # 更新任务状态为运行中
            job_id = body.get("job_id")
            if job_id:
                SupabaseService.update_job_status(
                    job_id, 
                    "running", 
                    {"sqs_message_id": sqs_message_id}
                )
                print(f"Updated job {job_id} status to running (SQS: {sqs_message_id})")
            
            try:
                # 触发 Modal 训练
                print(f"Enqueue Modal train for job {msg['MessageId']}")
                with app.run():
                    result = train.remote(  # 直接调用函数，不需要 app.train
                        model_name=body["model_name"],
                        dataset_url=body["dataset_url"],
                        parameters=body["parameters"]
                    )
                    print(f"Modal training result: {result}")
                    
                    # 更新任务状态为完成并记录完成时间
                    if job_id:
                        SupabaseService.mark_job_completed(job_id)
                        print(f"Updated job {job_id} status to completed with timestamp")
            except Exception as e:
                print(f"Error during training: {str(e)}")
                # 收集详细的错误信息
                import traceback
                error_details = f"""
错误类型: {type(e).__name__}
错误信息: {str(e)}
异常栈:
{traceback.format_exc()}
任务参数:
- 模型名称: {body.get('model_name', 'N/A')}
- 数据集地址: {body.get('dataset_url', 'N/A')}
- 参数: {body.get('parameters', 'N/A')}
- SQS消息ID: {sqs_message_id}
时间: {datetime.utcnow().isoformat()}
"""
                
                # 更新任务状态为失败并记录失败时间和错误日志
                if job_id:
                    SupabaseService.mark_job_failed(job_id, error_details)
                    print(f"Updated job {job_id} status to failed with timestamp and error log")

            # TODO: 把 run.object_id 和初始状态写入 Supabase

            # 删除 SQS 消息
            try:
                sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
                print(f"Deleted message {msg['MessageId']}")
            except ClientError as e:
                print(f"Failed to delete message: {e}")

        # 根据需求控制轮询频率
        time.sleep(1)

if __name__ == "__main__":
    print("Worker started, polling SQS...")
    poll_and_process()
