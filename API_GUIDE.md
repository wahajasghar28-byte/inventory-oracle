# SmartStock AI - API Guide & Usage

## 🎯 Overview

SmartStock AI v2.0 is a complete inventory management system with:
- ✅ User authentication (signup/login with JWT)
- ✅ Product management
- ✅ Sales tracking
- ✅ AI-powered forecasting
- ✅ Comprehensive error handling
- ✅ Concurrent transaction safety

---

## 🚀 Quick Start

### 1. Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# For production, update SECRET_KEY:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Run the Server

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔐 Authentication

### Register New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2026-10-22"
  }
}
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Get Current User

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📦 Products Management

### Create Product

```bash
curl -X POST "http://localhost:8000/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "T-Shirt",
    "category": "Clothing",
    "stock": 100,
    "reorder_level": 20,
    "price": 15.99
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "T-Shirt",
  "category": "Clothing",
  "stock": 100,
  "reorder_level": 20,
  "price": 15.99,
  "owner_id": 1,
  "created_at": "2026-10-22"
}
```

### List Products

```bash
# Get all products
curl -X GET "http://localhost:8000/products" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search products
curl -X GET "http://localhost:8000/products?search=shirt" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Limit results
curl -X GET "http://localhost:8000/products?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Single Product

```bash
curl -X GET "http://localhost:8000/products/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Product

```bash
curl -X PUT "http://localhost:8000/products/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock": 150,
    "reorder_level": 25
  }'
```

### Delete Product

```bash
curl -X DELETE "http://localhost:8000/products/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💳 Sales Management

### Record a Sale

```bash
curl -X POST "http://localhost:8000/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 5,
    "sold_on": "2026-10-22"
  }'
```

**Response:**
```json
{
  "id": 1,
  "product_id": 1,
  "user_id": 1,
  "quantity": 5,
  "sold_on": "2026-10-22",
  "created_at": "2026-10-22"
}
```

### List Sales

```bash
# Get recent sales
curl -X GET "http://localhost:8000/sales" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Limit results
curl -X GET "http://localhost:8000/sales?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Sales by Date

```bash
curl -X GET "http://localhost:8000/sales/by-date/2026-10-22" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Dashboard & Analytics

### Get Summary

```bash
curl -X GET "http://localhost:8000/dashboard/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_products": 5,
  "low_stock": 2,
  "todays_sales": 89.95,
  "reorder_suggestions": 1,
  "timestamp": "2026-10-22"
}
```

### Get Sales Forecast

```bash
# Forecast for 7 days
curl -X GET "http://localhost:8000/predict/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Forecast for 14 days
curl -X GET "http://localhost:8000/predict/1?horizon=14" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "product_id": 1,
  "product_name": "T-Shirt",
  "current_stock": 95,
  "forecast_period_days": 7,
  "forecast_sales": 25.5,
  "average_daily_sales": 3.64,
  "days_until_stockout": 26,
  "status": "OK",
  "suggested_order_qty": 0,
  "confidence": "HIGH",
  "data_points": 30
}
```

### Get Reorder Suggestions

```bash
curl -X GET "http://localhost:8000/reorder-suggestions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get AI Explanation of Reorders

```bash
curl -X GET "http://localhost:8000/reorder-suggestions/explain" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (deleted) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (inactive user) |
| 404 | Not Found |
| 409 | Conflict (duplicate product name) |
| 422 | Unprocessable Entity (invalid data) |
| 500 | Server Error |

### Example Error Responses

**Missing Token:**
```json
{
  "detail": "Not authenticated"
}
```

**Invalid Credentials:**
```json
{
  "detail": "Invalid email or password"
}
```

**Insufficient Stock:**
```json
{
  "detail": "Insufficient stock. Available: 10, Requested: 15"
}
```

**Product Not Found:**
```json
{
  "detail": "Product not found"
}
```

---

## 🔄 Concurrency & Transaction Safety

The system handles concurrent requests safely:

- **Database-level locking** on sales operations prevents race conditions
- **Transaction rollback** on any error maintains data consistency
- **Stock validation** before deduction ensures no negative inventory
- **Automatic connection pooling** for optimal performance

---

## 📝 Demo Data Setup

### Python Script to Seed Data

```python
from app.database import SessionLocal
from app import models, security
from datetime import date, timedelta
import random

db = SessionLocal()

# Create demo user
user = models.User(
    email="demo@example.com",
    full_name="Demo User",
    hashed_password=security.hash_password("demo123"),
    is_active=True
)
db.add(user)
db.commit()
db.refresh(user)

# Create demo products
products = [
    ("Shirt", "Clothing", 50, 10, 12.99),
    ("Jeans", "Clothing", 30, 8, 34.99),
    ("Shoes", "Footwear", 20, 5, 49.99),
    ("Hat", "Accessories", 100, 15, 8.99),
]

for name, category, stock, reorder, price in products:
    product = models.Product(
        owner_id=user.id,
        name=name,
        category=category,
        stock=stock,
        reorder_level=reorder,
        price=price
    )
    db.add(product)

db.commit()

# Add some sample sales
for _ in range(50):
    sale = models.Sale(
        user_id=user.id,
        product_id=random.randint(1, 4),
        quantity=random.randint(1, 5),
        sold_on=date.today() - timedelta(days=random.randint(1, 30))
    )
    db.add(sale)

db.commit()
print("Demo data created!")
print("Email: demo@example.com")
print("Password: demo123")
```

---

## 🛡️ Security Best Practices

1. **Always use HTTPS** in production
2. **Keep SECRET_KEY secret** - never commit to version control
3. **Use strong passwords** (min 6 characters, but recommend 12+)
4. **Validate inputs** on the client side and server side
5. **Set CORS_ORIGINS** to only trusted domains
6. **Use environment variables** for sensitive data
7. **Update dependencies** regularly for security patches

---

## 📱 Using with Frontend

### JavaScript/React Example

```javascript
// Register
const registerResponse = await fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword',
    full_name: 'John Doe'
  })
});

const { access_token } = await registerResponse.json();
localStorage.setItem('token', access_token);

// Make authenticated request
const productsResponse = await fetch('http://localhost:8000/products', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});

const products = await productsResponse.json();
```

---

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📞 Support & Issues

- Check the logs: `tail -f app.log`
- Review the database: SQLite browser or psql for PostgreSQL
- Enable debug mode: Set `DEBUG=1` in .env
- Check CORS settings if frontend can't connect
- Verify SECRET_KEY is set in production

---

**Version**: 2.0.0  
**Last Updated**: 2026-10-22  
**Status**: Production Ready ✅
