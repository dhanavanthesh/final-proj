# QGENOME – Quantum Viterbi for DNA Sequences

**Full-stack, production-ready implementation** of the QGENOME project with real algorithms, database persistence, and dynamic data flow. This system implements PhysioQ encoding, Needleman-Wunsch alignment, PWM-based motif discovery, and feature-driven variant classification.

## Stack
- **Frontend:** React 18 (CDN) + Chart.js, responsive single-page application with real-time API integration
- **Backend:** FastAPI + SQLModel/SQLAlchemy with SQLite persistence
- **Database:** SQLite with full CRUD operations for run history
- **Algorithms:** 
  - Needleman-Wunsch alignment with traceback
  - Position Weight Matrix (PWM) motif search with information content
  - Logistic regression-based variant classifier with biological features
- **Environment:** Fully local, no cloud dependencies, runs on standard hardware

## Features
### Backend APIs
- **`POST /encode`** – PhysioQ 3-qubit-per-base encoding with hydrogen bonding angles
- **`POST /align`** – Needleman-Wunsch alignment with dynamic programming, traceback, and convergence history
- **`POST /find-motifs`** – PWM-based motif discovery with information content scoring
- **`POST /detect-variant`** – Feature-driven variant classification (GC content, Ti/Tv ratio, k-mer entropy, homopolymer analysis)
- **`POST /smith-waterman`** – Local sequence alignment with position tracking
- **`POST /blast-search`** – Word-based similarity search across sequences
- **`POST /batch-align`** – Batch process multiple sequence pairs
- **`POST /batch-motif`** – Find motifs in multiple sequence sets
- **`POST /visualize`** – Generate 3D DNA helix and quantum circuit diagrams
- **`GET /samples`** – Dynamic sample sequence generation with embedded motifs
- **`GET /runs`** – Fetch run history with filtering (limit, run_type)
- **`PATCH /runs/{id}`** – Update existing run scores/results
- **`DELETE /runs/{id}`** – Remove runs from database
- **`GET /health`** – Service health check

### Frontend Features
- Dynamic sequence loading from backend
- Real-time alignment visualization with Chart.js convergence plots
- Live metrics dashboard (alignment score, energy, qubits, iterations)
- Decoded path visualization (E=match, I=mismatch/gap)
- Motif position and information content display
- Variant classification with feature breakdown
- **Classical algorithm comparison** (Smith-Waterman, BLAST-like search)
- **3D DNA helix visualization** with base coordinates
- **Quantum circuit diagrams** for VQE/QAOA/QCNN
- Batch processing UI for multiple sequences
- Database-backed run history table
- JSON export functionality
- Comprehensive error handling and validation
- Loading states and user feedback

## Project Structure
```
Final_Project/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app with CRUD endpoints
│   ├── db.py                    # SQLModel database layer
│   ├── physioq_encoder.py       # PhysioQ 3-qubit encoding with validation
│   ├── vqe_alignment.py         # Needleman-Wunsch alignment algorithm
│   ├── qaoa_motif.py            # PWM-based motif search
│   ├── qcnn_variant.py          # Feature-driven variant classifier
│   └── requirements.txt         # Python dependencies
├── frontend/
│   └── index.html               # React SPA with dynamic API integration
├── .env.example                 # Environment configuration template
├── .gitiStart

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd Final_Project
```

### 2. Configure Environment
```bash
# Copy environment template
copy .env.example .env       # Windows
# OR
cp .env.example .env         # macOS/Linux

# Edit .env if needed (defaults work for local development)
```

### 3. Backend Setup
```bash
# Create virtual environment
cd API Reference

### Sequence Operations
```bash
# Encode sequence with PhysioQ
curl -X POST http://localhost:8000/encode \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGC"}'

# Align two sequences (Needleman-Wunsch)
curl -X POST http://localhost:8000/align \
  -H "Content-Type: application/json" \
  -d '{"sequence1":"ATGCGTAGC","sequence2":"ATGCGTGGG"}'

# Smith-Waterman local alignment
curl -X POST http://localhost:8000/smith-waterman \
  -H "Content-Type: application/json" \
  -d '{"sequence1":"ATGCGTAGC","sequence2":"ATGCGTGGG"}'

# BLAST-like sequence search
curl -X POST http://localhost:8000/blast-search \
  -H "Content-Type: application/json" \
  -d '{"sequences":["ATGCGTAGCT","ATGCGTGGCT","ATGCCTAGCT"],"motif_length":11}'

# Find motifs in multiple sequences
curl -X POST http://localhost:8000/find-motifs \
  -H "Content-Type: application/json" \
  -d '{"sequences":["ATGCGTAGCT","ATGCGTGGCT"],"motif_length":6}'

# Detect variants
curl -X POST http://localhost:8000/detect-variant \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGCGTAGCT"}'

# Generate 3D DNA helix coordinates
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGCGTAGCT","type":"helix"}'

