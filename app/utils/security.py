# app/utils/security.py
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False  # suppress the 72-byte hard error
)

def _get_prehash(password: str) -> str:
    """
    Consistently turns any password into a 64-character hex string.
    This bypasses the 72-byte limit of bcrypt.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    # We hash the SHA-256 string instead of the raw password
    prehashed = _get_prehash(password)
    return pwd_context.hash(prehashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # We pre-hash the login attempt to match the stored format
    prehashed = _get_prehash(plain_password)
    return pwd_context.verify(prehashed, hashed_password)