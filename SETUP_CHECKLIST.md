# QGENOME Setup Checklist

## ✅ Pre-Flight Checklist

Use this checklist to ensure everything is ready to run.

### Step 1: MongoDB Setup ☐

Choose one option:

#### Option A: Docker (Recommended)
```powershell
# Start MongoDB container
docker run -d -p 27017:27017 --name qgenome-mongo mongo

# Verify it's running
docker ps | Select-String "qgenome-mongo"
```

#### Option B: Local MongoDB
```powershell
# Start MongoDB service
mongod

# Or if installed as service
net start MongoDB
```

#### Option C: MongoDB Atlas (Cloud)
1. Create account at https://www.mongodb.com/atlas
2. Create free cluster
3. Get connection string
4. Update `.env` with connection string

### Verify MongoDB ☐
```powershell
# Test connection
mongosh
# Should connect without errors
# Type 'exit' to quit
```

---

### Step 2: Environment Setup ☐

#### Check Python Environment
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify activation (should see (.venv) in prompt)
# Example: (.venv) PS C:\Users\harsh\final-proj>
```

#### Check Environment Variables
```powershell
# Verify .env file exists
Test-Path .env
# Should return: True

# If False, copy from example
Copy-Item .env.example .env
```

#### Run MongoDB Setup Script ☐
```powershell
python -m backend.setup_mongodb
```

Expected output:
```
================================================================================
QGENOME - MongoDB Setup
================================================================================

[1/3] Connecting to MongoDB...
✓ Connected successfully!

[2/3] Verifying database access...
✓ Database accessible. Collections: None (new database)

[3/3] Creating indexes...
✓ Datasets indexes created
✓ Processing jobs indexes created
✓ Sequence runs indexes created

================================================================================
MongoDB setup completed successfully!
================================================================================
```

---

### Step 3: Start Backend ☐

#### Terminal 1: Backend
```powershell
# From project root
cd c:\Users\harsh\final-proj

# Activate environment
.\.venv\Scripts\Activate.ps1

# Start backend
python -m backend.main
```

#### Verify Backend Started ☐

Look for this output:
```
Connected to MongoDB at mongodb://localhost:27017, database: qgenome
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Test Backend Health ☐
```powershell
# In a new PowerShell window
curl http://localhost:8000/health

# Should return: {"status":"ok"}
```

---

### Step 4: Start Frontend ☐

#### Terminal 2: Frontend
```powershell
# From project root
cd c:\Users\harsh\final-proj\frontend

# Start frontend
npm run dev
```

#### Verify Frontend Started ☐

Look for this output:
```
VITE v5.4.21  ready in 1736 ms

➜  Local:   http://localhost:3000/
➜  Network: http://192.168.x.x:3000/
➜  press h + enter to show help
```

#### Test Frontend ☐
- Open browser to http://localhost:3000/
- Page should load without errors
- No console warnings about 'jsx' attribute

---

### Step 5: Test CLI ☐

#### Terminal 3: CLI
```powershell
# From project root
cd c:\Users\harsh\final-proj

# Activate environment
.\.venv\Scripts\Activate.ps1

# Test CLI help
python -m backend.cli --help
```

#### Run CLI Tests ☐

```powershell
# 1. List datasets (should be empty)
python -m backend.cli dataset list

# 2. Create a test dataset
python -m backend.cli dataset create `
  --name "Test Dataset" `
  --sequences ATGCGTACGATCGATCG CGTAGCTAGCTAGCTA `
  --description "Test sequences"

# 3. List datasets again (should show 1)
python -m backend.cli dataset list

# 4. Create a processing job
python -m backend.cli job create `
  --name "Test Alignment" `
  --algorithm vqe_alignment `
  --sequences ATGCGTACGATCGATCG CGTAGCTAGCTAGCTA

# 5. List jobs
python -m backend.cli job list

# 6. Get job details (use job_id from above)
python -m backend.cli job get <job_id>
```

---

### Step 6: Integration Test ☐

#### Test Frontend → MongoDB → CLI Flow

1. **Frontend Submission** ☐
   - Open http://localhost:3000/
   - Enter two sequences (any valid DNA)
   - Click "Run Alignment"
   - Verify results appear

