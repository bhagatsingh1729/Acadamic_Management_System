from datetime import datetime, timedelta, timezone

from jose import jwt
from jose import JWTError

from app.core.config import get_settings

import hashlib
from passlib.context import CryptContext

"""
hashing code explaination:
SHA-256 (Pre-hash step): First, your code uses hashlib.sha256() to turn the password into a fixed 64-character text [^1]. This is done purely to bypass bcrypt's built-in 72-character limit [^1].
bcrypt (Main hashing step): Next, your code passes that 64-character text into pwd_context.hash(), which applies the bcrypt algorithm to generate the final, secure mathematical fingerprint that you save to your database [^1].

"""

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

#----------------------------------------
# JWT Token Handling
#----------------------------------------

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY.get_secret_value()
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES



def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None