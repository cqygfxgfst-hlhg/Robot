# Clerk身份验证配置指南

## 环境变量配置

在您的 `.env` 文件中添加以下Clerk相关配置：

```bash
# Clerk身份验证配置（推荐使用JWKS URL）
CLERK_JWKS_URL=your_clerk_jwks_url
CLERK_API_KEY=your_clerk_api_key
CLERK_ISSUER=your_clerk_issuer_url

# 或者使用JWT公钥（传统方式）
# CLERK_JWT_PUBLIC_KEY=your_clerk_jwt_public_key
```

## 获取Clerk配置信息

### 1. 登录Clerk Dashboard
访问 [https://dashboard.clerk.com](https://dashboard.clerk.com)

### 2. 选择您的应用
在Clerk Dashboard中选择您的应用

### 3. 获取JWKS URL（推荐）
- 进入 "Settings" > "General" 页面
- 找到 "JWKS URL" 字段
- 复制JWKS URL（格式类似：`https://clerk.your-app.com/.well-known/jwks.json`）
- 设置为 `CLERK_JWKS_URL`

**注意**: JWKS URL是动态获取公钥的现代方式，推荐使用

### 4. 获取JWT Public Key（传统方式）
如果您想使用传统的JWT公钥方式：
- 进入 "JWT Templates" 页面
- 点击 "Create template" 或使用默认模板
- 在模板设置中，确保：
  - Algorithm: RS256
  - Audience: authenticated（重要！）
  - Issuer: 您的Clerk实例URL
- 复制 "Public Key" 值（PEM格式）
- 设置为 `CLERK_JWT_PUBLIC_KEY`

**注意**: 
- 公钥应该是PEM格式，以 `-----BEGIN PUBLIC KEY-----` 开头
- Audience必须设置为 `authenticated`，否则会导致验证失败

### 4. 获取API Key
- 进入 "API Keys" 页面
- 创建新的API Key或使用现有的
- 设置为 `CLERK_API_KEY`

### 5. 获取Issuer URL
- 进入 "Settings" > "General" 页面
- 复制 "Issuer URL" 值（格式类似：`https://clerk.your-app.com`）
- 设置为 `CLERK_ISSUER`

**注意**: Issuer URL应该与JWT模板中的Issuer设置一致

## 前端配置

确保您的前端已经正确配置了Clerk：

1. 在 `frontend/.env.local` 中设置：
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

2. 在 `frontend/middleware.ts` 中配置路由保护：
```typescript
import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  publicRoutes: ["/"]
});

export const config = {
  matcher: ["/((?!.*\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
};
```

## 测试身份验证

配置完成后，您可以测试身份验证功能：

1. 启动后端服务
2. 启动前端服务
3. 登录Clerk账户
4. 创建训练任务
5. 查看任务列表（应该只显示当前用户的任务）

## 故障排除

### 常见问题

1. **"Algorithm not supported" 错误**
   - 确保JWT模板使用RS256算法
   - 检查JWT公钥格式是否正确
   - 运行验证脚本：`python verify_clerk_config.py`

2. **"Invalid token" 错误**
   - 检查JWT模板的audience设置（应该是"authenticated"）
   - 确认issuer URL与JWT模板设置一致
   - 验证token是否过期

3. **"Token is missing the 'aud' claim" 错误**
   - 确保JWT模板的Audience设置为 `authenticated`
   - 检查前端是否正确发送token
   - 验证Clerk应用配置是否正确

3. **"Token verification failed" 错误**
   - 检查JWT公钥是否完整复制
   - 确认公钥格式（PEM或JSON）
   - 验证环境变量是否正确设置

4. **用户数据隔离不工作**
   - 确认数据库迁移已执行
   - 检查user_id字段是否正确设置
   - 验证API调用是否包含Authorization header

5. **前端无法获取Token**
   - 确认Clerk前端配置正确
   - 检查用户是否已登录
   - 验证Clerk应用设置

### 验证配置

运行配置验证脚本：
```bash
cd backend
python verify_clerk_config.py
```

### 调试步骤

1. **检查环境变量**
   ```bash
   echo $CLERK_JWT_PUBLIC_KEY
   echo $CLERK_API_KEY
   echo $CLERK_ISSUER
   ```

2. **测试JWT公钥格式**
   - 确保以 `-----BEGIN PUBLIC KEY-----` 开头
   - 或者包含正确的JSON结构

3. **验证Issuer URL**
   - 格式：`https://clerk.your-app.com`
   - 与JWT模板中的issuer设置一致 