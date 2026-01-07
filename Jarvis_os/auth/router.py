from fastapi import APIRouter, HTTPException
from auth.models import RegisterRequest, LoginRequest
from auth.database import users_collection
from auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔐 REGISTER
@router.post("/register")
def register(data: RegisterRequest):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one({
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password)
    })

    return {"message": "User registered successfully"}

# 🔐 LOGIN
@router.post("/login")
def login(data: LoginRequest):
    user = users_collection.find_one({"email": data.email})

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["email"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }
