# 🚀 SmartStock AI v2.0 - START HERE

## ⚡ Quick Start (5 Minutes)

### 1. Extract & Navigate
```bash
unzip smartstock-v2.0.zip
cd smartstock-v2.0
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and change SECRET_KEY to output of:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Create Demo Data (Optional)
```bash
python seed_data.py
```

### 6. Run Server
```bash
uvicorn app.main:app --reload
```

### 7. Test
Visit: **http://localhost:8000/docs**

---

## 📚 Documentation Guide

Read these files in order:

1. **QUICK_REFERENCE.md** ← Start here (5 min)
   - Overview of what's changed
   - Quick setup
   - Common commands

2. **SETUP_GUIDE.md** ← Then this (10 min)
   - Detailed installation
   - Configuration options
   - Troubleshooting

3. **API_GUIDE.md** ← For API reference
   - All endpoints explained
   - cURL examples
   - Response formats

4. **README_v2.md** ← Full overview
   - Feature list
   - Security info
   - Deployment guide

5. **FILES_MANIFEST.txt** ← File reference
   - What each file does
   - Where to copy files

---

## 🔐 Demo Account

After running `seed_data.py`:

```
Email:    demo@example.com
Password: demo123
```

Use these to login in Swagger UI at `/docs`

---

## ✅ What's Fixed

✅ User authentication (signup/login)
✅ JWT tokens
✅ User data isolation
✅ Concurrency safety
✅ Error handling
✅ Stock validation
✅ ML forecasting with safety

---

## 📁 File Structure

```
smartstock-v2.0/
├── app/
│   ├── models.py           (Database models)
│   ├── schemas.py          (Request/response validation)
│   ├── main.py             (FastAPI app + endpoints)
│   ├── security.py         (Authentication)
│   ├── database.py         (Database config)
│   ├── ml.py               (Forecasting)
│   └── __init__.py         (Package init)
├── requirements.txt        (Dependencies)
├── .env.example            (Environment template)
├── seed_data.py            (Demo data script)
├── START_HERE.md           (This file)
├── QUICK_REFERENCE.md      (Quick lookup)
├── SETUP_GUIDE.md          (Detailed setup)
├── API_GUIDE.md            (Endpoint reference)
├── README_v2.md            (Project overview)
├── FILES_MANIFEST.txt      (File descriptions)
└── IMPLEMENTATION_SUMMARY.md (What changed)
```

---

## 🎯 First Steps

1. Read **QUICK_REFERENCE.md** (5 minutes)
2. Setup virtual environment & install deps
3. Create `.env` file with SECRET_KEY
4. Run `python seed_data.py`
5. Start server: `uvicorn app.main:app --reload`
6. Test at http://localhost:8000/docs
7. Create account or use demo@example.com / demo123

---

## 🆘 Need Help?

Check **QUICK_REFERENCE.md** → Troubleshooting section

Common issues:
- Module not found? → `pip install -r requirements.txt`
- Port in use? → `uvicorn app.main:app --port 8001`
- Auth errors? → Check token is included in header

---

## ✨ Ready for Demo Class

This version is production-ready with:
- ✅ Full authentication
- ✅ Comprehensive error handling
- ✅ Demo data included
- ✅ Interactive Swagger UI
- ✅ Complete documentation

---

**Version**: 2.0.0  
**Status**: ✅ Production Ready  
**Start with**: QUICK_REFERENCE.md
