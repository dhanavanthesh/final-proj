# Quick Start Guide - QGENOME with MongoDB

## Prerequisites

1. **Python 3.9+** with virtual environment
2. **Node.js 16+** for frontend
3. **MongoDB** (local or cloud)

## Setup Steps

### 1. MongoDB Setup

#### Option A: Local MongoDB
```powershell
# Download and install MongoDB from https://www.mongodb.com/try/download/community
# Or use Docker:
docker run -d -p 27017:27017 --name qgenome-mongo mongo
```

#### Option B: MongoDB Atlas (Cloud)
1. Create free account at https://www.mongodb.com/atlas
2. Create a cluster
3. Get connection string
4. Update `.env` file with connection string

### 2. Environment Configuration

Create `.env` file in project root:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=qgenome
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Install Backend Dependencies

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt
```

### 4. Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

## Running the Application

### Start Backend (Terminal 1)

```powershell
# From project root
.\.venv\Scripts\Activate.ps1
python -m backend.main
```

You should see:
```
Connected to MongoDB at mongodb://localhost:27017, database: qgenome
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Start Frontend (Terminal 2)

```powershell
cd frontend
npm run dev
```

You should see:
```
VITE v5.4.21 ready in 1736 ms
➜  Local:   http://localhost:3000/
```

### Using the CLI (Terminal 3)

```powershell
# From project root
.\.venv\Scripts\Activate.ps1

# List datasets
python -m backend.cli dataset list

# Create a test dataset
python -m backend.cli dataset create --name "Test" --sequences ATGCGTACG CGTAGCTA

# Create a processing job
python -m backend.cli job create --name "Test Job" --algorithm vqe_alignment --sequences ATGCGTACG CGTAGCTA

# View job details
python -m backend.cli job list
```

## Workflow Examples

### Example 1: Frontend → MongoDB → CLI

1. **Open frontend**: http://localhost:3000/
2. **Enter sequences** in the web interface
3. **Click "Run Alignment"** (or any other algorithm)
4. **Data is saved to MongoDB** with full processing details
5. **Check in CLI**:
   ```powershell
   python -m backend.cli job list
   python -m backend.cli job get <job_id>
   ```
6. **View processing steps** including timing and details

### Example 2: CLI → MongoDB → Frontend

1. **Create dataset via CLI**:
   ```powershell
   python -m backend.cli dataset create \
     --name "My Genes" \
     --sequences ATGCGTACGATCG CGTAGCTAGCTA \
     --description "Sample gene sequences"
   ```

2. **Access via API**:
   ```powershell
   curl http://localhost:8000/datasets
   ```

3. **View in MongoDB** (using mongosh or MongoDB Compass)

### Example 3: FASTA Import → Process → Analyze

1. **Create FASTA file** `data.fasta`:
   ```
   >Gene1
   ATGCGTACGATCGATCG
   >Gene2
   CGTAGCTAGCTAGCTA
   >Gene3
   TGCAGTCAGTCAGTCA
   ```

2. **Import via CLI**:
   ```powershell
   python -m backend.cli dataset import data.fasta --name "Imported Genes"
   ```

3. **Create processing job**:
   ```powershell
   python -m backend.cli job create \
     --name "Batch Alignment" \
     --algorithm vqe_alignment \
     --sequences ATGCGTACGATCGATCG CGTAGCTAGCTAGCTA
   ```

4. **Monitor progress**:
   ```powershell
   python -m backend.cli job get <job_id>
   ```

## Verify MongoDB Storage

### Using mongosh

```powershell
mongosh

use qgenome

# View datasets
db.datasets.find().pretty()

# View processing jobs
db.processing_jobs.find().pretty()

# View sequence runs
db.sequence_runs.find().pretty()
```

### Using MongoDB Compass

1. Download: https://www.mongodb.com/try/download/compass
2. Connect to: `mongodb://localhost:27017`
3. Browse database: `qgenome`
4. View collections:
   - `datasets` - Your DNA datasets
   - `processing_jobs` - Jobs with processing steps
   - `sequence_runs` - Legacy run data

## API Documentation

Access interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### New Endpoints

#### Datasets
- `POST /datasets` - Create dataset
- `GET /datasets` - List datasets
- `GET /datasets/{id}` - Get dataset details
- `DELETE /datasets/{id}` - Delete dataset

#### Processing Jobs
- `POST /jobs` - Create job
- `GET /jobs` - List jobs (with filters)
- `GET /jobs/{id}` - Get job details with processing steps

## Processing Visibility

Every processing job now includes:

```json
{
  "job_id": "64abc123...",
  "processing_summary": {
    "total_steps": 4,
    "total_duration_ms": 1234.56,
    "steps": [
      {
        "step_name": "Input Validation",
        "duration_ms": 12.34,
        "status": "completed",
        "details": {"seq1_length": 15, "seq2_length": 15}
      },
      {
        "step_name": "VQE Circuit Construction",
        "duration_ms": 856.78,
        "status": "completed",
        "details": {"alignment_score": 0.85}
      },
      {
        "step_name": "Database Storage",
        "duration_ms": 345.12,
        "status": "completed",
        "details": {}
      }
    ]
  }
}
```

## Troubleshooting

### Backend won't start
```powershell
# Check if virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Check if MongoDB is running
mongosh
# or
docker ps | grep mongo

# Check environment variables
Get-Content .env
```

### Frontend won't connect to backend
```powershell
# Verify backend is running on port 8000
# Check CORS settings in .env
# Ensure frontend is on port 3000
```

### CLI import errors
```powershell
# Always run from project root
cd c:\Users\harsh\final-proj

# Use module syntax
python -m backend.cli --help
```

### MongoDB connection issues
```powershell
# Test connection
mongosh mongodb://localhost:27017

# Check MongoDB logs
# Windows: C:\Program Files\MongoDB\Server\{version}\log\mongod.log
# Docker: docker logs qgenome-mongo
```

## Next Steps

1. ✅ Start MongoDB
2. ✅ Configure `.env` file
3. ✅ Install dependencies
4. ✅ Run backend: `python -m backend.main`
5. ✅ Run frontend: `npm run dev`
6. ✅ Open http://localhost:3000/
7. ✅ Try CLI: `python -m backend.cli dataset list`
8. ✅ Submit sequences via frontend
9. ✅ View processing details in CLI
10. ✅ Check MongoDB data

## Demo Commands

```powershell
# Terminal 1 - Backend
.\.venv\Scripts\Activate.ps1
python -m backend.main

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - CLI Demo
.\.venv\Scripts\Activate.ps1

# Create dataset
python -m backend.cli dataset create --name "Demo Dataset" --sequences ATGCGTACGATCGATCG CGTAGCTAGCTAGCTA --description "Demo sequences for presentation"

# List datasets
python -m backend.cli dataset list

# Create processing job
python -m backend.cli job create --name "Demo Alignment" --algorithm vqe_alignment --sequences ATGCGTACGATCGATCG CGTAGCTAGCTAGCTA

# Check job status
python -m backend.cli job list

# Get detailed results
python -m backend.cli job get <job_id_from_above>
```

## Architecture

```
Frontend (React)
    ↓ HTTP Requests
Backend API (FastAPI)
    ↓ Async Operations
MongoDB Database
    ↑ Direct Access
CLI Tool (Python)
```

All components share the same MongoDB database, enabling:
- Real-time data synchronization
- Full processing traceability
- Multiple access methods (Web, API, CLI)
- NoSQL flexibility for complex data structures
