# API Contracts

This summarizes key REST endpoints exposed by the backend with field names, constraints, and examples.

## Core Endpoints

### Health & Info
- GET /health
  - Response: { status: "ok" }
  - Example: `curl http://localhost:8000/health`

- GET /samples
  - Response: Sample sequence pairs for testing.
  - Example: `curl http://localhost:8000/samples`

### Alignment
- POST /align
  - Request: { sequence1: str, sequence2: str }
  - Response: { algorithm, results: {...}, job_id, processing_summary }
  - Constraints: DNA only (A/C/G/T), recommend < 5000 bp each.
  
  ```bash
  curl -X POST http://localhost:8000/align \
    -H "Content-Type: application/json" \
    -d '{"sequence1": "ATGCGTACG", "sequence2": "ATGCTTACG"}'
  ```

### Viterbi Algorithm
- POST /viterbi/quantum
  - Request: { sequence: str, hmm_model?: str, shots?: int, save_to_db?: bool }
  - Response: { algorithm, hmm_model, results: {...} }
  - Constraints: 16-2048 shots recommended; sequence < 500 bp for simulator speed.
  
  ```bash
  curl -X POST http://localhost:8000/viterbi/quantum \
    -H "Content-Type: application/json" \
    -d '{"sequence": "ATGCCTACGCATGCTA", "hmm_model": "2-state-exon-intron", "shots": 1024}'
  ```

- POST /viterbi/classical
  - Request: { sequence: str, hmm_model?: str, save_to_db?: bool }
  - Response: { algorithm, hmm_model, results: {...} }
  - Use for baseline comparison; fast and deterministic.
  
  ```bash
  curl -X POST http://localhost:8000/viterbi/classical \
    -H "Content-Type: application/json" \
    -d '{"sequence": "ATGCCTACGCATGCTA", "hmm_model": "2-state-exon-intron"}'
  ```

- POST /viterbi/compare
  - Request: { sequence: str, hmm_model?: str, shots?: int, save_to_db?: bool }
  - Response: { classical: {...}, quantum: {...}, comparison_metrics }
  
  ```bash
  curl -X POST http://localhost:8000/viterbi/compare \
    -H "Content-Type: application/json" \
    -d '{"sequence": "ATGCCTACGCATGCTA", "shots": 1024}'
  ```

- GET /hmm/models
  - Response: List of available HMM model names and descriptions.
  - Example: `curl http://localhost:8000/hmm/models`

### Motif Discovery
- POST /find-motifs
  - Request: { sequences: [str, ...], motif_length?: int }
  - Response: { motifs: [...], run_id }
  
  ```bash
  curl -X POST http://localhost:8000/find-motifs \
    -H "Content-Type: application/json" \
    -d '{"sequences": ["ATGCATGC", "CGTAGCTA"], "motif_length": 6}'
  ```

### Variant Detection
- POST /detect-variant
  - Request: { sequence: str }
  - Response: { variant_score, classification }
  
  ```bash
  curl -X POST http://localhost:8000/detect-variant \
    -H "Content-Type: application/json" \
    -d '{"sequence": "ATGCGTACG"}'
  ```

### Sequence Alignment (Classical)
- POST /smith-waterman
  - Request: { sequence1: str, sequence2: str }
  - Response: { score, alignment, run_id }

- POST /blast-search
  - Request: { sequence: str, database?: str }
  - Response: { matches: [...], run_id }

### Datasets
- POST /datasets
  - Request: { name: str, description?: str, sequences: [str], tags?: [str] }
  - Response: { id, name, created_at }
  
  ```bash
  curl -X POST http://localhost:8000/datasets \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Dataset",
      "description": "Sample sequences",
      "sequences": ["ATGC", "CGTA"],
      "tags": ["gene"]
    }'
  ```

- GET /datasets
  - Response: { items: [{id, name, created_at, ...}] }
  - Example: `curl http://localhost:8000/datasets`

- GET /datasets/{dataset_id}
  - Response: Full dataset details with all sequences.

### Runs / History
- GET /runs
  - Response: { items: [...] } — all recorded runs (align, viterbi, etc.)
  - Example: `curl http://localhost:8000/runs`

- DELETE /runs/{run_id}
  - Response: { status: "deleted" }

## Notes
- All requests use `Content-Type: application/json`.
- All error responses include `{ detail: "error message" }`.
- HTTP codes: 200 success, 400 invalid input, 422 validation error, 500 server error.
- DNA sequences must be uppercase A/C/G/T only.
- See [backend/models.py](../../backend/models.py) for exact Pydantic shapes.
