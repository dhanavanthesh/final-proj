# Data Flow

## Request Lifecycle (Step-by-Step)
1. Client sends JSON to FastAPI (e.g., `/align`, `/viterbi/quantum`).
2. Pydantic validates request shape and examples.
3. If tracking needed: create `processing_job` (pending → running).
4. Call algorithm service (alignment / Viterbi / motif / variant).
5. Persist `sequence_run` results in MongoDB.
6. Update `processing_job` with result/score/steps (completed or failed).
7. Return JSON response to client.

## Validation
- DNA sequences validated for A/C/G/T and length caps.
- HMM model name validated.
- Pydantic ensures required fields and types.

## Transformations
- Sequence normalization (uppercase, trimmed).
- DP matrices computed and traced back.
- HMM observations encoded (0..3); quantum circuits built/transpiled.

## Response Generation
- Minimal JSON with algorithm name, metrics, decoded paths/alignments, and optional `job_id`.

## Edge Cases
- Empty or invalid characters → 400.
- Overly long sequences → 400.
- Quantum shots too high → longer latency; advise defaults.
- DB connectivity issues → 500; jobs marked failed when applicable.

## Flowchart

```mermaid
flowchart TD
  A[Client Request] --> B[Validate (Pydantic + DNA checks)]
  B -->|valid| C[Create/Update Job]
  B -->|invalid| X[HTTP 400]
  C --> D[Run Algorithm]
  D -->|success| E[Save Run to Mongo]
  D -->|error| Y[Mark Job Failed + HTTP 500]
  E --> F[Update Job Completed]
  F --> G[Build JSON Response]
  G --> H[Client]
```
