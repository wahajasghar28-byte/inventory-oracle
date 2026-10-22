# SmartStock AI v2.0 - Production Ready Inventory System

> 🎯 **AI-powered inventory management with full authentication, error handling, and demo-ready features**

---

## 🚀 Features

### ✅ User Management
- **Signup/Registration** - Create account with email and password
- **Secure Login** - JWT token-based authentication
- **Data Isolation** - Each user sees only their own data
- **Account Management** - Get current user info, manage profile

### ✅ Product Management
- **Create Products** - Add items with name, category, stock, price
- **View Products** - List all products with search and pagination
- **Update Products** - Modify any product field
- **Delete Products** - Remove products and associated data

### ✅ Sales Tracking
- **Record Sales** - Log product sales automatically
- **Automatic Deduction** - Stock automatically reduced
- **Sales History** - View all sales with filtering
- **Date-based Reports** - Get sales for specific dates

### ✅ Analytics & AI
- **Dashboard Summary** - Key metrics at a glance
- **Sales Forecasting** - AI predicts future demand
- **Reorder Suggestions** - System recommends when to reorder
- **AI Explanations** - Gemini provides insights (optional)

### ✅ Production Ready
- **Comprehensive Error Handling** - Helpful error messages
- **Concurrency Safety** - Database locking prevents race conditions
- **Input Validation** - All data validated before storage
- **CORS Support** - Frontend-friendly API configuration
- **Scalable** - Ready for PostgreSQL in production

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip/poetry
- PostgreSQL (for production) or SQLite (for development)

### Quick Start

```bash
# 1. Clone/Extract project
cd smartstock

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Generate SECRET_KEY (recommended)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Add output to SECRET_KEY in .env

# 6. Create demo data (optional)
python seed_data.py

# 7. Start server
uvicorn app.main:app --reload
```

### Access Points
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health

---

## 🔐 Authentication

### Register New Account
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response**: JWT token (include in all future requests)

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

### Use Token
```bash
curl -X GET "http://localhost:8000/products" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 API Overview

### Product Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/products` | Create product |
| GET | `/products` | List products |
| GET | `/products/{id}` | Get product details |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

### Sales Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sales` | Record sale |
| GET | `/sales` | List recent sales |
| GET | `/sales/by-date/{date}` | Get sales by date |

### Analytics Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/dashboard/summary` | Dashboard metrics |
| GET | `/predict/{product_id}` | Sales forecast |
| GET | `/reorder-suggestions` | Items to reorder |
| GET | `/reorder-suggestions/explain` | AI explanation |

---

## 📝 Demo Data

### Pre-populated Demo Account
```
Email:    demo@example.com
Password: demo123
```

### Create Demo Data
```bash
python seed_data.py
```

Creates:
- 1 demo user
- 5 demo products (T-Shirt, Jeans, Shoes, Jacket, Hat)
- 40 sample sales (last 30 days)

---

## 🔧 Configuration

### Environment Variables (.env)

```ini
# Database
DATABASE_URL=sqlite:///./smartstock.db
# PostgreSQL: postgresql://user:pass@localhost/dbname

# Security
SECRET_KEY=your-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Optional: Gemini API
GEMINI_API_KEY=
```

---

## 🛡️ Security Features

### ✅ Implemented
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based auth
- **Input Validation**: All fields validated
- **CORS Protection**: Configurable origins
- **Database Locking**: Prevents race conditions
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: (Configure in production)
- **HTTPS Ready**: Use reverse proxy in production

### 🔒 Best Practices
1. Change `SECRET_KEY` before production
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS with SSL certificates
4. Set strong password requirements
5. Configure CORS for your domain only
6. Use environment variables for secrets
7. Enable audit logging
8. Monitor failed login attempts
9. Implement rate limiting
10. Regular security updates

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# 1. Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","full_name":"Test User"}'

# Save the token
TOKEN="copy_token_from_response"

# 2. Create product
curl -X POST "http://localhost:8000/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Product","stock":100,"price":10.99}'