2. **Check in CLI** ☐
   ```powershell
   # List recent jobs
   python -m backend.cli job list
   
   # Should show the job you just submitted
   ```

3. **Verify in MongoDB** ☐
   ```powershell
   mongosh
   use qgenome
   
   # Check datasets
   db.datasets.countDocuments()
   
   # Check jobs
   db.processing_jobs.countDocuments()
   
   # View a job with details
   db.processing_jobs.findOne()
   
   # Exit mongosh
   exit
   ```

---

### Step 7: API Documentation ☐

#### Access API Docs
- **Swagger UI**: http://localhost:8000/docs ☐
- **ReDoc**: http://localhost:8000/redoc ☐

#### Test New Endpoints

Using Swagger UI, test these endpoints:

1. **POST /datasets** ☐
   - Click "Try it out"
   - Enter test data
   - Execute
   - Verify response

2. **GET /datasets** ☐
   - Should return your test dataset

3. **POST /jobs** ☐
   - Create a job via API
   - Verify in CLI

4. **GET /jobs** ☐
   - Should show all jobs

---

## 🎯 Final Verification

### All Systems Go? ☐

Check all of these:

- ☐ MongoDB is running (mongosh connects)
- ☐ Backend is running (http://localhost:8000/health returns OK)
- ☐ Frontend is running (http://localhost:3000/ loads)
- ☐ CLI works (can list datasets and jobs)
- ☐ Can create dataset via CLI
- ☐ Can submit job via frontend
- ☐ Job appears in CLI
- ☐ Data persists in MongoDB
- ☐ Processing steps are visible
- ☐ No errors in any terminal

---

## 🐛 Troubleshooting Guide

### Issue: Backend won't start
```powershell
# Check MongoDB connection
mongosh

# Verify .env file
Get-Content .env

# Check Python environment
.\.venv\Scripts\Activate.ps1
python --version

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: Frontend connection errors
```powershell
# Verify backend is running
curl http://localhost:8000/health

# Check CORS in .env
Get-Content .env | Select-String "CORS"

# Clear browser cache
# Try incognito mode
```

### Issue: CLI import errors
```powershell
# Verify you're in project root
Get-Location
# Should be: C:\Users\harsh\final-proj

# Use module syntax
python -m backend.cli --help

# Check virtual environment
.\.venv\Scripts\Activate.ps1
```

### Issue: MongoDB connection failed
```powershell
# Check if MongoDB is running
docker ps | Select-String "mongo"
# OR
Get-Service MongoDB

# Test direct connection
mongosh mongodb://localhost:27017

# Check .env MONGODB_URL
Get-Content .env | Select-String "MONGODB_URL"
```

---

## 📚 Quick Reference

### Essential Commands

```powershell
# Start MongoDB (Docker)
docker run -d -p 27017:27017 --name qgenome-mongo mongo

# Start Backend
.\.venv\Scripts\Activate.ps1
python -m backend.main

# Start Frontend
cd frontend
npm run dev

# CLI Help
python -m backend.cli --help
python -m backend.cli dataset --help
python -m backend.cli job --help

# MongoDB Shell
mongosh
use qgenome
db.datasets.find().pretty()
db.processing_jobs.find().pretty()
exit
```

### Important URLs
- Frontend: http://localhost:3000/
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- ReDoc: http://localhost:8000/redoc

### Important Files
- Configuration: `.env`
- Backend Main: `backend/main.py`
- CLI Tool: `backend/cli.py`
- Frontend: `frontend/index.html`

---

## ✅ Completion

Once all checkboxes are marked:

1. ✅ System is fully operational
2. ✅ All components working together
3. ✅ Data flows: Frontend → API → MongoDB
4. ✅ CLI can access all data
5. ✅ Processing steps are visible
6. ✅ Ready for demonstration

---

## 🎉 Success!

Your QGENOME system is now:
- ✅ Connected to MongoDB
- ✅ Running backend API
- ✅ Serving frontend UI
- ✅ CLI operational
- ✅ Fully integrated
- ✅ Production ready

**You're ready to process quantum genomics data!**

---

*Print this checklist and check off items as you complete them*
*Keep this handy for future startups*
