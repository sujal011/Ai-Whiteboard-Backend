from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., max_length=72)

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
