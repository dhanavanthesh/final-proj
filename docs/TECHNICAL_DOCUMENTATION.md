# QGENOME — Full Technical Documentation

This document explains the project from beginner to senior-engineer depth, covering overview, architecture, data flow, algorithms, contracts, environment, performance, security, testing, pitfalls, extensibility, and a simple analogy. File references link to the workspace code.

---

## 1. High‑Level Overview

- Problem: Interactive DNA sequence analysis (alignment, motif discovery, variant scoring) and HMM decoding using both classical and quantum‑style (Qiskit Aer) approaches. Results are persisted for review.
- Target users: Computational biologists, bioinformatics engineers, researchers, students exploring quantum‑inspired genomics.
- System type: Full‑stack app:
  - Backend API: FastAPI (Python) exposing REST routes (alignment, motif, variant, Viterbi classical/quantum, datasets/jobs).
  - Algorithms: Deterministic DP alignment (Needleman–Wunsch variant), local alignment (Smith–Waterman), PWM motif finder, QCNN‑inspired variant scoring, HMM Viterbi (hmmlearn + Qiskit Aer).
  - Persistence: MongoDB (Motor async driver).
  - Frontend: React + Vite (Chart.js, Three.js visualizations).
- Real‑world use cases:
  - Compare classical vs quantum‑style Hidden Markov Model decoding on DNA sequences.
  - Run global/local alignments to score sequence similarity and visualize matches/mismatches.
  - Discover conserved motifs and rank candidates.
  - Score potential variant pathogenicity using interpretable sequence features.
  - Persist results and audit processing steps.

Beginner summary: You paste DNA letters (A/C/G/T) in a web UI; the server runs algorithms to align, decode, or analyze, saves results, and shows charts/3D visuals.

---

## 2. Architecture

- Style: Layered monolith.
  - API layer: request validation, routing, error handling.
  - Algorithm layer: pure Python/NumPy + hmmlearn + Qiskit Aer.
  - Persistence layer: MongoDB DAOs via Motor.
  - UI layer: React SPA calling REST endpoints.

- Key files and responsibilities:
  - API and orchestration:
    - [backend/main.py](backend/main.py): FastAPI app, routes, Pydantic models, CORS, lifespan hooks for Mongo, orchestration and error handling.
  - Persistence:
    - [backend/db.py](backend/db.py): connection management, `sequence_runs` CRUD (save/list/get/update/delete runs), indexes.
    - [backend/mongo_operations.py](backend/mongo_operations.py): high‑level ops for `datasets`, `processing_jobs`, `sequence_analysis` using Pydantic models.
    - [backend/models.py](backend/models.py): Pydantic models + enums (datasets, processing jobs, statuses, algorithm types).
  - Algorithms:
    - [backend/vqe_alignment.py](backend/vqe_alignment.py): Deterministic Needleman–Wunsch‑like alignment (named “VQE” for UI parity) with convergence trace and windowed mode.
    - [backend/smith_waterman.py](backend/smith_waterman.py): Smith–Waterman local alignment + BLAST‑like wrapper.
    - [backend/hmm_models.py](backend/hmm_models.py): HMM configurations (2‑state and 3‑state), base mappings, validation.
    - [backend/classical_viterbi.py](backend/classical_viterbi.py): Viterbi via hmmlearn (baseline).
    - [backend/qva_viterbi.py](backend/qva_viterbi.py): Quantum‑style Viterbi using Qiskit Aer per‑time‑step circuits.
    - [backend/qaoa_motif.py](backend/qaoa_motif.py): PWM motif discovery, IC scoring.
    - [backend/qcnn_variant.py](backend/qcnn_variant.py): QCNN‑inspired (feature‑based logistic) variant scoring.
  - Instrumentation & viz:
    - [backend/processing_logger.py](backend/processing_logger.py): step‑wise timing and details per job.
    - [backend/visualizations.py](backend/visualizations.py): helix coordinates, circuit topology, alignment segments.
  - CLI & setup:
    - [backend/cli.py](backend/cli.py): dataset/job CLI.
    - [backend/requirements.txt](backend/requirements.txt): Python deps.
  - Frontend:
    - [frontend/src/App.jsx](frontend/src/App.jsx): SPA, tabs, calls APIs, renders results.

- Component communication:
  - Frontend → Backend: `fetch` JSON to FastAPI endpoints.
  - Backend → MongoDB: Motor async ops with Pydantic (typed I/O).
  - Backend internal: Routes call algorithm modules and persistence helpers.

- Entry point and execution flow:
  - Backend: `uvicorn` executes [backend/main.py](backend/main.py) (`__main__` block starts the server); startup hook calls `connect_to_mongo()`, shutdown calls `close_mongo_connection()`.
  - Frontend: `vite dev` serves the SPA; it calls the API at `http://localhost:8000`.

