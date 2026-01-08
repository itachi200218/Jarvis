from fastapi import APIRouter, HTTPException, Depends

from auth.models import (
    RegisterRequest,
    LoginRequest,
    UpdateProfileRequest,
    ChangePasswordRequest
)
from auth.database import users_collection
from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# ==============================
# 🔐 REGISTER
# ==============================
@router.post("/register")
def register(data: RegisterRequest):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one({
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "role": "guest",
        "secure_mode": False
    })

    return {"message": "User registered successfully"}

# ==============================
# 🔐 LOGIN
# ==============================
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

# ==============================
# 🔐 GET PROFILE
# ==============================
@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user.get("role", "guest"),
        "secure_mode": current_user.get("secure_mode", False),
    }

# ==============================
# ✏️ UPDATE PROFILE (NAME)
# ==============================
@router.put("/profile")
def update_profile(
    data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"name": data.name}}
    )

    return {"message": "Profile updated successfully"}

# ==============================
# 🔑 CHANGE PASSWORD
# ==============================
@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"password": hash_password(data.new_password)}}
    )

    return {"message": "Password updated successfully"}
