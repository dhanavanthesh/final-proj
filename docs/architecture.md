# 🏗️ System Architecture

QGENOME follows a **layered monolith architecture** with clear separation of concerns across UI, API, services, and database layers.

---

## Architecture Style

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                  PRESENTATION LAYER (React SPA)                      ║
║              Components, State Management, Charts & Viz              ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
                              │
                     HTTP/JSON │ JSON Response
                              │
┌──────────────────────────────▼──────────────────────────────────┐
│                                                                  │
│            API LAYER (FastAPI + Pydantic)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Routes: /align, /motif, /variant, /health, /runs      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Input Validation, Error Handling, CORS                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                        Orchestrate
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼────────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │  ALIGNMENT     │  │  MOTIF      │  │  VARIANT    │
    │  SERVICE       │  │  SERVICE    │  │  SERVICE    │
    │  ┌───────────┐ │  │ ┌─────────┐ │  │ ┌────────┐  │
    │  │Needleman- │ │  │ │ PWM     │ │  │ │Feature │  │
    │  │ Wunsch    │ │  │ │ Scoring │ │  │ │Extract │  │
    │  ├───────────┤ │  │ ├─────────┤ │  │ ├────────┤  │
    │  │Smith-     │ │  │ │Info     │ │  │ │Risk    │  │
    │  │ Waterman  │ │  │ │Content  │ │  │ │Score   │  │
    │  └───────────┘ │  │ └─────────┘ │  │ └────────┘  │
    └───────┬────────┘  └──────┬──────┘  └──────┬──────┘
            │                  │                │
            └──────────────────┼────────────────┘
                               │
                        HMM SERVICE
                  ┌─────────────┬──────────────┐
                  │             │              │
          ┌───────▼────┐   ┌────▼────┐   ┌───▼──────┐
          │ Classical  │   │ Quantum-│   │Encoding &│
          │ Viterbi    │   │ Inspired│   │PhysioQ   │
          │(hmmlearn)  │   │ Viterbi │   │          │
          └───────┬────┘   └────┬────┘   └───┬──────┘
                  │             │            │
                  └─────────────┼────────────┘
                                │
                         Persist Results
                                │
                    ┌───────────▼────────────┐
                    │                        │
                    │  DATABASE LAYER        │
                    │  ┌──────────────────┐  │
                    │  │  SQLite/MongoDB  │  │
                    │  │  - sequence_runs │  │
                    │  │  - datasets      │  │
                    │  │  - jobs          │  │
                    │  └──────────────────┘  │
                    │                        │
                    └────────────────────────┘
