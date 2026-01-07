# Core Logic

## Backend Responsibilities
- API orchestration and validation (FastAPI + Pydantic).
- Algorithm delegation (classical vs quantum modules).
- Persistence of runs, datasets, and jobs (Mongo via Motor).
- Logging and metrics collection for processing steps.

## Key Modules
- main.py: route handlers and composition of services.
- models.py: Pydantic request/response DTOs and enums.
- db.py: Mongo connection lifecycle, database handle export.
- mongo_operations.py: CRUD helpers for runs, jobs, datasets.
- classical_viterbi.py, qva_viterbi.py: HMM path decoding implementations.
- smith_waterman.py, vqe_alignment.py: alignment algorithms.

## Decision Points
- Which algorithm to run: derive from endpoint or payload flag.
- Which HMM to use: model name maps to preset in hmm_models.py.
- Whether to create a job: long-running or batch requests create jobs.
- When to persist: always save successful runs; save failures for audit when job tracking enabled.

## Error Handling
- ValidationError → 400 with message.
- Known algorithm errors → 422 with detail.
- Unexpected errors → 500; log + mark job failed when applicable.

## Concurrency Model
- FastAPI async endpoints; heavy CPU tasks can offload to threads/processes if needed.
- Mongo operations are async via Motor; avoid blocking in event loop.

## Idempotency & Reproducibility
- Deterministic seeds for stochastic routines when provided.
- Persist parameters and versions with each run document.
- Return `job_id` and `run_id` for traceability.