# Generate quantum circuit diagram
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGCGTAGCT","type":"circuit"}'
```

### Batch Operations
```bash
# Batch align multiple sequence pairs
curl -X POST http://localhost:8000/batch-align \
  -H "Content-Type: application/json" \
  -d '{"sequence_pairs":[{"seq1":"ATGC","seq2":"ATCC"},{"seq1":"CGAT","seq2":"CGTA"}]}'

# Batch motif search
curl -X POST http://localhost:8000/batch-motif \
  -H "Content-Type: application/json" \
  -d '{"sequences_list":[[["ATGCGTAGCT","ATGCGTGGCT"],["ATGCCTAGCT"]]],"motif_length":6}'
```Usage Guide

### Frontend Workflow
1. **Load Sequences**
   - Click "Use sample data" to fetch dynamic sequences from backend
   - Or manually paste DNA sequences (A, T, G, C only)
   - Sequences are validated and normalized (case-insensitive)

2. **Run Analysis**
   -lgorithm Details

### PhysioQ Encoding
3-qubit-per-base encoding preserving biochemical properties:
- **Qubit 0**: Chemical class (purine vs pyrimidine)
- *Technical Implementation

### Database Schema
```python
class SequenceRun:
    id: int (primary key)
    run_type: str (align, motif, variant)
    sequence_a: str
   Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# RFuture Enhancements

### Completed Features ✅
- [x] Advanced visualizations (3D helix, circuit diagrams)
- [x] Comparison with classical algorithms (Smith-Waterman, BLAST)
- [x] Support for longer sequences with windowing/chunking
- [x] Batch processing for multiple sequence sets
- [x] Real-time progress with enhanced UI

### Remaining Planned Features
- [ ] Real-time WebSocket progress updates for long operations
- [ ] FASTQ file upload and parsing
- [ ] Export results to CSV/Excel
- [ ] User authentication and session management
- [ ] Advanced 3D visualization rendering with Three.js
- [ ] Comparison plots between algorithms
- [ ] Support for protein sequences (20 amino acids)
- [ ] Docker containerization for easy deployment
- [ ] CI/CD pipeline with automated testing

### Research Extensions
- Integration with quantum hardware (IBM Q, AWS Braket)
- Error mitigation strategies for NISQ devices
- Semi-Markov models for complex genomic features
- Quantum motif clustering algorithms
- Protein sequence support
- Multi-species alignment
# With coverage
pytest --cov=backend
```

### Code Quality
```bash
# Format code
pip install black isort
black backend/
isort backend/

# Type checking
pip install mypy
mypy backend/

# Linting
pip install flake8
flake8 backend/
```

### Database Management
```bash
# Reset database
rm qgenome.db
# Backend will auto-create on next startup

# Backup database
copy qgenome.db qgenome_backup.db

# VLicense & Credits

This project is a final-year academic implementation for educational purposes.