```

---

## Component Responsibilities

| Component | Responsibility | Key Files |
|-----------|-----------------|-----------|
| **React UI** | User interaction, rendering, visualization | `frontend/src/App.jsx`, `components/*` |
| **FastAPI Routes** | HTTP request handling, routing, CORS | `backend/main.py` |
| **Input Validation** | Schema validation, constraint checking | `backend/models.py` |
| **Alignment Service** | Global/local sequence alignment | `backend/vqe_alignment.py`, `backend/smith_waterman.py` |
| **Motif Service** | Pattern discovery, PWM scoring | `backend/qaoa_motif.py` |
| **Variant Service** | Feature extraction, risk classification | `backend/qcnn_variant.py` |
| **HMM Service** | Hidden Markov Model decoding | `backend/classical_viterbi.py`, `backend/qva_viterbi.py` |
| **Database** | Persistence layer, CRUD operations | `backend/db.py`, `backend/mongo_operations.py` |

---

## Folder Structure & Explanations

```
final-proj/
│
├── backend/
│   ├── main.py                 # Entry point, FastAPI app, route definitions
│   ├── models.py               # Pydantic request/response models
│   ├── db.py                   # Database connection & CRUD operations
│   │
│   ├── vqe_alignment.py        # Global alignment (Needleman-Wunsch variant)
│   ├── smith_waterman.py       # Local alignment + BLAST-like search
│   ├── qaoa_motif.py           # PWM motif discovery with IC scoring
│   ├── qcnn_variant.py         # Feature-based variant classification
│   │
│   ├── hmm_models.py           # HMM configurations and state mappings
│   ├── classical_viterbi.py    # Classical HMM Viterbi (hmmlearn)
│   ├── qva_viterbi.py          # Quantum-inspired Viterbi (Qiskit Aer)
│   │
│   ├── physioq_encoder.py      # Nucleotide to qubit/angle encoding
│   ├── visualizations.py       # Chart & diagram data generation
│   ├── processing_logger.py    # Job execution logging
│   ├── mongo_operations.py     # MongoDB dataset/job CRUD
│   │
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── index.html              # HTML entry point
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── styles.css          # Global styling
│   │   └── components/         # UI building blocks
│   │       ├── Tabs.jsx
│   │       ├── Metric.jsx
│   │       ├── Table.jsx
│   │       ├── HMMModelSelector.jsx
│   │       ├── ViterbiComparison.jsx
│   │       ├── DecodedPathViewer.jsx
│   │       └── Helix3D.jsx
│   │
│   ├── package.json            # NPM dependencies
│   └── vite.config.js          # Vite bundler config
│
├── docs/                       # Technical documentation
├── .env.example                # Environment template
└── README.md                   # Main project README
```

---

## Entry Point & Execution Flow

### Backend Startup

```
┌─────────────────────────────────────────────────┐
│ START: uvicorn backend.main:app                │
└─────────────────────────────┬───────────────────┘
                              │
                    ┌─────────▼────────────┐
                    │ Load Environment     │
                    │ (python-dotenv)      │
                    └─────────────────────┘
                              │
                    ┌─────────▼─────────────┐
                    │ Connect to Database   │
                    │ (SQLModel/Motor)      │
                    └─────────────────────┘
                              │
                    ┌─────────▼──────────────┐
                    │ Server Running        │
                    │ 0.0.0.0:8000         │
                    └─────────────────────┘
                              │
                    ┌─────────▼──────────────┐
                    │ Accept Requests       │
                    │ HTTP/JSON            │
                    └─────────────────────┘
```

### Request Processing Pipeline

```
STEP 1: RECEIVE                    STEP 2: VALIDATE
┌──────────────────┐               ┌──────────────────┐
│ HTTP Request     │──Parse JSON──▶│ Pydantic Model   │
│ (from browser)   │               │ Validation       │
└──────────────────┘               └──────────────────┘
                                           │
                                           │
STEP 3: AUTHORIZE                   STEP 4: EXECUTE
┌──────────────────┐                ┌──────────────────┐
│ Check            │◀─Check─────────│ Route Handler    │
│ Permissions      │  Constraints   │ Select Algorithm │
└──────────────────┘                └──────────────────┘
         │                                   │
         │                          ┌────────▼────────┐
         └─────────────────────────▶│ Algorithm Exec   │
                                    │ (Compute)        │
                                    └─────────┬────────┘
                                              │
                        ┌─────────────────────┴─────────────────┐
                        │                                       │
                   ┌────▼────┐                          ┌──────▼──────┐
                   │ Format   │                          │ Persist to │
                   │ Response │                          │ Database   │
                   │ (JSON)   │                          │            │
                   └────┬─────┘                          └──────┬──────┘
                        │                                       │
                        └────────────────┬─────────────────────┘
                                         │
                                ┌────────▼────────┐
                                │ HTTP 200        │
                                │ JSON Response   │
                                └─────────────────┘
```

### Frontend Initialization

```
┌─────────────────────────────────┐
│ Load index.html                │
└─────────────────┬───────────────┘
                  │
        ┌─────────▼──────────┐
        │ Parse HTML         │
        │ Load JS/CSS        │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ React App.jsx          │
        │ Initialize             │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Component Tree         │
        │ Create Hierarchy       │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ State Management       │
        │ Initialize Hooks       │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Render UI              │
        │ Show Components        │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Listen to Events       │
        │ (User Input)           │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ User Interaction       │
        │ Click, Type, Select    │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Dispatch API Call      │
        │ fetch(endpoint)        │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Process Response       │
        │ Parse JSON             │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Update State           │
        │ Store Results          │
        └─────────────────┘
                  │
        ┌─────────▼──────────────┐
        │ Render Results         │
        │ Charts, Tables, Viz    │
        └─────────────────┘
```

---

## Component Communication

### Synchronous (HTTP Request-Response)

```
React Component
    ↓ fetch(endpoint, { method: 'POST', body: JSON })
FastAPI Route Handler
    ↓ Validate input
Algorithm Service
    ↓ Compute
Database (Persist)
    ↓ Save result
FastAPI (Serialize)
    ↓ JSON response
React (Render)
```

### Database Integration

- **Query:** `db.get_run(run_id)` → SQLite/MongoDB
- **Insert:** `db.save_run(SequenceRun(...))` → Persist
- **Update:** `db.update_run(run_id, fields)` → Modify
- **Delete:** `db.delete_run(run_id)` → Remove

---

## Layer Responsibilities in Detail

### Presentation Layer (React)
- ✅ Form input capture
- ✅ API request dispatch
- ✅ Response rendering
- ✅ Chart/visualization generation
- ✅ User feedback (loading states, error messages)

### API Layer (FastAPI)
- ✅ Route registration (`POST /align`, `GET /runs`, etc.)
- ✅ Request deserialization
- ✅ Pydantic validation
- ✅ CORS handling
- ✅ Response serialization

### Service Layer (Algorithms)
- ✅ Pure algorithm implementation
- ✅ Input validation (internal)
- ✅ Computation
- ✅ Result formatting

### Data Layer (Database)
- ✅ Connection management
- ✅ CRUD operations
- ✅ Indexing
- ✅ Query optimization

---

## Key Design Patterns

| Pattern | Usage | Location |
|---------|-------|----------|
| **Strategy Pattern** | Algorithm selection (classical vs quantum) | `main.py` (viterbi endpoint) |
| **Factory Pattern** | HMM model creation | `hmm_models.py` |
| **DAO Pattern** | Database operations | `db.py`, `mongo_operations.py` |
| **Repository Pattern** | Data access abstraction | `mongo_operations.py` |
| **Adapter Pattern** | Qiskit Aer integration | `qva_viterbi.py` |

---

## Data Flow Example: Alignment Request

```
USER INTERACTION:
┌──────────────────────────────────────────┐
│ User pastes DNA sequences                │
│ Clicks "Align" button                    │
└──────────────────┬───────────────────────┘
                   │
                   ▼
REACT UI LAYER:
┌──────────────────────────────────────────┐
│ Capture input from form                  │
│ Show loading state                       │
│ Send: POST /align {seq1, seq2}          │
└──────────────────┬───────────────────────┘
                   │
                   ▼
FASTAPI LAYER:
┌──────────────────────────────────────────┐
│ Receive HTTP request                     │
│ Deserialize JSON body                    │
│ Validate Pydantic model                  │
│ ✓ Check ACGT only                        │
│ ✓ Check length ≤ 500bp                   │
└──────────────────┬───────────────────────┘
                   │
                   ▼
ALGORITHM SERVICE:
┌──────────────────────────────────────────┐
│ Call: execute_alignment()                │
│ Run: needleman_wunsch(seq1, seq2)       │
│ Compute:                                 │
│  - DP matrix                             │
│  - Traceback                             │
│  - Score normalization                   │
│ Return: {score, path, energy}           │
└──────────────────┬───────────────────────┘
                   │
                   ▼
DATABASE LAYER:
┌──────────────────────────────────────────┐
│ Create SequenceRun record                │
│ Save to SQLite/MongoDB                   │
│ Store: run_id, sequences, score, result  │
│ Return: run_id                           │
└──────────────────┬───────────────────────┘
                   │
                   ▼
FASTAPI RESPONSE:
┌──────────────────────────────────────────┐
│ Serialize result to JSON                 │
│ Add run_id                               │
│ Return HTTP 200                          │
└──────────────────┬───────────────────────┘
                   │
                   ▼
REACT UI DISPLAY:
┌──────────────────────────────────────────┐
│ Hide loading state                       │
│ Render alignment visualization           │
│ Show convergence chart                   │
│ Display metrics (score, energy)          │
│ Show decoded path (E/I sequence)        │
│ Store run_id for history                 │
└──────────────────────────────────────────┘
```

---

## Scalability Considerations

### Current (Monolith)
- Single FastAPI process
- Local SQLite or MongoDB
- In-memory algorithm execution
- Suitable for development/small scale

### Future (Microservices)
- Separate API service
- Separate algorithm workers
- Message queue (RabbitMQ/Redis)
- Distributed database
- Suitable for production scale

---

## Performance Optimizations

| Optimization | Where Applied | Benefit |
|--------------|--------------|---------|
| **Caching** | Sample sequences, HMM models | Reduced computation |
| **Async I/O** | Database queries | Non-blocking operations |
| **Vectorization** | NumPy operations | CPU efficiency |
| **Early Validation** | API layer | Fail fast |
| **Connection Pooling** | Database | Reuse connections |

---

## Security Architecture

```
SECURITY LAYERS:

┌─────────────────────────────────────────────────┐
│ CLIENT (Browser)                               │
│ - HTTPS/TLS Encryption                         │
└──────────────────┬──────────────────────────────┘
                   │ [Encrypted Connection]
                   ▼
┌─────────────────────────────────────────────────┐
│ NETWORK LAYER                                   │
│ - TLS 1.3 Encryption                           │
│ - Certificate Validation                        │
└──────────────────┬──────────────────────────────┘
                   │ [Encrypted]
                   ▼
┌─────────────────────────────────────────────────┐
│ API GATEWAY (FastAPI)                          │
│ ✓ CORS: Origin Check                          │
│ ✓ Rate Limiting                                │
│ ✓ Request Headers Validation                   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ INPUT VALIDATION LAYER                         │
│ ✓ Pydantic Schema Validation                  │
│ ✓ Type Checking                               │
│ ✓ Constraint Checking (length, format)        │
│ ✓ SQL Injection Prevention                    │
│ ✓ XSS Prevention (output encoding)            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ AUTHORIZATION LAYER                            │
│ ✓ Permission Checks                           │
│ ✓ Role-Based Access Control (Future)          │
│ ✓ Rate Limiting per User (Future)             │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ DATABASE LAYER                                  │
│ ✓ Connection Pooling                          │
│ ✓ Prepared Statements                         │
│ ✓ Access Control Lists                        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ DATA AT REST                                    │
│ - SQLite File Permissions                      │
│ - Database Encryption (Optional)               │
│ - Secrets in .env (not in repo)               │
└─────────────────────────────────────────────────┘
```

---

**Related Documents:**
- [data-flow.md](data-flow.md) – Detailed request lifecycle
- [api-contracts.md](api-contracts.md) – Endpoint specifications
- [algorithms.md](algorithms.md) – Algorithm implementations
