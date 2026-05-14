import hashlib
import hmac
import os


# PBKDF2-HMAC-SHA256 settings
_ITERATIONS = 260_000   # OWASP 2023 recommended minimum for PBKDF2-SHA256
_HASH_NAME   = "sha256"
_SALT_BYTES  = 32       # 256-bit salt


def hash_password(plain_password: str) -> str:
    """
    Hashes a plain-text password using PBKDF2-HMAC-SHA256.

    - No length limit (unlike bcrypt which caps at 72 bytes)
    - Uses a random 256-bit salt per password
    - Returns a single storable string: "salt_hex:key_hex"
    - Zero external dependencies — uses Python's built-in hashlib
    """
    salt = os.urandom(_SALT_BYTES)
    key = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        plain_password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )
    return f"{salt.hex()}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored PBKDF2 hash.
    Uses hmac.compare_digest to prevent timing attacks.
    """
    try:
        salt_hex, key_hex = hashed_password.split(":")
    except ValueError:
        return False  # malformed hash

    salt = bytes.fromhex(salt_hex)
    candidate_key = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        plain_password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )
    # constant-time comparison — prevents timing attacks
    return hmac.compare_digest(candidate_key.hex(), key_hex)
