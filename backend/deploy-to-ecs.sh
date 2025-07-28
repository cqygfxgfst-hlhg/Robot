#!/bin/bash

# ECS部署脚本
# 使用方法: ./deploy-to-ecs.sh

set -e

# 配置变量
AWS_REGION="us-east-2"  # 修改为您的区域
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"  # 修改为您的账户ID
ECR_REPOSITORY="lerobot-backend"
ECS_CLUSTER="lerobot-cluster"
ECS_SERVICE="lerobot-backend-service"
TASK_DEFINITION="lerobot-backend"

echo "🚀 开始部署到ECS..."

# 1. 登录到ECR
echo "📦 登录到ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. 创建ECR仓库（如果不存在）
echo "🏗️ 创建ECR仓库..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# 3. 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker build -t $ECR_REPOSITORY .

# 4. 标记镜像
echo "🏷️ 标记镜像..."
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 5. 推送镜像到ECR
echo "⬆️ 推送镜像到ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 6. 注册新的任务定义
echo "📝 注册任务定义..."
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json --region $AWS_REGION

# 7. 更新服务
echo "🔄 更新ECS服务..."
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --task-definition $TASK_DEFINITION \
    --region $AWS_REGION

# 8. 等待部署完成
echo "⏳ 等待部署完成..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE \
    --region $AWS_REGION

echo "✅ 部署完成！"
echo "🌐 服务URL: http://YOUR_ALB_DNS_NAME"
echo "📊 查看日志: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups/log-group/ecs/lerobot-backend" 