ASCII sketch:
```
[ React SPA ] --HTTP/JSON--> [ FastAPI ] --async--> [ MongoDB ]
                         \--> Algorithms (DP, HMM, PWM, Qiskit)
```

---

## 3. Data Flow (IN → PROCESS → OUT)

Inputs:
- HTTP JSON (Pydantic models) from the SPA or tools (curl).
- Env vars (.env): `MONGODB_URL`, `DATABASE_NAME`, `API_PORT`, `CORS_ORIGINS`.
- MongoDB: persistent collections (`sequence_runs`, `datasets`, `processing_jobs`).

Example: `POST /align` in [backend/main.py](backend/main.py#L211-L270)
1. Pydantic validates `AlignRequest` with `sequence1`, `sequence2`.
2. Create a processing job via [backend/mongo_operations.py](backend/mongo_operations.py) (status pending → running).
3. Run `VQEAlignment.align()` ([backend/vqe_alignment.py](backend/vqe_alignment.py)): DP fill + traceback, normalized score, convergence history.
4. Persist a run record via `save_run()` ([backend/db.py](backend/db.py)).
5. Update job with result, score, and processing steps (from `ProcessingLogger`).
6. Return JSON: algorithm, results, job_id, processing_summary.

Validation/transform:
- DNA sequence validation in `PhysioQEncoder.validate()` ([backend/physioq_encoder.py](backend/physioq_encoder.py)).
- HMM model name validation in [backend/hmm_models.py](backend/hmm_models.py).
- Pydantic schemas ensure request shapes and helpful examples.

Errors:
- Invalid inputs → `HTTPException(400)`.
- Unexpected runtime issues → `HTTPException(500)`; jobs marked failed when applicable.
- Guards: length limits (e.g., 500 bp), valid bases only, shots kept moderate.

---

## 4. Algorithms Used

Each algorithm includes purpose, intuition, steps, and complexity.

1) Needleman–Wunsch‑like (global alignment) — `VQEAlignment.align()`
- Why: Robust global alignment baseline with explainable scoring.
- Solves: Maximal score alignment of two sequences end‑to‑end.
- Steps: init first row/column → DP recurrence (`match/delete/insert`) → traceback to build aligned sequences and `alignment_path`.
- Complexity: Time O(nm), Space O(nm).
- Optimizations: Convergence history, normalized score [0..100], windowed mode for long sequences.
- Alternatives: Gotoh (affine gaps), banded alignment, WFA.

2) Smith–Waterman (local alignment) — [backend/smith_waterman.py](backend/smith_waterman.py)
- Why: Best local matching subsequences; foundational for similarity search.
- Solves: Highest scoring local subalignment.
- Steps: DP with zero floor → track global max → traceback from max cell.
- Complexity: O(nm) time/space.
- Alternatives: SIMD‑accelerated SW, striped SW, WFA.

3) BLAST‑like heuristic — `BlastLike.search()`
- Why: Faster candidate filtering with word seeding + SW refinement.
- Steps: k‑mer indexing → hit counting → run SW on candidates → rank.
- Complexity: Approx O(N·L·k) + SW on top hits.
- Alternatives: Minimizer‑based seeding, FM‑index.

4) Classical Viterbi (HMM) — [backend/classical_viterbi.py](backend/classical_viterbi.py)
- Why: Baseline HMM decoding; comparison to QVA.
- Solves: Most likely hidden state path for a sequence.
- Steps: encode observations → set HMM params → hmmlearn `predict`/`decode` → get `decoded_path` and `log_probability`.
- Complexity: O(n·S²) time; space O(n·S) (S: states).
- Alternatives: Custom DP, CRF implementations.

5) Quantum‑style Viterbi — [backend/qva_viterbi.py](backend/qva_viterbi.py)
- Why: Educational quantum‑inspired decoding with Qiskit Aer.
- Solves: Iterative per‑time‑step measurement‑driven state decisions using emissions and current probabilities.
- Steps per t: build circuit (encode probs with RY, emissions with RZ) → transpile → simulate shots → pick most likely bitstring → map to state → update probabilities via transition matrix.
- Complexity: ~O(n · Csim(shots)); qubits = states; average circuit depth tracked.
- Alternatives: Full trellis QVA, statevector sims, tensor networks.

6) PWM Motif Finder — [backend/qaoa_motif.py](backend/qaoa_motif.py)
- Why: Simple, interpretable motif discovery.
- Solves: Identify a high likelihood k‑mer across sequences.
- Steps: slide windows → build PWM with Laplace smoothing → compute information content → score windows by log‑likelihood → choose best.
- Complexity: O(N·L·k).
- Alternatives: Gibbs sampling (MEME), planted motif, HMM motif models.

