# backend/app/dependencies/auth.py

from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from app.services.clerk_service import ClerkService

# 初始化Clerk服务
clerk_service = ClerkService()

async def get_current_user(authorization: Optional[str] = Header(None)):
    """获取当前用户信息的依赖"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    try:
        # 验证token并获取用户信息
        user_payload = clerk_service.verify_token(authorization)
        user_id = user_payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        return {
            "user_id": user_id,
            "email": user_payload.get("email"),
            "payload": user_payload
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """获取当前用户ID的依赖"""
    user = await get_current_user(authorization)
    return user["user_id"] 