### Design
- UI colors: white/gray surfaces with blue accents (#0a5ec0)
- Responsive design matching modern bioinformatics tools
- Chart.js for convergence visualization

### Technologies
- **Backend**: FastAPI, SQLModel, NumPy
- **Frontend**: React, Chart.js
- **Database**: SQLite
- **No external dependencies**: Runs completely offline

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

For questions or issues, please open a GitHub issue.

---

**Note**: This is a quantum-inspired classical implementation. All algorithms run on standard CPUs without requiring quantum hardware
```

## Troubleshooting

### Backend won't start
- **Error**: `ModuleNotFoundError: No module named 'backend'`
  - **Solution**: Run `uvicorn backend.main:app` from project root, not backend directory

- **Error**: `Address already in use`
  - **Solution**: Kill existing process or use different port: `--port 8001`

### Frontend can't connect
- **Error**: `CORS policy` or `Failed to fetch`
  - **Solution**: Check CORS_ORIGINS in .env matches frontend URL
  - Verify backend is running on port 8000

### Database errors
- **Error**: Database locked
  - **Solution**: Close other connections, restart backend
  
- **Error**: No such table
  - **Solution**: Delete qgenome.db and let backend recreate it
### Environment Configuration
```ini
# .env file
API_PORT=8000
DATABASE_URL=sqlite:///./qgenome.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Dependencies
**Backend:**
- fastapi==0.110.0
- uvicorn[standard]==0.29.0
- sqlmodel==0.0.14
- python-dotenv==1.0.1
- numpy==1.24.4
- pydantic==1.10.14

**Frontend:**
- React 18 (CDN)
- Chart.js (CDN)
- Babel Standalone (CDN)
- Gap penalty: -2
- Full traceback for aligned sequences
- Normalized score (0-100) based on optimal/worst bounds
- Energy convergence trace for UI visualization

### PWM Motif Discovery
Position Weight Matrix with information content:
- Laplace smoothing for probability estimates
- Log-likelihood scoring per window
- Information content: bits preserved vs maximum entropy
- Returns best motif, position, and conservation score

### Variant Classification
Feature-based logistic classifier with biological features:
- GC content
- Transition/transversion ratio
- Longest homopolymer fraction
- K-mer entropy (k=3)
- PhysioQ mean hydrogen angle
- Length normalization
- Trained weights for pathogenic/benign classification
3. **View Results**
   - Alignment score (0-100), energy, and qubit count
   - Convergence chart shows energy landscape per iteration
   - Decoded path (E=match, I=mismatch/gap)
   - Motif position, information content, and consensus
   - Variant probability with feature breakdown (GC%, Ti/Tv, entropy)

4. **History & Export**
   - Recent runs table (auto-refreshed from database)
   - Download JSON results for further analysis
   - All runs persisted to SQLite automatically

### Input Validation
- **Valid bases**: A, T, G, C (case-insensitive)
- **Max length**: 500 bp per sequence
- **Motif length**: Must be ≤ sequence length
- Invalid input triggers error badges with helpful messages
curl http://localhost:8000/runs?run_type=align&limit=5

# Update run score
curl -X PATCH http://localhost:8000/runs/1 \
  -H "Content-Type: application/json" \
  -d '{"score":95.5}'

# Delete run
curl -X DELETE http://localhost:8000/runs/1
```

### Utility Endpoints
```bash
# Get dynamic sample sequences
curl http://localhost:8000/samples

# Health check
curl http://localhost:8000/healtht 0.0.0.0 --port 8000
```

The API will:
- Initialize SQLite database at `qgenome.db`
- Listen on `http://localhost:8000`
- Persist all alignment/motif/variant runs
- Auto-reload on code changes

### 4. Frontend Setup (New Terminal)
```bash
cd frontend
python -m http.server 3000
```

Access the application at **`http://localhost:3000`**

### 5. Verify Installation
```bash
# Test backend health
curl http://localhost:8000/health

# Test sample generation
curl http://localhost:8000/samples

# Test alignment
curl -X POST http://localhost:8000/align \
  -H "Content-Type: application/json" \
  -d '{"sequence1":"ATGCGTA","sequence2":"ATGCTTA"}'
```
```bash
cd frontend
python -m http.server 3000
```
- The UI will call `http://localhost:8000` for APIs (respecting CORS_ORIGINS).

## Sample API calls
```bash
# Encode
curl -X POST http://localhost:8000/encode -H "Content-Type: application/json" -d "{\"sequence\":\"ATGC\"}"

# Align (VQE)
curl -X POST http://localhost:8000/align -H "Content-Type: application/json" \
     -d "{\"sequence1\":\"ATGCGTAGC\",\"sequence2\":\"ATGCGTGGG\"}"

# Motif (QAOA)
curl -X POST http://localhost:8000/find-motifs -H "Content-Type: application/json" \
     -d "{\"sequences\":[\"ATGCGTAGCT\",\"ATGCGTGGCT\"],\"motif_length\":6}"

# Variant (QCNN)
curl -X POST http://localhost:8000/detect-variant -H "Content-Type: application/json" \
     -d "{\"sequence\":\"ATGCGTAGCT\"}"
```

## Demo walkthrough (aligns with screenshots)
1. **Home/Upload:** Paste FASTA/plain DNA for Sequence A/B, use sample data button.
2. **Model selection:** Choose VQE alignment, QAOA motif, QCNN variant via buttons.
3. **Processing screen:** Observe loading state and convergence chart.
4. **Decoded path visualization:** E (match) vs I (mismatch) ribbon shown in text.
5. **Performance dashboard:** Runtime, length, qubits, accuracy target table.
6. **Result export panel:** Download JSON for alignment/motif/variant outputs.
7. **Error handling:** Invalid bases/oversize (>500bp) return friendly badges.

## Assumptions (per report scope)
- Simulators only (no real quantum hardware); sequences ≤500 bp for demos.
- Qubit budget capped at 24 (3 qubits/base) for UI parity and quick demos.
- Accuracy/energy values are illustrative; align to report narratives, not benchmarked to real datasets.

## Viva prep (sample Q&A)
- **What is PhysioQ?** A 3-qubit encoding capturing chemical class, H-bond strength, and base identity, preserving biochemical meaning in quantum states.
- **Why VQE for alignment?** Casts alignment as an energy minimization; variational circuits search low-energy (good alignment) states.
- **Why QAOA for motifs?** Motif positions are a combinatorial search; QAOA alternates cost/mixer layers to amplify conserved windows.
- **QCNN role?** Uses convolution/pooling-like quantum layers to classify variants (pathogenic vs benign) from encoded sequences.
- **Limits?** NISQ constraints: qubit counts, noise, and simulator overhead; thus short-to-mid sequences and simulated runs only.
- **Classical baseline?** Classical Viterbi (hmmlearn-like) retained for side-by-side comparison and validation.

## Future enhancement ideas (from report)
- Move to real hardware (IBM/AWS) with error mitigation.
- Add FASTQ ingestion and batching.
- Support longer reads with compression or windowing.
- Extend to semi-Markov models and quantum motif clustering.
- Richer visualizations (3D helix, circuit diagrams) if GPU budget permits.

## Testing
- Manual: sample sequences through UI + curl smoke tests above.
- Validates: length guard, invalid nucleotide guard, convergence rendering, export.

## Notes
- UI colors: dominant white/gray surfaces with blue accents (#0a5ec0 / #226ccc) extracted from `demo_frontend_output` assets.
- Runs fully offline; no paid services.
