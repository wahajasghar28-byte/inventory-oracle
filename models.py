from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model with email and password authentication"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    products = relationship("Product", back_populates="owner", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    """Product model with owner reference"""
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), index=True, nullable=False)
    category = Column(String(50), default="General")
    stock = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    created_at = Column(Date, default=date.today)
    owner = relationship("User", back_populates="products")
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        # Unique constraint per user - same product name can exist for different users
        # but not for the same user
    )


class Sale(Base):
    """Sale model with proper tracking"""
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    sold_on = Column(Date, default=date.today, index=True)
    created_at = Column(Date, default=date.today)
    product = relationship("Product", back_populates="sales")
    user = relationship("User", back_populates="sales")
