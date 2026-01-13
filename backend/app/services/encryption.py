from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """从配置获取加密密钥，如果不存在则生成一个"""
    key = settings.encryption_key.encode()
    # 使用 SHA256 生成 32 字节密钥，然后 base64 编码
    key_hash = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt_api_key(api_key: str) -> str:
    """加密 API Key"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API Key"""
    try:
        f = Fernet(get_encryption_key())
        decrypted = f.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        # 如果解密失败，可能是密钥不匹配或数据损坏
        # 尝试直接返回（可能是未加密的 key）
        if "InvalidToken" in str(type(e).__name__) or "InvalidToken" in str(e):
            # 如果解密失败，可能是存储时没有加密，直接返回
            # 这在迁移旧数据时可能有用
            return encrypted_key
        raise


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """隐藏 API Key，只显示前几个字符"""
    if len(api_key) <= visible_chars:
        return "*" * len(api_key)
    return api_key[:visible_chars] + "*" * (len(api_key) - visible_chars)

