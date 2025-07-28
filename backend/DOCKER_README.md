# Docker 部署指南

## 文件说明

- `Dockerfile` - 容器化配置文件
- `.dockerignore` - Docker构建时忽略的文件
- `docker-compose.yml` - 容器编排配置

## 快速开始

### 1. 构建镜像

```bash
# 在backend目录下执行
docker build -t lerobot-backend .
```

### 2. 运行容器

#### 使用Docker Compose（推荐）

```bash
# 生产环境
docker-compose up -d

# 开发环境（支持热重载）
docker-compose --profile dev up -d
```

#### 使用Docker命令

```bash
# 运行容器
docker run -d \
  --name lerobot-backend \
  -p 8000:8000 \
  --env-file .env \
  lerobot-backend
```

### 3. 查看日志

```bash
# 查看容器日志
docker-compose logs -f backend

# 或者
docker logs -f lerobot-backend
```

### 4. 停止服务

```bash
# 停止并移除容器
docker-compose down

# 或者
docker stop lerobot-backend
docker rm lerobot-backend
```

## 环境变量

确保您的 `.env` 文件包含所有必要的环境变量：

```bash
# AWS配置
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-2
SQS_QUEUE_URL=your_sqs_queue_url

# Supabase配置
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Clerk配置
CLERK_JWKS_URL=your_clerk_jwks_url
CLERK_API_KEY=your_clerk_api_key
CLERK_ISSUER=your_clerk_issuer_url
```

## 健康检查

容器包含健康检查功能：

```bash
# 检查容器健康状态
docker ps

# 查看健康检查详情
docker inspect lerobot-backend | grep Health -A 10
```

## 开发模式

开发模式下支持代码热重载：

```bash
# 启动开发环境
docker-compose --profile dev up -d

# 访问开发服务器
curl http://localhost:8001/health
```

## 生产部署

### 1. 构建生产镜像

```bash
docker build -t lerobot-backend:latest .
```

### 2. 推送到镜像仓库

```bash
# 标记镜像
docker tag lerobot-backend:latest your-registry/lerobot-backend:latest

# 推送镜像
docker push your-registry/lerobot-backend:latest
```

### 3. 部署到服务器

```bash
# 拉取镜像
docker pull your-registry/lerobot-backend:latest

# 运行容器
docker run -d \
  --name lerobot-backend \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  your-registry/lerobot-backend:latest
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep 8000
   
   # 使用不同端口
   docker run -p 8001:8000 lerobot-backend
   ```

2. **环境变量问题**
   ```bash
   # 检查环境变量
   docker exec lerobot-backend env
   
   # 重新加载环境变量
   docker-compose down && docker-compose up -d
   ```

3. **权限问题**
   ```bash
   # 检查容器用户
   docker exec lerobot-backend whoami
   
   # 如果需要，以root用户运行
   docker run --user root lerobot-backend
   ```

### 调试命令

```bash
# 进入容器
docker exec -it lerobot-backend bash

# 查看应用日志
docker logs lerobot-backend

# 检查网络连接
docker exec lerobot-backend curl -f http://localhost:8000/health
```

## 性能优化

### 多阶段构建（可选）

如果需要更小的镜像，可以使用多阶段构建：

```dockerfile
# 构建阶段
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 资源限制

```yaml
# 在docker-compose.yml中添加
services:
  backend:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
``` 