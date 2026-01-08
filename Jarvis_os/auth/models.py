from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class UpdateProfileRequest(BaseModel):
    name: str
    

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str