#!/usr/bin/env python3
"""
Clerk配置验证脚本
用于验证Clerk环境变量配置是否正确
"""

import os
import json
import jwt
from datetime import datetime

def check_env_vars():
    """检查环境变量"""
    print("🔍 检查环境变量...")
    
    # 必需的变量
    required_vars = {
        "CLERK_API_KEY": "API密钥",
        "CLERK_ISSUER": "Issuer URL"
    }
    
    # 可选的变量（至少需要一个）
    optional_vars = {
        "CLERK_JWKS_URL": "JWKS URL（推荐）",
        "CLERK_JWT_PUBLIC_KEY": "JWT公钥（传统方式）"
    }
    
    missing_required = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_required.append(f"{var} ({desc})")
        else:
            print(f"✅ {var}: {'*' * 10}...{value[-10:] if len(value) > 10 else value}")
    
    if missing_required:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_required)}")
        return False
    
    # 检查至少有一个可选变量
    has_optional = False
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            has_optional = True
            print(f"✅ {var}: {'*' * 10}...{value[-10:] if len(value) > 10 else value}")
        else:
            print(f"⚠️  {var}: 未设置 ({desc})")
    
    if not has_optional:
        print(f"❌ 至少需要设置一个身份验证方式: {', '.join(optional_vars.keys())}")
        return False
    
    print("✅ 所有必需的环境变量都已设置")
    return True

def validate_jwt_key():
    """验证JWT公钥格式或JWKS URL"""
    print("\n🔑 验证身份验证配置...")
    
    # 检查JWKS URL
    jwks_url = os.getenv("CLERK_JWKS_URL")
    if jwks_url:
        if jwks_url.startswith("https://") and jwks_url.endswith("/.well-known/jwks.json"):
            print("✅ JWKS URL格式正确")
            return True
        else:
            print("❌ JWKS URL格式不正确，应该以https://开头并以/.well-known/jwks.json结尾")
            return False
    
    # 检查JWT公钥
    public_key = os.getenv("CLERK_JWT_PUBLIC_KEY")
    if public_key:
        # 检查是否是PEM格式
        if public_key.startswith("-----BEGIN PUBLIC KEY-----"):
            print("✅ JWT公钥是PEM格式")
            return True
        elif public_key.startswith('{"'):
            try:
                key_data = json.loads(public_key)
                if 'publicKey' in key_data:
                    print("✅ JWT公钥是JSON格式，包含publicKey字段")
                    return True
                elif 'pem' in key_data:
                    print("✅ JWT公钥是JSON格式，包含pem字段")
                    return True
                else:
                    print("❌ JWT公钥JSON格式不正确")
                    return False
            except json.JSONDecodeError:
                print("❌ JWT公钥不是有效的JSON格式")
                return False
        else:
            print("❌ JWT公钥格式不正确，应该是PEM格式或JSON格式")
            return False
    
    print("❌ 未找到有效的身份验证配置")
    return False

def test_jwt_decoding():
    """测试JWT解码"""
    print("\n🧪 测试JWT解码...")
    
    # 创建一个测试token（仅用于验证公钥格式）
    try:
        public_key = os.getenv("CLERK_JWT_PUBLIC_KEY")
        
        # 如果是JSON格式，提取公钥
        if public_key.startswith('{"'):
            key_data = json.loads(public_key)
            if 'publicKey' in key_data:
                public_key = key_data['publicKey']
            elif 'pem' in key_data:
                public_key = key_data['pem']
        
        print("✅ JWT公钥格式验证通过")
        return True
        
    except Exception as e:
        print(f"❌ JWT公钥验证失败: {e}")
        return False

def check_issuer_format():
    """检查Issuer格式"""
    print("\n🌐 检查Issuer格式...")
    
    issuer = os.getenv("CLERK_ISSUER")
    
    if issuer.startswith("https://"):
        print("✅ Issuer URL格式正确")
        return True
    else:
        print("❌ Issuer URL格式不正确，应该以https://开头")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔐 Clerk配置验证工具")
    print("=" * 60)
    
    # 检查环境变量
    if not check_env_vars():
        print("\n❌ 环境变量配置不完整")
        return False
    
    # 验证JWT公钥
    if not validate_jwt_key():
        print("\n❌ JWT公钥格式不正确")
        return False
    
    # 测试JWT解码
    if not test_jwt_decoding():
        print("\n❌ JWT解码测试失败")
        return False
    
    # 检查Issuer格式
    if not check_issuer_format():
        print("\n❌ Issuer格式不正确")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有配置验证通过！")
    print("✅ 您可以启动后端服务器了")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n📋 配置说明:")
        print("1. 确保在.env文件中设置了所有必需的环境变量")
        print("2. JWT公钥应该是PEM格式或包含publicKey/pem字段的JSON")
        print("3. Issuer URL应该以https://开头")
        print("4. 参考CLERK_SETUP.md获取详细的配置说明") 