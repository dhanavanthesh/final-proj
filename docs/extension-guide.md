# Extension Guide

## Add a New Algorithm
1. Create `backend/new_algo.py` with a `run(request) -> ResultDTO`.
2. Add request/response models in `backend/models.py`.
3. Register an endpoint in `backend/main.py`.
4. Optionally add job creation + persistence in `mongo_operations.py`.
5. Update frontend fetch + UI component to consume results.

## Plugging a New HMM
- Add model preset in `backend/hmm_models.py`.
- Validate name in request and map to preset.

## Batch/Async Processing
- For long runs, create `processing_job` first and return `job_id`.
- Add a worker (Celery/RQ) for background execution if needed.

## Observability
- Add timing around hot paths; log `job_id`/`run_id`.
- Expose `/metrics` if deploying with Prometheus.

## Deployment
- Provide `MONGO_URI`, `DB_NAME`, feature flags in `.env`.
- Run with `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.
