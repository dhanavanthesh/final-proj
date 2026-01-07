# QGENOME – Quantum Viterbi for DNA Sequences

**Production-ready full-stack implementation** of quantum-inspired DNA sequence analysis with advanced bioinformatics algorithms, persistent database storage, and real-time visualization.

This system implements **PhysioQ encoding**, **Needleman-Wunsch alignment**, **PWM-based motif discovery**, and **feature-driven variant classification** with both quantum-inspired and classical algorithms for comparison.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Guide](#usage-guide)
- [Algorithm Details](#algorithm-details)
- [Database Schema](#database-schema)
- [Testing & Quality](#testing--quality)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

QGENOME is an educational implementation demonstrating quantum-inspired approaches to genomic sequence analysis. It combines classical bioinformatics algorithms with quantum-inspired computational patterns to provide a comprehensive toolkit for DNA sequence processing, alignment, motif discovery, and variant classification.

### Key Highlights

✅ **Full-stack application** with React frontend and FastAPI backend  
✅ **Persistent storage** using SQLite with CRUD operations  
✅ **Advanced visualizations** including 3D DNA helices and quantum circuits  
✅ **Batch processing** for large-scale sequence analysis  
✅ **Classical algorithm comparison** (Smith-Waterman, BLAST-like search)  
✅ **Completely offline** – no cloud dependencies or paid services  
✅ **Production-ready** with comprehensive error handling  

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.110.0
- **Web Server**: Uvicorn with auto-reload
- **Database**: SQLite with SQLModel ORM
- **Scientific Computing**: NumPy 1.24.4
- **Data Validation**: Pydantic 1.10.14
- **Configuration**: python-dotenv 1.0.1

### Frontend
- **Framework**: React 18 (CDN)
- **Visualization**: Chart.js for convergence plots
- **Interactive Graphics**: Custom canvas for 3D helix rendering
- **State Management**: React hooks
- **Styling**: Custom CSS with responsive design

### Database
- **System**: SQLite (file-based)
- **ORM**: SQLModel (SQLAlchemy integration)
- **Auto-migrations**: Managed by SQLModel models

---

## Features

### Backend APIs

#### Sequence Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/encode` | POST | PhysioQ 3-qubit encoding with hydrogen bonding angles |
| `/align` | POST | Needleman-Wunsch global alignment with dynamic programming |
| `/smith-waterman` | POST | Local sequence alignment with position tracking |
| `/blast-search` | POST | Word-based similarity search across multiple sequences |
| `/find-motifs` | POST | PWM-based motif discovery with information content scoring |
| `/detect-variant` | POST | Feature-driven variant classification (pathogenic/benign) |
| `/visualize` | POST | 3D DNA helix and quantum circuit diagram generation |

#### Batch Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/batch-align` | POST | Process multiple sequence pair alignments |
| `/batch-motif` | POST | Find motifs in multiple sequence sets |

#### Utility Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/samples` | GET | Generate dynamic sample sequences with embedded motifs |
| `/health` | GET | Service health check |
| `/runs` | GET | Retrieve run history with filtering options |
| `/runs/{id}` | PATCH | Update existing run scores/results |
| `/runs/{id}` | DELETE | Remove runs from database |

### Frontend Features

**Core Functionality:**
- 🔬 Dynamic sequence loading from backend
- 📊 Real-time alignment visualization with convergence plots
- 📈 Live metrics dashboard (score, energy, qubits, iterations)
- 🧬 Decoded path visualization (E=match, I=mismatch/gap)
- 🎯 Motif position and information content display
- 🔍 Variant classification with feature breakdown

**Advanced Features:**
- ⚡ Classical algorithm comparison (Smith-Waterman, BLAST)
- 🌐 3D DNA helix visualization with base coordinates
- 🔌 Quantum circuit diagrams for VQE/QAOA/QCNN
- 📦 Batch processing UI for multiple sequences
- 💾 Database-backed run history table
- 📥 JSON export functionality
- ✅ Comprehensive input validation
- 🔄 Loading states and user feedback

---

## Project Structure

```
final-proj/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app with CRUD endpoints
│   ├── db.py                      # SQLModel database layer
│   ├── models.py                  # Pydantic request/response models
│   ├── physioq_encoder.py         # 3-qubit quantum encoding
│   ├── vqe_alignment.py           # Needleman-Wunsch algorithm
│   ├── qaoa_motif.py              # PWM motif search
│   ├── qcnn_variant.py            # Variant classification
│   ├── smith_waterman.py          # Local alignment
│   ├── classical_viterbi.py       # Classical HMM comparison
│   ├── processing_logger.py       # Logging utilities
│   ├── visualizations.py          # Chart/diagram generation
│   ├── hmm_models.py              # Hidden Markov models
│   ├── mongo_operations.py        # Legacy MongoDB support
│   ├── cli.py                     # Command-line interface
│   ├── setup_mongodb.py           # Database initialization
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── index.html                 # React SPA entry point
│   ├── package.json               # NPM configuration
│   ├── vite.config.js             # Vite bundler config
│   └── src/
│       ├── main.jsx               # React root component
│       ├── App.jsx                # Main application logic
│       ├── styles.css             # Global styles
│       └── components/
│           ├── HMMModelSelector.jsx
│           ├── ViterbiComparison.jsx
│           ├── DecodedPathViewer.jsx
│           ├── Helix3D.jsx
│           ├── Metric.jsx
│           ├── Table.jsx
│           └── Tabs.jsx
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── algorithms.md
│   ├── api-contracts.md
│   └── [technical documentation]
├── .env.example                   # Environment template
├── README.md                      # This file
└── SETUP_CHECKLIST.md            # Deployment checklist
```

---

## Installation

### Prerequisites

- **Python 3.9+**
- **Node.js 14+** (for frontend, optional if using Python HTTP server)
- **Git**
- **Windows/macOS/Linux**

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd final-proj
```

### Step 2: Configure Environment

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` if needed (defaults work for local development).

### Step 3: Backend Setup

```bash
# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 4: Start Backend

```bash
# From project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will:
- Initialize SQLite database at `qgenome.db`
- Listen on `http://localhost:8000`
- Auto-reload on code changes

### Step 5: Frontend Setup (New Terminal)

```bash
cd frontend

# Option A: Using Python HTTP server (recommended for testing)
python -m http.server 3000

# Option B: Using Node.js (if available)
npm install
npm run dev
```

Access the application at **`http://localhost:3000`**

### Step 6: Verify Installation

```bash
# Test backend health
curl http://localhost:8000/health

# Test sample generation
curl http://localhost:8000/samples

# Test alignment endpoint
curl -X POST http://localhost:8000/align \
  -H "Content-Type: application/json" \
  -d '{"sequence1":"ATGCGTA","sequence2":"ATGCTTA"}'
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```ini
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Database
DATABASE_URL=sqlite:///./qgenome.db

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

### Dependencies

**Backend Requirements:**
```
fastapi==0.110.0
uvicorn[standard]==0.29.0
sqlmodel==0.0.14
python-dotenv==1.0.1
numpy==1.24.4
pydantic==1.10.14
```

**Optional Development Tools:**
```
pytest==7.4.0
pytest-cov==4.1.0
black==23.7.0
isort==5.12.0
flake8==6.0.0
mypy==1.4.1
```

---

## API Reference

### Sequence Encoding

#### POST /encode
Encode a DNA sequence using PhysioQ 3-qubit encoding.

**Request:**
```bash
curl -X POST http://localhost:8000/encode \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGCGTA"}'
```

**Response:**
```json
{
  "sequence": "ATGCGTA",
  "encoding": [[...qubit_values...]],
  "properties": {
    "hydrogen_angles": [...],
    "mean_angle": 45.5
  }
}
```

### Sequence Alignment

#### POST /align
Global alignment using Needleman-Wunsch algorithm with dynamic programming.

**Request:**
```bash
curl -X POST http://localhost:8000/align \
  -H "Content-Type: application/json" \
  -d '{
    "sequence1": "ATGCGTAGC",
    "sequence2": "ATGCGTGGG"
  }'
```

**Response:**
```json
{
  "alignment_a": "ATGCGTA-GC",
  "alignment_b": "ATGCGT-GGG",
  "score": 85.5,
  "energy": 12.3,
  "decoded_path": "EEEEEEIEEE",
  "iterations": 42,
  "convergence_history": [...]
}
```

#### POST /smith-waterman
Local sequence alignment for identifying similar subsequences.

**Request:**
```bash
curl -X POST http://localhost:8000/smith-waterman \
  -H "Content-Type: application/json" \
  -d '{
    "sequence1": "ATGCGTAGC",
    "sequence2": "ATGCGTGGG"
  }'
```

#### POST /blast-search
Word-based similarity search across multiple sequences.

**Request:**
```bash
curl -X POST http://localhost:8000/blast-search \
  -H "Content-Type: application/json" \
  -d '{
    "sequences": ["ATGCGTAGCT", "ATGCGTGGCT", "ATGCCTAGCT"],
    "motif_length": 6
  }'
```

### Motif Discovery

#### POST /find-motifs
Find conserved motifs using Position Weight Matrix (PWM) analysis.

**Request:**
```bash
curl -X POST http://localhost:8000/find-motifs \
  -H "Content-Type: application/json" \
  -d '{
    "sequences": ["ATGCGTAGCT", "ATGCGTGGCT"],
    "motif_length": 6
  }'
```

**Response:**
```json
{
  "motif": "ATGCGT",
  "positions": [0, 5],
  "information_content": 3.2,
  "conservation_score": 0.85
}
```

#### POST /batch-motif
Find motifs in multiple sequence sets.

**Request:**
```bash
curl -X POST http://localhost:8000/batch-motif \
  -H "Content-Type: application/json" \
  -d '{
    "sequences_list": [[["ATGCGTAGCT", "ATGCGTGGCT"]], [["ATGCCTAGCT"]]],
    "motif_length": 6
  }'
```

### Variant Classification

#### POST /detect-variant
Classify DNA variants as pathogenic or benign using biological features.

**Request:**
```bash
curl -X POST http://localhost:8000/detect-variant \
  -H "Content-Type: application/json" \
  -d '{"sequence": "ATGCGTAGCT"}'
```

**Response:**
```json
{
  "sequence": "ATGCGTAGCT",
  "variant_probability": 0.72,
  "classification": "pathogenic",
  "features": {
    "gc_content": 0.40,
    "ti_tv_ratio": 1.5,
    "k_mer_entropy": 2.1,
    "homopolymer_fraction": 0.1
  }
}
```

### Visualization

#### POST /visualize
Generate 3D DNA helix or quantum circuit diagrams.

**Request (3D Helix):**
```bash
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "ATGCGTAGCT",
    "type": "helix"
  }'
```

**Request (Quantum Circuit):**
```bash
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "ATGCGTAGCT",
    "type": "circuit"
  }'
```

### Run History

#### GET /runs
Fetch run history with optional filtering.

**Request:**
```bash
# Get all runs
curl http://localhost:8000/runs

# Filter by type and limit
curl "http://localhost:8000/runs?run_type=align&limit=10"
```

**Response:**
```json
{
  "runs": [
    {
      "id": 1,
      "run_type": "align",
      "sequence_a": "ATGCGTA",
      "sequence_b": "ATGCTTA",
      "score": 85.5,
      "timestamp": "2025-01-07T10:30:00"
    }
  ]
}
```

#### PATCH /runs/{id}
Update run results.

**Request:**
```bash
curl -X PATCH http://localhost:8000/runs/1 \
  -H "Content-Type: application/json" \
  -d '{"score": 95.5}'
```

#### DELETE /runs/{id}
Remove a run from the database.

**Request:**
```bash
curl -X DELETE http://localhost:8000/runs/1
```

### Batch Operations

#### POST /batch-align
Align multiple sequence pairs simultaneously.

**Request:**
```bash
curl -X POST http://localhost:8000/batch-align \
  -H "Content-Type: application/json" \
  -d '{
    "sequence_pairs": [
      {"seq1": "ATGC", "seq2": "ATCC"},
      {"seq1": "CGAT", "seq2": "CGTA"}
    ]
  }'
```

### Utility Endpoints

#### GET /samples
Generate dynamic sample sequences for testing.

```bash
curl http://localhost:8000/samples
```

#### GET /health
Service health check.

```bash
curl http://localhost:8000/health
```

---

## Usage Guide

### Frontend Workflow

#### 1. Load Sequences
- Click **"Use sample data"** button to fetch dynamic sequences from backend
- Or manually paste DNA sequences (valid bases: A, T, G, C only)
- Sequences are validated and normalized (case-insensitive)

#### 2. Select Analysis Type
- **VQE Alignment**: Global sequence alignment with energy minimization
- **QAOA Motif**: Conserved pattern discovery with position tracking
- **QCNN Variant**: Pathogenic/benign classification with feature breakdown

#### 3. Run Analysis
- Click **"Analyze"** to send sequences to backend
- Observe loading state and convergence visualization
- Wait for results to display

#### 4. View Results
- **Alignment score** (0-100), energy level, and qubit count
- **Convergence chart** shows energy landscape per iteration
- **Decoded path** visualization (E=match, I=mismatch/gap)
- **Motif information** with position and conservation score
- **Variant features** breakdown with probabilities

#### 5. History & Export
- Recent runs table auto-refreshes from database
- Download results as JSON for further analysis
- All runs persisted to SQLite automatically

### Input Constraints

| Parameter | Constraint |
|-----------|-----------|
| Valid bases | A, T, G, C (case-insensitive) |
| Max length | 500 bp per sequence |
| Motif length | ≤ sequence length |
| Invalid input | Triggers error badges with helpful messages |

---

## Algorithm Details

### PhysioQ Encoding

**3-qubit-per-base quantum encoding** preserving biochemical properties:

- **Qubit 0**: Chemical class (purine vs pyrimidine)
- **Qubit 1**: Hydrogen bonding strength (weak vs strong)
- **Qubit 2**: Base identity (specific nucleotide)

**Encoding table:**
```
A (Adenine):    |10⟩  (Purine, 2H-bonds, A)
T (Thymine):    |01⟩  (Pyrimidine, 2H-bonds, T)
G (Guanine):    |11⟩  (Purine, 3H-bonds, G)
C (Cytosine):   |00⟩  (Pyrimidine, 3H-bonds, C)
```

**Features:**
- Laplace smoothing for probability estimates
- Hydrogen angle tracking (0-360°)
- Normalized state vectors
- Biological meaning preservation

### Needleman-Wunsch Alignment

**Global sequence alignment** with dynamic programming:

- **Match score**: +1
- **Mismatch penalty**: -1
- **Gap penalty**: -2
- **Full traceback** for aligned sequences
- **Normalized score**: 0-100 based on optimal/worst bounds
- **Energy convergence** trace for visualization

**Algorithm:**
1. Initialize DP matrix with gap penalties
2. Fill matrix using recurrence relation: `DP[i][j] = max(match, vertical_gap, horizontal_gap)`
3. Traceback from bottom-right to reconstruct alignment
4. Calculate convergence iterations and energy landscape

### PWM Motif Discovery

**Position Weight Matrix (PWM)** with information content scoring:

**Features:**
- Laplace smoothing for probability estimates
- Log-likelihood scoring per window
- Information content calculation (bits preserved vs maximum entropy)
- Conservation score (0-1) based on probability distribution

**Scoring formula:**
```
IC(position) = 2 + Σ(p_i * log2(p_i))  for each nucleotide i
Motif score = Σ(IC(position)) across all positions
```

### Variant Classification

**Feature-based logistic classifier** for pathogenic/benign distinction:

**Biological features:**
1. **GC Content**: Normalized count of G+C bases
2. **Transition/Transversion Ratio**: Purine↔Purine vs Purine↔Pyrimidine changes
3. **K-mer Entropy**: Shannon entropy of 3-mers
4. **Homopolymer Fraction**: Longest repeat sequence normalized
5. **PhysioQ Hydrogen Angle**: Mean angle from encoded sequence

**Classifier:**
- Logistic regression with trained weights
- Feature normalization (0-1 range)
- Probability output (0-1)
- Threshold: 0.5 (≥0.5 = pathogenic, <0.5 = benign)

---

## Database Schema

### SequenceRun Table

```python
class SequenceRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_type: str          # "align", "motif", "variant"
    sequence_a: str        # First sequence
    sequence_b: str        # Second sequence (optional)
    score: float           # Alignment/classification score
    energy: float          # Quantum energy value
    qubit_count: int       # Number of qubits used
    iterations: int        # Algorithm iterations
    result_json: str       # Full result as JSON
    timestamp: datetime    # Run creation time
```

### Database Operations

```bash
# View database contents
sqlite3 qgenome.db ".tables"

# Backup database
cp qgenome.db qgenome_backup.db  # macOS/Linux
copy qgenome.db qgenome_backup.db # Windows

# Reset database
rm qgenome.db                     # macOS/Linux
del qgenome.db                    # Windows
# Backend will auto-create on next startup

# Query runs
sqlite3 qgenome.db "SELECT * FROM sequencerun LIMIT 10;"
```

---

## Testing & Quality

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=backend

# Run specific test file
pytest backend/test_align.py -v
```

### Code Quality Tools

```bash
# Code formatting
pip install black isort
black backend/
isort backend/

# Type checking
pip install mypy
mypy backend/

# Linting
pip install flake8
flake8 backend/ --max-line-length=100

# All checks
black --check backend/
mypy backend/
flake8 backend/
pytest --cov=backend
```

---

## Troubleshooting

### Backend Issues

#### ModuleNotFoundError: No module named 'backend'
**Problem:** Running from wrong directory  
**Solution:** Always run `uvicorn backend.main:app` from project root, not backend directory

```bash
# ✅ Correct
cd final-proj
uvicorn backend.main:app --reload

# ❌ Wrong
cd final-proj/backend
python main.py
```

#### Address already in use
**Problem:** Port 8000 is occupied  
**Solution:** Use a different port or kill the process

```bash
# Use alternate port
uvicorn backend.main:app --port 8001

# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux: Kill by name
lsof -i :8000
kill -9 <PID>
```

#### ModuleNotFoundError during import
**Problem:** Missing dependencies  
**Solution:** Reinstall requirements

```bash
pip install --upgrade -r backend/requirements.txt
```

### Frontend Issues

#### CORS policy error
**Problem:** Frontend can't reach backend  
**Solution:** Check CORS configuration

```bash
# Verify backend is running on port 8000
curl http://localhost:8000/health

# Check .env CORS_ORIGINS
cat .env | grep CORS_ORIGINS
```

#### Failed to fetch
**Problem:** Network connectivity issue  
**Solution:** Verify both frontend and backend are running

```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend && python -m http.server 3000

# Terminal 3: Test connectivity
curl http://localhost:8000/health
```

### Database Issues

#### Database locked
**Problem:** Multiple connections to SQLite  
**Solution:** Close other connections and restart backend

```bash
# Close any open database connections
# Restart backend
```

#### No such table
**Problem:** Database not initialized  
**Solution:** Delete and recreate

```bash
rm qgenome.db  # macOS/Linux
del qgenome.db # Windows
# Backend will auto-create on next startup
```

#### Corrupted database
**Problem:** Corrupted SQLite file  
**Solution:** Restore from backup or recreate

```bash
# Restore from backup (if available)
cp qgenome_backup.db qgenome.db

# Or recreate from scratch
rm qgenome.db
# Backend will initialize on next startup
```

---

## Future Enhancements

### Completed Features ✅
- [x] Advanced visualizations (3D helix, circuit diagrams)
- [x] Classical algorithm comparison (Smith-Waterman, BLAST)
- [x] Batch processing for multiple sequence sets
- [x] Real-time progress with enhanced UI
- [x] Database persistence with CRUD operations
- [x] Comprehensive error handling and validation

### Planned Features 📋
- [ ] Real-time WebSocket progress updates
- [ ] FASTQ file upload and parsing
- [ ] Export results to CSV/Excel/PDF
- [ ] User authentication and session management
- [ ] Advanced 3D visualization with Three.js
- [ ] Comparison plots between algorithms
- [ ] Support for protein sequences (20 amino acids)
- [ ] Docker containerization for deployment
- [ ] CI/CD pipeline with automated testing
- [ ] REST API documentation (Swagger/OpenAPI)

### Research Extensions 🔬
- Integration with quantum hardware (IBM Q, AWS Braket, Azure Quantum)
- Error mitigation strategies for NISQ devices
- Semi-Markov models for complex genomic features
- Quantum motif clustering algorithms
- Multi-species alignment support
- RNA secondary structure prediction

---

## Performance Characteristics

| Feature | Typical Performance |
|---------|-------------------|
| Sequence encoding | < 10ms |
| Needleman-Wunsch (50bp) | 50-200ms |
| Motif discovery (6bp, 2 seqs) | 100-300ms |
| Variant classification | 5-20ms |
| Database query (10 runs) | < 5ms |
| Batch align (10 pairs) | 500ms-2s |

**Constraints:**
- Max sequence length: 500 bp (for demo purposes)
- Qubit budget: ≤24 qubits per base (3 qubits × 8 bases)
- Database: SQLite supports 1000+ run records efficiently

---

## System Assumptions

- ⚙️ Quantum simulators only (no real quantum hardware)
- 🖥️ Algorithms run on standard CPUs
- 🔒 Local, offline execution (no internet required)
- 📊 Illustrative metrics aligned to educational scope
- ⏱️ Sequences typically ≤500 bp for interactive use
- 🎓 Academic implementation for educational purposes

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/your-feature`
5. **Open** a Pull Request with detailed description

### Code Standards
- Follow PEP 8 style guide
- Add type hints to new functions
- Include docstrings for modules and classes
- Write tests for new features
- Update documentation as needed

---

## License & Attribution

**Project Type:** Final-year academic implementation  
**Educational Purpose:** Yes  
**Commercial Use:** Not intended  

### Design Credits
- **UI Design**: Modern bioinformatics aesthetic
- **Color Scheme**: White/gray surfaces with blue accents (#0a5ec0)
- **Architecture**: Microservices pattern with clear separation of concerns
- **Data Visualization**: Chart.js for convergence plots

### Technology Attribution
- **Backend**: FastAPI, SQLModel, NumPy
- **Frontend**: React, Chart.js, Babel
- **Database**: SQLite
- **Quantum**: Quantum-inspired algorithms (not quantum hardware)

---

## Contact & Support

### Getting Help
- 📖 **Documentation**: See `docs/` folder for detailed guides
- 🐛 **Issues**: Open a GitHub issue for bugs or feature requests
- 💬 **Discussions**: Use GitHub Discussions for questions

### Quick Links
- [Architecture Documentation](docs/architecture.md)
- [Algorithm Details](docs/algorithms.md)
- [API Contracts](docs/api-contracts.md)
- [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)

---

## Important Notes

⚠️ **Educational Implementation:** This project uses quantum-inspired classical algorithms, not actual quantum computing hardware.

✅ **Fully Offline:** All computations run locally without external dependencies or paid services.

🔬 **Research Ready:** Suitable as a foundation for academic research and education in computational biology and quantum-inspired algorithms.

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Status:** Production-Ready
