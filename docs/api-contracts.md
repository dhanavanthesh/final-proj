# API Contracts

This summarizes key REST endpoints exposed by the backend.

## Alignment
- POST /align
  - body: { seqA, seqB, scoring?, method?: "smith-waterman"|"vqe" }
  - resp: { score, alignment, path, run_id?, job_id? }

## Viterbi
- POST /viterbi/classical
  - body: { observations, hmmModel }
  - resp: { path, logLikelihood, metrics, run_id }
- POST /viterbi/quantum
  - body: { observations, hmmModel, shots?, depth? }
  - resp: { pathApprox, stats, run_id }
- POST /viterbi/compare
  - body: { observations, hmmModel, shots?, depth? }
  - resp: { classical: {...}, quantum: {...}, delta }

## Motif
- POST /motif/qaoa
  - body: { sequences, k, constraints? }
  - resp: { motifs: [{motif, score}], run_id }

## Variant
- POST /variant/qcnn
  - body: { sequences, labels? }
  - resp: { scores or probs, run_id }

## Datasets
- GET /datasets
  - resp: { items: [...] }
- POST /datasets
  - body: { name, sequences, metadata? }
  - resp: { dataset_id }

## Jobs
- GET /jobs/{id}
  - resp: { id, status, result?, error? }
- GET /jobs
  - query: { status? }
  - resp: { items: [...] }

Notes
- All responses are JSON; errors use { detail } with proper HTTP codes.
- See models in backend/models.py for exact shapes and examples.
