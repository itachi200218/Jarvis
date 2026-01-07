import os
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

# ==============================
# JWT CONFIG
# ==============================
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==============================
# PASSWORD CONTEXT
# ==============================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ==============================
# PASSWORD UTILS
# ==============================
def _bcrypt_safe_bytes(password: str) -> bytes:
    """
    bcrypt supports max 72 bytes.
    ALWAYS return bytes (never string).
    """
    return password.encode("utf-8")[:72]

def hash_password(password: str) -> str:
    password_bytes = _bcrypt_safe_bytes(password)
    return pwd_context.hash(password_bytes)

def verify_password(password: str, hashed: str) -> bool:
    password_bytes = _bcrypt_safe_bytes(password)
    return pwd_context.verify(password_bytes, hashed)

# ==============================
# JWT TOKEN
# ==============================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
