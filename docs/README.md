# 📚 QGENOME Documentation

Welcome to the QGENOME technical documentation. This guide covers all aspects of the system architecture, APIs, algorithms, and deployment.

---

## What is QGENOME?

**QGENOME** is a full-stack bioinformatics platform combining classical and quantum-inspired algorithms for DNA sequence analysis.

| Aspect | Details |
|--------|---------|
| **Purpose** | Interactive DNA sequence alignment, motif discovery, variant classification |
| **Users** | Computational biologists, researchers, bioinformatics engineers, students |
| **Architecture** | Layered monolith (API + Services + Database) |
| **Tech Stack** | FastAPI, React, SQLite/MongoDB, NumPy, Qiskit Aer |
| **Deployment** | Local/on-premise, fully offline capable |

---

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     👤 USER / WEB BROWSER                      │
│                                                                 │
└────────────────────────────┬──────────────────────────────────┘
                             │
                    HTTP/JSON │ JSON Response
                             │
                    ┌────────▼────────┐
                    │   🎨 REACT UI   │
                    │   - Components  │
                    │   - Chart.js    │
                    │   - 3D Viz      │
                    └────────┬────────┘
                             │
                       API Calls
                             │
        ┌────────────────────▼────────────────────┐
        │         ⚡ FASTAPI (Routes)             │
        │   - Validation (Pydantic)              │
        │   - Request Routing                    │
        │   - CORS & Error Handling              │
        └────────────────────┬────────────────────┘
                             │
                      Orchestrate
                             │
    ┌────────────────────────▼────────────────────────┐
    │      🧬 ALGORITHM SERVICES                      │
    │  ┌─────────────┐  ┌──────────────┐            │
    │  │ Alignment   │  │ Motif Search │            │
    │  │ - NW        │  │ - PWM Score  │            │
    │  │ - SW        │  │ - IC Calc    │            │
    │  └─────────────┘  └──────────────┘            │
    │  ┌─────────────┐  ┌──────────────┐            │
    │  │ Variant     │  │ HMM Decoding │            │
    │  │ - Features  │  │ - Viterbi    │            │
    │  │ - Classify  │  │ - Scoring    │            │
    │  └─────────────┘  └──────────────┘            │
    └────────────────────┬────────────────────────────┘
                         │
                   Persist Results
                         │
                   ┌─────▼──────┐
                   │ 💾 DATABASE │
                   │ SQLite/Mongo│
                   └──────────────┘
```

---

## Real-World Use Cases

### 1. Sequence Alignment
- **Scenario:** Compare two DNA sequences to find similarity regions
- **Output:** Alignment score, decoded path (matches vs mismatches), visualization

### 2. Motif Discovery
- **Scenario:** Find conserved patterns across multiple sequences
- **Output:** Consensus motif, positions, information content score

### 3. Variant Classification
- **Scenario:** Classify genetic variants as pathogenic or benign
- **Output:** Risk score, biological feature breakdown

### 4. Classical vs Quantum Comparison
- **Scenario:** Benchmark quantum-inspired HMM decoding vs classical
- **Output:** Side-by-side accuracy metrics and performance stats

---

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[architecture.md](architecture.md)** | System components, responsibilities, data flow | Architects, Backend Devs |
| **[algorithms.md](algorithms.md)** | Algorithm details, complexity analysis, implementation | Algorithm Engineers |
| **[api-contracts.md](api-contracts.md)** | REST endpoints, request/response schemas | Frontend Devs, API Users |
| **[data-flow.md](data-flow.md)** | Request lifecycle, validation, error handling | Full-Stack Engineers |
| **[performance.md](performance.md)** | Benchmarks, optimization, tuning | DevOps, Performance Engineers |
| **[security.md](security.md)** | Authentication, input validation, best practices | Security Engineers |
| **[testing.md](testing.md)** | Unit tests, integration tests, test strategy | QA Engineers |
| **[technology.md](technology.md)** | Tech stack decisions, dependency rationale | Tech Leads |
| **[extension-guide.md](extension-guide.md)** | Adding new algorithms and features | Contributors |
| **[pitfalls.md](pitfalls.md)** | Common mistakes and gotchas | All Engineers |

---

## System Mental Model

### Input → Process → Output

```
┌──────────────────────┐
│ 📝 INPUT             │
│ - DNA Sequences      │
│ - Parameters         │
│ - User Settings      │
└──────────┬───────────┘
           │
           │ VALIDATE
           │
