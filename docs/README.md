# QGENOME — Documentation (Overview)

## 1. High-Level Overview
- Problem: Interactive DNA sequence analysis (alignment, motif discovery, variant scoring) and HMM decoding using classical and quantum-style (Qiskit Aer) methods.
- Target users: Computational biologists, bioinformatics engineers, researchers, students.
- Type: Full-stack system — API backend (FastAPI), Algorithms (Python/NumPy/hmmlearn/Qiskit), Web UI (React), CLI tools, MongoDB persistence.
- Real-world use cases:
	- Compare classical vs quantum-style HMM decoding on gene-like sequences.
	- Run global/local alignment and visualize matches.
	- Discover short motifs across multiple sequences.
	- Score variant “pathogenicity” with interpretable features.

## 2. Architecture Summary
- Style: Layered monolith.
- Components:
	- UI (React): Calls API, renders charts/3D.
	- API (FastAPI): Validation, routing, orchestration.
	- Services/Algorithms: DP alignment, HMM Viterbi, PWM motif, QCNN-inspired variant.
	- Database (MongoDB): Runs, datasets, jobs.

## 3. System Flow (IN → PROCESS → OUT)
- Inputs: HTTP JSON (sequences, params), env vars (.env), MongoDB documents.
- Process: Validate → Create job → Run algorithm → Save run → Update job → Build response.
- Outputs: JSON results (scores, decoded paths, metrics), persisted records.
- Error handling: 400 for invalid inputs; 500 for unexpected errors; job status marked failed on exception.

## 4. Simple System Flow Diagram

```mermaid
flowchart LR
	User[User / SPA] -->|HTTP JSON| API[FastAPI]
	API -->|validate & route| Services[Algorithms]
	Services --> DB[(MongoDB)]
	API -->|JSON response| User
```

## 5. Beginner Friendly Summary
- Paste DNA letters (A/C/G/T) into the web app.
- Click a button (align, decode, find motif). The server checks inputs, runs math/algorithms, saves results.
- You see scores, decoded paths, charts, and 3D visuals. If inputs are invalid or too long, you’ll get a clear error.

## 6. Documentation Index

Navigate to specific topics:

| Document | Purpose |
|----------|---------|
| [architecture.md](architecture.md) | System components, responsibilities, and communication flows. |
| [data-flow.md](data-flow.md) | Request lifecycle, validation, transformations, error handling. |
| [algorithms.md](algorithms.md) | Algorithm summaries (Smith-Waterman, Viterbi, QAOA, QCNN) with complexity. |
| [core-logic.md](core-logic.md) | Backend module responsibilities, decision points, concurrency model. |
| [api-contracts.md](api-contracts.md) | Endpoint specifications with curl examples and field names. |
| [technology.md](technology.md) | Languages, frameworks, design patterns, deployment stack. |
| [performance.md](performance.md) | Hot paths, optimization tips, complexity analysis, monitoring. |
| [security.md](security.md) | Input validation, secrets, CORS, rate limiting, auditing. |
| [testing.md](testing.md) | Unit/integration test strategies, tools, example cases. |
| [pitfalls.md](pitfalls.md) | Common mistakes and edge cases to avoid. |
| [extension-guide.md](extension-guide.md) | How to add new algorithms, HMMs, and features. |
| [analogy.md](analogy.md) | High-level system analogy for quick mental model. |

---

**Next Steps:**
- Developers: Start with [architecture.md](architecture.md), then [api-contracts.md](api-contracts.md).
- Researchers: Read [algorithms.md](algorithms.md) for method details.
- DevOps: Check [technology.md](technology.md) and [performance.md](performance.md).
- Troubleshooting: See [pitfalls.md](pitfalls.md) and [security.md](security.md).