7) QCNN‑inspired Variant Scoring — [backend/qcnn_variant.py](backend/qcnn_variant.py)
- Why: Explainable features + logistic-like scoring.
- Solves: Pathogenic probability estimate using GC, Ti/Tv, homopolymer, k‑mer entropy, PhysioQ angle, length normalization.
- Steps: validate → extract features → weights·features+bias → sigmoid.
- Complexity: O(L) feature pass; O(1) inference.
- Alternatives: True CNN/transformers, gradient boosted trees.

---

## 5. Core Logic Deep Dive

A) `/align` route — [backend/main.py](backend/main.py#L211-L270)
- Creates a `ProcessingLogger` and a `processing_job` record, sets status to running.
- Calls `vqe_engine.align()` which:
  - Validates DNA and lengths.
  - Initializes DP matrices (scores, traceback), fills them row by row, collecting convergence info.
  - Traceback reconstructs `aligned_sequence1`, `aligned_sequence2`, and `alignment_path`.
  - Computes normalized score and returns a result dict.
- Persists a `sequence_run` and updates job with result, score, and step summary.
- Returns a JSON payload with `algorithm`, `results`, `job_id`, and `processing_summary`.
- Memory: DP uses (n+1)×(m+1) float/int arrays; path strings are linear in alignment length.

B) Classical Viterbi — [backend/classical_viterbi.py](backend/classical_viterbi.py#L10-L98)
- `validate_sequence()` ensures uppercase ACGT; `base_to_int()` maps to 0..3; observations reshaped `(len,1)`.
- hmmlearn model configured (CategoricalHMM or MultinomialHMM fallback), with parameters from `hmm_config`.
- `predict`/`decode` yields hidden states and log probability; indices mapped back to labels.

C) Quantum‑style Viterbi — [backend/qva_viterbi.py](backend/qva_viterbi.py#L74-L173)
- For each time step: build circuit per current probabilities and emission for observed base; measure; select likely bitstring; infer state; update probabilities; append path.
- Tracks `runtime_ms`, `circuit_depth`, `total_shots`.

---

## 6. Technologies & Tools

- Python 3: type hints, async/await (Motor), Pydantic validation.
- FastAPI + Pydantic: typed REST APIs, validation, OpenAPI generation.
- Motor (MongoDB): async client for throughput; indexes created for query speed.
- NumPy: numeric DP operations.
- hmmlearn: classical HMM/Viterbi.
- Qiskit Aer: quantum circuit simulation for QVA.
- React + Vite: SPA; Chart.js for plots; Three.js for 3D helix; fetch for HTTP.
- Design patterns:
  - DAO/Repository‑like persistence separation ([backend/db.py](backend/db.py), [backend/mongo_operations.py](backend/mongo_operations.py)).
  - Strategy‑like choice between classical vs quantum Viterbi via separate endpoints.
  - Builder‑style circuit construction in QVA.
  - DTOs via Pydantic models.

---

## 7. API / Function Contracts

Representative endpoints (see full routes in [backend/main.py](backend/main.py)):

- `POST /align`
  - Input: `{ sequence1: str, sequence2: str }`
  - Output: `{ algorithm: 'VQE', results: { ...alignment... }, job_id, processing_summary }`
  - Side effects: Saves `sequence_run`, creates/updates `processing_job`.
  - Constraints: A/C/G/T only; length ≤ 500; normalized scoring 0..100.

- `POST /smith-waterman`
  - Input: `{ sequence1, sequence2 }`
  - Output: local alignment result (score, aligned seqs, path, positions).

- `POST /find-motifs`
  - Input: `{ sequences: string[], motif_length: number }`
  - Output: `{ motif, positions, score, information_content }`.

- `POST /detect-variant`
  - Input: `{ sequence }`
  - Output: `{ pathogenic_probability, classification, features }`.

- `POST /viterbi/quantum | /viterbi/classical | /viterbi/compare`
  - Input: `{ sequence, hmm_model, shots? }`
  - Output: decoded path(s), metrics; `compare` returns agreement.

- Datasets & Jobs:
  - `POST /datasets`, `GET /datasets`, `GET /datasets/{id}`, `DELETE /datasets/{id}`.
  - `POST /jobs`, `GET /jobs`, `GET /jobs/{id}`.

Pydantic request models referenced: see [backend/main.py](backend/main.py#L84-L159).

---

## 8. Configuration & Environment

- Env vars (via `.env`):
  - `MONGODB_URL` (default `mongodb://localhost:27017`)
  - `DATABASE_NAME` (default `qgenome`)
  - `API_PORT` (default `8000`)
  - `CORS_ORIGINS` (comma list; defaults allow common localhost ports)
- CORS middleware configured in [backend/main.py](backend/main.py#L50-L64).
- Indexes:
  - `sequence_runs`: `run_type`, `created_at` desc ([backend/db.py](backend/db.py#L30-L47)).
  - Optional job indexes prepared in [backend/setup_mongodb.py](backend/setup_mongodb.py).

Run locally:
```bash
# Backend (from project root)
uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## 9. Performance & Scalability

- Bottlenecks:
  - Quadratic DP (global/local) for long sequences (time/space O(nm)).
  - Qiskit Aer simulation cost grows with shots and transpilation.
  - Mongo writes per operation (runs/jobs) — fine for light loads.
- Scaling:
  - Use banded DP, affine gaps (Gotoh), or WFA for speed/space improvements.
  - Queue long computations (Celery/RQ) and return job IDs; poll results.
  - Horizontal scale FastAPI; shard/replicate Mongo as needed.
- Concurrency:
  - FastAPI async helps I/O; heavy CPU tasks could be offloaded to worker processes.
- Caching:
  - None built‑in; consider memoization keyed by inputs for repeated analyses.

---

## 10. Security Considerations

- AuthN/Z: None provided; add API keys or OAuth for production.
- Validation: Strong DNA base validation and model name checks; Pydantic shapes enforced.
- Potential issues:
  - Open dev CORS is acceptable locally; restrict in prod.
  - DoS via oversize inputs or large `shots`; bounded by length guards; add explicit rate/size limits.
- Enforcement:
  - `HTTPException` with status codes; job failure states recorded for auditing.

---

## 11. Testing

- Unit tests:
  - DNA validation and encoding (PhysioQ).
  - VQE (NW) DP fill/traceback on toy inputs; Smith–Waterman on known pairs.
  - Motif PWM scoring; QCNN feature extraction and classifier monotonicity checks.
  - HMM decoding sanity (classical & quantum‑style) on short sequences.
- Integration tests:
  - API routes via httpx against a test Mongo (or mock Motor).
  - Contracts: Pydantic schemas accept+reject cases.
- Example cases:
  - VQE: identical sequences → high normalized score (~100); randoms → lower score.
  - SW: known local motif alignment recovers expected score/window.
  - Viterbi: `ACGT` under 2‑state model returns length‑4 decoded path; `compare` returns agreement metrics.

---

## 12. Common Pitfalls

- Mongo not reachable or wrong URL → startup or first DB call fails.
- Sequence validation: lowercase or invalid letters cause 400; ensure uppercase A/C/G/T.
- Length guards: >500 bp rejected; adjust only with care.
- hmmlearn differences: `CategoricalHMM` vs `MultinomialHMM` in different versions — code handles fallback.
- Shots too large on QVA: latency grows; keep around 1024 for dev.

---

## 13. How to Modify or Extend

- Add a new algorithm endpoint:
  1) Implement core logic in a new module under `backend/`, returning JSON‑friendly dicts.
  2) Add an enum value in [backend/models.py](backend/models.py) `AlgorithmType` if persisted.
  3) Add a Pydantic request model and FastAPI route in [backend/main.py](backend/main.py); wire `ProcessingLogger`, create/update jobs, and `save_run()` if you want history.
  4) Update the SPA handler in [frontend/src/App.jsx](frontend/src/App.jsx) and render UI (new component if necessary).
- Add HMM models:
  - Extend `HMM_CONFIGS` in [backend/hmm_models.py](backend/hmm_models.py); frontend will list via `/hmm/models`.
- Do not change (without coordinated updates):
  - Request/response field names expected by the frontend and persisted in Mongo.
  - Job state transitions unless you update UI and tools relying on them.

---

## 14. Simple Analogy

Think of QGENOME as a modern genomics lab:
- Reception (FastAPI) checks your sample form (Pydantic validation).
- Workbenches (algorithms): global alignment, local alignment, motif discovery, HMM decoders (classical/quantum‑style).
- Lab notebook (MongoDB) records each experiment with steps, times, and results.
- Observation room (React) shows graphs and 3D molecule visuals.
- The lab manager (ProcessingLogger) timestamps and summarizes every step for audits.

---

## Depth by Audience

- Beginner: Use the UI to paste sequences and click buttons. If you see an error, ensure only A/C/G/T and keep sequences reasonably short.
- Intermediate: Read the route handlers in [backend/main.py](backend/main.py), then inspect algorithm modules to understand data contracts and return formats. Try sample curl calls.
- Senior: Consider algorithmic improvements (banded DP, WFA), add a task queue for heavy processing, constrain shots, and add auth/rate limiting. Tighten indexes and consider schema for cross‑linking runs ↔ jobs.
