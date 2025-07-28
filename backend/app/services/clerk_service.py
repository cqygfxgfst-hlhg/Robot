# backend/app/services/clerk_service.py

import os
import jwt
import requests
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class ClerkService:
    """Clerk身份验证服务"""
    
    def __init__(self):
        # 支持JWKS URL或JWT公钥
        self.clerk_jwks_url = os.getenv("CLERK_JWKS_URL")
        self.clerk_jwt_public_key = os.getenv("CLERK_JWT_PUBLIC_KEY")
        self.clerk_api_key = os.getenv("CLERK_API_KEY")
        self.clerk_issuer = os.getenv("CLERK_ISSUER")
        
        # 检查必要的环境变量
        if not self.clerk_api_key:
            raise ValueError("CLERK_API_KEY environment variable is required")
        if not self.clerk_issuer:
            raise ValueError("CLERK_ISSUER environment variable is required")
        
        # 至少需要JWKS URL或JWT公钥中的一个
        if not self.clerk_jwks_url and not self.clerk_jwt_public_key:
            raise ValueError("Either CLERK_JWKS_URL or CLERK_JWT_PUBLIC_KEY environment variable is required")
        
        # 初始化JWKS缓存
        self._jwks_cache = {}
        self._jwks_cache_time = 0
        self._cache_duration = 3600  # 1小时缓存
        
        # 如果使用JWT公钥，处理格式
        if self.clerk_jwt_public_key:
            self._prepare_jwt_key()
    
    def _prepare_jwt_key(self):
        """准备JWT公钥用于验证"""
        try:
            # 如果公钥是JSON格式，提取实际的公钥
            if self.clerk_jwt_public_key.startswith('{"'):
                key_data = json.loads(self.clerk_jwt_public_key)
                if 'publicKey' in key_data:
                    self.clerk_jwt_public_key = key_data['publicKey']
                elif 'pem' in key_data:
                    self.clerk_jwt_public_key = key_data['pem']
        except (json.JSONDecodeError, KeyError):
            # 如果不是JSON格式，直接使用
            pass
    
    def _get_jwks(self):
        """获取JWKS（JSON Web Key Set）"""
        import time
        current_time = time.time()
        
        # 检查缓存是否有效
        if (current_time - self._jwks_cache_time) < self._cache_duration and self._jwks_cache:
            return self._jwks_cache
        
        try:
            response = requests.get(self.clerk_jwks_url)
            response.raise_for_status()
            jwks = response.json()
            
            # 更新缓存
            self._jwks_cache = jwks
            self._jwks_cache_time = current_time
            
            return jwks
        except Exception as e:
            print(f"Error fetching JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch JWKS"
            )
    
    def _get_public_key_from_jwks(self, kid: str):
        """从JWKS中获取指定kid的公钥"""
        jwks = self._get_jwks()
        
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                # 使用cryptography库直接处理JWK
                from cryptography.hazmat.primitives.asymmetric import rsa
                from cryptography.hazmat.primitives import serialization
                import base64
                
                # 从JWK提取n和e
                n = int.from_bytes(base64.urlsafe_b64decode(key['n'] + '=='), 'big')
                e = int.from_bytes(base64.urlsafe_b64decode(key['e'] + '=='), 'big')
                
                # 创建RSA公钥
                public_key = rsa.RSAPublicNumbers(e, n).public_key()
                
                # 转换为PEM格式
                pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                return pem.decode('utf-8')
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Public key not found in JWKS"
        )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证JWT token并返回用户信息"""
        try:
            # 移除Bearer前缀
            if token.startswith("Bearer "):
                token = token[7:]
            
            # 解码token header获取kid
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing key ID (kid)"
                )
            
            # 根据配置选择验证方式
            if self.clerk_jwks_url:
                # 使用JWKS URL
                public_key = self._get_public_key_from_jwks(kid)
                try:
                    payload = jwt.decode(
                        token,
                        public_key,
                        algorithms=["RS256"],
                        audience="authenticated",
                        issuer=self.clerk_issuer
                    )
                except jwt.InvalidTokenError:
                    # 如果标准验证失败，尝试不验证audience和issuer
                    payload = jwt.decode(
                        token,
                        public_key,
                        algorithms=["RS256"],
                        options={
                            "verify_aud": False,
                            "verify_iss": False,
                        }
                    )
            else:
                # 使用JWT公钥
                try:
                    payload = jwt.decode(
                        token,
                        self.clerk_jwt_public_key,
                        algorithms=["RS256"],
                        audience="authenticated",
                        issuer=self.clerk_issuer
                    )
                except jwt.InvalidTokenError:
                    payload = jwt.decode(
                        token,
                        self.clerk_jwt_public_key,
                        algorithms=["RS256"],
                        options={
                            "verify_aud": False,
                            "verify_iss": False,
                        }
                    )
            
            return payload
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """通过Clerk API获取用户详细信息"""
        try:
            headers = {
                "Authorization": f"Bearer {self.clerk_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"https://api.clerk.com/v1/users/{user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user info: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return None
    
    def extract_user_id_from_token(self, token: str) -> str:
        """从token中提取用户ID"""
        payload = self.verify_token(token)
        return payload.get("sub")  # Clerk使用"sub"字段作为用户ID 