# backend/app/services/sqs_service.py
from dotenv import load_dotenv
load_dotenv()
import os
import boto3
import json
from botocore.exceptions import ClientError

# 从环境变量读取队列 URL
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

# 初始化 SQS 客户端
sqs = boto3.client("sqs", region_name=os.getenv("AWS_DEFAULT_REGION"))

def enqueue_job(job_payload: dict) -> str:
    """
    将 job_payload 推入 SQS 队列，返回 MessageId。
    """
    try:
        print(f"[SQS] 即将推送到 SQS 的内容: {json.dumps(job_payload, ensure_ascii=False, indent=2)}")
        resp = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(job_payload),
            MessageAttributes={
                'JobType': {
                    'StringValue': job_payload.get("type", "training"),
                    'DataType': 'String'
                }
            }
        )
        return resp['MessageId']
    except ClientError as e:
        # 可根据需要改为日志或自定义异常
        raise RuntimeError(f"Failed to enqueue job: {e}")
