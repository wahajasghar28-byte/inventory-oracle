from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr


# ========== User Schemas ==========
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(default="", max_length=100)


class UserRegister(UserBase):
    """Schema for user registration/signup"""
    password: str = Field(..., min_length=6, max_length=100, description="Password must be at least 6 characters")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Email cannot be empty")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 0 and len(v) < 2:
            raise ValueError("Full name must be at least 2 characters if provided")
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserOut(UserBase):
    """Schema for user output"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: date


class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ========== Product Schemas ==========
class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(default="General", min_length=1, max_length=50)
    stock: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    price: float = Field(default=0.0, ge=0, allow_inf_nan=False)

    @field_validator("name", "category")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    stock: Optional[int] = Field(default=None, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)

    @field_validator("name", "category")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: date


# ========== Sale Schemas ==========
class SaleCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    sold_on: Optional[date] = None


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    user_id: int
    quantity: int
    sold_on: date
    created_at: date


# ========== Error Response Schemas ==========
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class MessageResponse(BaseModel):
    """Standard message response"""
    message: str