# 3. List products
curl -X GET "http://localhost:8000/products" \
  -H "Authorization: Bearer $TOKEN"

# 4. Record sale
curl -X POST "http://localhost:8000/sales" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":5}'

# 5. Check dashboard
curl -X GET "http://localhost:8000/dashboard/summary" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click on each endpoint
3. Click "Try it out"
4. Enter parameters
5. Click "Execute"

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001 --reload
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Database Locked (SQLite)
```bash
# Normal behavior with SQLite
# Use PostgreSQL for production
```

### Authentication Errors
```bash
# Verify token format
# Should be: Authorization: Bearer <token>
# NOT: Authorization: <token>
```

### CORS Error (Frontend)
```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000
```

---

## 📊 What's Changed from v1.0

### Major Improvements
| Feature | v1.0 | v2.0 |
|---------|------|------|
| Authentication | ❌ None | ✅ JWT + Signup |
| User Isolation | ❌ No | ✅ Yes |
| Error Handling | ⚠️ Basic | ✅ Comprehensive |
| Concurrency | ⚠️ Unsafe | ✅ Database locking |
| Stock Management | ⚠️ Issues | ✅ Validated |
| Product Search | ⚠️ Basic | ✅ Full |
| Sales By Date | ❌ No | ✅ Yes |
| Admin Interface | ❌ No | ✅ Swagger |
| Production Ready | ⚠️ Partial | ✅ Full |

---

## 🚀 Production Deployment

### Using Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Heroku
```bash
git push heroku main
```

### Using Railway/Render
1. Connect GitHub repo
2. Set environment variables
3. Deploy
4. Database auto-configured

---

## 📚 Documentation

- **API_GUIDE.md** - Complete endpoint reference
- **SETUP_GUIDE.md** - Detailed setup instructions
- **README_v2.md** - This file

---

## 💡 Tips for Demo Class

### Before Demo (Prep)
1. Run seed_data.py to populate demo data
2. Start server: `uvicorn app.main:app --reload`
3. Open http://localhost:8000/docs in browser
4. Have credentials handy

### During Demo
1. Show signup process
2. Demonstrate product creation
3. Record a few sales
4. Show stock deduction
5. Display dashboard summary
6. Show forecasts
7. Show API documentation

### Interactive Elements
- Use Swagger UI for live testing
- Show database changes in real-time
- Demonstrate error handling
- Show concurrent operations
- Display AI forecasting

---

## 🤝 Contributing

To improve the project:
1. Report bugs with details
2. Test new features
3. Update documentation
4. Follow code style
5. Add tests for new code

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

## 📞 Support

### Debugging
- Check error messages carefully
- Review app logs
- Test with Swagger UI first
- Verify database connection
- Check environment variables

### Common Issues
1. **Module not found** → `pip install -r requirements.txt`
2. **Port in use** → Use different port
3. **Auth errors** → Check token format
4. **CORS errors** → Update CORS_ORIGINS
5. **Database errors** → Check DATABASE_URL

---

## ✅ Verification Checklist

After installation, verify:
- [ ] Server starts without errors
- [ ] Health check responds
- [ ] Can signup new user
- [ ] Can login with credentials
- [ ] Can create products
- [ ] Can view products
- [ ] Can record sales
- [ ] Stock decreases on sale
- [ ] Dashboard shows metrics
- [ ] Forecasts generate
- [ ] Swagger UI works

---

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- [JWT Authentication](https://jwt.io/)
- [REST API Design](https://restfulapi.net/)
- [Python Best Practices](https://pep8.org/)

---

## 🎉 Ready for Production

This version is production-ready with:
- ✅ Full authentication system
- ✅ Comprehensive error handling  
- ✅ Concurrency safety
- ✅ Input validation
- ✅ CORS support
- ✅ Database migrations
- ✅ Demo data
- ✅ Complete documentation

---

**Version**: 2.0.0  
**Release Date**: 2026-10-22  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-10-22

---

Made with ❤️ for SmartStock AI Demo
