from passlib.context import CryptContext

# CryptContext handles hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hashes a plain-text password and returns the hashed version."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)
