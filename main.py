"""
SmartStock AI - AI-powered inventory management system with proper authentication and error handling
"""
from datetime import date, timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from . import models, schemas, ml, gemini_service, security
from .database import Base, engine, get_db

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartStock AI",
    version="2.0.0",
    description="AI-powered inventory management for small retailers - With Authentication"
)

# ========== CORS Configuration ==========
import os
cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ========== Health & Info Endpoints ==========
@app.get("/", tags=["Info"])
def root():
    """Root endpoint with API information"""
    return {
        "app": "SmartStock AI",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "auth": "/auth/register"
    }


@app.get("/health", tags=["Info"])
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "SmartStock AI",
        "database": "connected"
    }


# ========== Authentication Endpoints ==========
@app.post("/auth/register", response_model=schemas.Token, status_code=201, tags=["Authentication"])
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account

    Email must be unique. Password must be at least 6 characters.
    """
    try:
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            models.User.email == user_data.email.lower()
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create new user
        new_user = models.User(
            email=user_data.email.lower(),
            full_name=user_data.full_name or user_data.email.split("@")[0],
            hashed_password=security.hash_password(user_data.password),
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT token
        access_token = security.create_access_token({"sub": new_user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": schemas.UserOut.model_validate(new_user)
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during registration"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/auth/login", response_model=schemas.Token, tags=["Authentication"])
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password

    Returns JWT token for authenticated requests
    """
    try:
        # Find user by email
        user = db.query(models.User).filter(
            models.User.email == credentials.email.lower()
        ).first()

        if not user or not security.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Generate JWT token
        access_token = security.create_access_token({"sub": user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": schemas.UserOut.model_validate(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.get("/auth/me", response_model=schemas.UserOut, tags=["Authentication"])
def get_current_user_info(current_user: models.User = Depends(security.get_current_user)):
    """Get current authenticated user information"""
    return schemas.UserOut.model_validate(current_user)


# ========== Products Endpoints ==========
@app.post("/products", response_model=schemas.ProductOut, status_code=201, tags=["Products"])
def add_product(
    data: schemas.ProductCreate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new product to inventory

    Requires authentication. Each user has their own products.
    """
    try:
        # Check if product with same name already exists for this user
        existing_product = db.query(models.Product).filter(
            and_(
                models.Product.name == data.name.strip(),
                models.Product.owner_id == current_user.id
            )
        ).first()

        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with this name already exists"
            )

        product = models.Product(
            owner_id=current_user.id,
            name=data.name.strip(),
            category=data.category.strip(),
            stock=data.stock,
            reorder_level=data.reorder_level,
            price=data.price
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return schemas.ProductOut.model_validate(product)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add product"
        )


@app.get("/products", response_model=List[schemas.ProductOut], tags=["Products"])
def list_products(
    search: str = Query("", description="Search products by name"),
    limit: int = Query(default=500, ge=1, le=1000),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all products for authenticated user

    Supports search by product name and pagination via limit
    """
    try:
        query = db.query(models.Product).filter(
            models.Product.owner_id == current_user.id
        )

        if search:
            query = query.filter(
                models.Product.name.ilike(f"%{search}%")
            )

        products = query.order_by(models.Product.name).limit(limit).all()
        return [schemas.ProductOut.model_validate(p) for p in products]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )


@app.get("/products/{pid}", response_model=schemas.ProductOut, tags=["Products"])
def get_product(
    pid: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific product"""
    product = db.query(models.Product).filter(
        and_(
            models.Product.id == pid,
            models.Product.owner_id == current_user.id
        )
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return schemas.ProductOut.model_validate(product)


@app.put("/products/{pid}", response_model=schemas.ProductOut, tags=["Products"])
def update_product(
    pid: int,
    data: schemas.ProductUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update product details

    Any field can be updated individually. Only changed fields are sent.
    """
    try:
        product = db.query(models.Product).filter(
            and_(
                models.Product.id == pid,
                models.Product.owner_id == current_user.id
            )
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return schemas.ProductOut.model_validate(product)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this name already exists"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@app.delete("/products/{pid}", status_code=204, tags=["Products"])
def delete_product(
    pid: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product and all its related sales"""
    try:
        product = db.query(models.Product).filter(
            and_(
                models.Product.id == pid,
                models.Product.owner_id == current_user.id
            )
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        db.delete(product)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )


# ========== Sales Endpoints ==========
@app.post("/sales", response_model=schemas.SaleOut, status_code=201, tags=["Sales"])
def record_sale(
    data: schemas.SaleCreate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a product sale

    Automatically deducts from stock. Validates sufficient inventory.
    """
    try:
        # Get product with locking for concurrent safety
        product = db.query(models.Product).filter(
            and_(
                models.Product.id == data.product_id,
                models.Product.owner_id == current_user.id
            )
        ).with_for_update().first()  # Database-level locking

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Quantity must be greater than 0"
            )

        if data.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.stock}, Requested: {data.quantity}"
            )

        # Deduct from stock and record sale
        product.stock -= data.quantity

        sale = models.Sale(
            user_id=current_user.id,
            product_id=product.id,
            quantity=data.quantity,
            sold_on=data.sold_on or date.today()
        )

        db.add(sale)
        db.commit()
        db.refresh(sale)

        return schemas.SaleOut.model_validate(sale)

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record sale"
        )


@app.get("/sales", response_model=List[schemas.SaleOut], tags=["Sales"])
def list_sales(
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent sales for authenticated user

    Shows most recent sales first
    """
    try:
        sales = db.query(models.Sale).filter(
            models.Sale.user_id == current_user.id
        ).order_by(
            models.Sale.sold_on.desc(),
            models.Sale.id.desc()
        ).limit(limit).all()

        return [schemas.SaleOut.model_validate(s) for s in sales]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sales"
        )


@app.get("/sales/by-date/{sale_date}", response_model=List[schemas.SaleOut], tags=["Sales"])
def get_sales_by_date(
    sale_date: date,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sales for a specific date"""
    try:
        sales = db.query(models.Sale).filter(
            and_(
                models.Sale.user_id == current_user.id,
                models.Sale.sold_on == sale_date
            )
        ).order_by(models.Sale.id.desc()).all()

        return [schemas.SaleOut.model_validate(s) for s in sales]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sales"
        )


# ========== Dashboard & Analytics Endpoints ==========
@app.get("/dashboard/summary", tags=["Dashboard"])
def summary(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary with key metrics

    Returns: total products, low stock count, today's sales, reorder suggestions
    """
    try:
        products = db.query(models.Product).filter(
            models.Product.owner_id == current_user.id
        ).all()

        today_sales_query = db.query(
            func.coalesce(
                func.sum(models.Sale.quantity * models.Product.price),
                0
            )
        ).join(models.Product).filter(
            and_(
                models.Sale.user_id == current_user.id,
                models.Sale.sold_on == date.today()
            )
        ).scalar()

        today_sales = float(today_sales_query or 0)
        low_stock = sum(1 for p in products if p.stock <= p.reorder_level)

        # Safe forecast calculation
        forecasts = []
        for p in products:
            try:
                forecast = ml.product_forecast(db, p, current_user.id)
                if forecast and forecast.get("status") == "REORDER":
                    forecasts.append(forecast)
            except Exception:
                continue

        return {
            "total_products": len(products),
            "low_stock": low_stock,
            "todays_sales": round(today_sales, 2),
            "reorder_suggestions": len(forecasts),
            "timestamp": date.today().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary"
        )


@app.get("/predict/{pid}", tags=["Dashboard"])
def predict(
    pid: int,
    horizon: int = Query(default=7, ge=1, le=90),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI sales forecast for a product

    Predicts future demand based on historical sales patterns.
    Horizon: days into future (1-90 days)
    """
    try:
        product = db.query(models.Product).filter(
            and_(
                models.Product.id == pid,
                models.Product.owner_id == current_user.id
            )
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        forecast = ml.product_forecast(db, product, current_user.id, horizon)
        return forecast

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate forecast"
        )


@app.get("/reorder-suggestions", tags=["Dashboard"])
def reorder_suggestions(
    horizon: int = Query(default=7, ge=1, le=90),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Get products that need reordering based on forecast"""
    try:
        products = db.query(models.Product).filter(
            models.Product.owner_id == current_user.id
        ).all()

        forecasts = []
        for p in products:
            try:
                forecast = ml.product_forecast(db, p, current_user.id, horizon)
                if forecast and forecast.get("status") == "REORDER":
                    forecasts.append(forecast)
            except Exception:
                continue

        sorted_forecasts = sorted(
            forecasts,
            key=lambda f: -f.get("suggested_order_qty", 0)
        )

        return {
            "suggestions": sorted_forecasts,
            "count": len(sorted_forecasts)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reorder suggestions"
        )


@app.get("/reorder-suggestions/explain", tags=["Dashboard"])
def explain(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI explanation of reorder suggestions using Gemini"""
    try:
        products = db.query(models.Product).filter(
            models.Product.owner_id == current_user.id
        ).all()

        forecasts = []
        for p in products:
            try:
                forecast = ml.product_forecast(db, p, current_user.id, 7)
                if forecast and forecast.get("status") == "REORDER":
                    forecasts.append(forecast)
            except Exception:
                continue

        items = sorted(
            forecasts,
            key=lambda item: -item.get("suggested_order_qty", 0)
        )[:10]

        if not items:
            return {"explanation": "Abhi koi product reorder ke liye nahi hai. Sab kuch stock mein theek hai!"}

        try:
            explanation = gemini_service.explain_reorders(items)
            return {"explanation": explanation}
        except Exception as e:
            return {
                "explanation": f"Reorder suggestions available but AI explanation temporarily unavailable. {len(items)} products need reordering."
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation"
        )


# ========== Error Handlers ==========
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return {
        "error": "Validation Error",
        "detail": str(exc),
        "code": "VALIDATION_ERROR"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    return {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred",
        "code": "INTERNAL_ERROR"
    }