┌──────────▼───────────────────┐
│ ⚙️  PROCESS                   │
│ - Select Algorithm            │
│ - Run Computation             │
│ - Generate Metrics            │
└──────────┬───────────────────┘
           │
           │ COMPUTE
           │
┌──────────▼──────────────────┐
│ 📊 OUTPUT                    │
│ - Score & Results            │
│ - Visualization (Charts)     │
│ - Decoded Path               │
└──────────┬──────────────────┘
           │
           │ SAVE
           │
┌──────────▼──────────────────┐
│ 💾 PERSIST                   │
│ - Store in Database          │
│ - Create Run Record          │
└──────────────────────────────┘
```

**Step 1: Input**
- User submits DNA sequences via web UI or API
- System validates: format (ACGT only), length (≤500bp), type

**Step 2: Process**
- Algorithm selected (alignment, motif, variant)
- Computation runs on backend
- Results generated with metrics

**Step 3: Output**
- Results returned to user
- Visualizations rendered (charts, 3D helix)
- Data persisted to database

---

## Getting Started Paths

### 👨‍💻 As a Backend Developer
1. Read [architecture.md](architecture.md) – understand components
2. Read [data-flow.md](data-flow.md) – understand request lifecycle
3. Read [api-contracts.md](api-contracts.md) – learn endpoints
4. Run tests: `pytest backend/`

### 🎨 As a Frontend Developer
1. Read [api-contracts.md](api-contracts.md) – learn endpoints
2. Check [data-flow.md](data-flow.md) – understand request/response
3. Review component architecture in `frontend/src/`
4. Test API integration with sample calls

### 🧬 As an Algorithm Engineer
1. Read [algorithms.md](algorithms.md) – understand implementations
2. Read [extension-guide.md](extension-guide.md) – add new algorithms
3. Read [performance.md](performance.md) – optimize existing ones
4. Review individual algorithm files in `backend/`

### 🚀 For Deployment
1. Read main [README.md](../README.md) – installation
2. Read [security.md](security.md) – hardening
3. Read [performance.md](performance.md) – tuning
4. Review `.env.example` configuration

---

## Key Concepts Glossary

| Term | Definition |
|------|-----------|
| **VQE Alignment** | Variational Quantum Eigensolver-inspired sequence alignment using DP |
| **Smith-Waterman** | Classic local sequence alignment algorithm |
| **HMM** | Hidden Markov Model for sequence decoding |
| **Viterbi** | Algorithm to find most likely hidden state sequence |
| **PWM** | Position Weight Matrix for motif scoring |
| **QAOA** | Quantum Approximate Optimization Algorithm |
| **QCNN** | Quantum Convolutional Neural Network |
| **PhysioQ** | 3-qubit encoding preserving biochemical properties |

---

## Architecture Highlights

### Layered Design
```
┌─────────────────────────┐
│   React SPA (UI)        │
├─────────────────────────┤
│   FastAPI (Routes)      │
├─────────────────────────┤
│  Algorithm Services     │
├─────────────────────────┤
│  Database (SQLite/Mongo)│
└─────────────────────────┘
```

### Technology Choices
- **FastAPI** – Modern, async-capable web framework
- **SQLite** – Zero-config local database, or MongoDB for scale
- **React** – Interactive UI with real-time updates
- **NumPy** – Efficient sequence computation
- **Qiskit Aer** – Quantum simulator backend

---

## Common Tasks

### Add a New Algorithm
→ See [extension-guide.md](extension-guide.md)

### Deploy to Production
→ See main [README.md](../README.md) and [security.md](security.md)

### Optimize Performance
→ See [performance.md](performance.md)

### Debug Issues
→ See [pitfalls.md](pitfalls.md)

### Write Tests
→ See [testing.md](testing.md)

---

## Support & Resources

> **Need help?**  
> 1. Check [pitfalls.md](pitfalls.md) for common issues  
> 2. Review [data-flow.md](data-flow.md) for request lifecycle  
> 3. Check [api-contracts.md](api-contracts.md) for endpoint details

> **Contributing?**  
> Follow [extension-guide.md](extension-guide.md) for best practices

---

## Document Maintenance

| Document | Last Updated | Owner |
|----------|--------------|-------|
| README.md | Jan 2025 | Tech Docs Team |
| architecture.md | Jan 2025 | Architects |
| algorithms.md | Jan 2025 | Algorithm Team |
| api-contracts.md | Jan 2025 | API Owners |

---

**Quick Links:**  
[🏗️ Architecture](architecture.md) • [📘 Algorithms](algorithms.md) • [🔌 API Docs](api-contracts.md) • [🚀 Deployment](../README.md)
