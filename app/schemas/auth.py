from pydantic import BaseModel, EmailStr,constr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: constr(min_length=10, max_length=15)
    password: constr(min_length=6)
    address: str | None = None