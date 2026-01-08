import os
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from auth.database import users_collection

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

# ==============================
# 🔐 TOKEN → USER
# ==============================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = users_collection.find_one({"email": email})

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
