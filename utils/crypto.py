"""
Encryption utility for sensitive data (e.g. GST numbers).
Uses Fernet symmetric encryption from the cryptography library.
"""
import os
from cryptography.fernet import Fernet

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "6z8O4yuMbESvpQBdYpdWpx5C27GsrbQHHDVYMq22X7M=")

_fernet = Fernet(ENCRYPTION_KEY)

def encrypt_sensitive_string(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    return _fernet.encrypt(plaintext.encode()).decode()

def decrypt_sensitive_string(ciphertext: str) -> str:
    if not ciphertext:
        return ciphertext
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ciphertext  # Return as-is if not encrypted
