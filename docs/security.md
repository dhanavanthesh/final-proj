# Security

## Inputs & Validation
- Strict Pydantic models; reject unknown fields and invalid DNA chars.
- Enforce sequence length caps; limit shots/depth.

## Secrets & Config
- Use `.env` for Mongo URI; never commit secrets.
- Principle of least privilege on Mongo user.

## Data Protection
- Avoid storing raw PHI; hash or tokenize sensitive IDs.
- Consider field-level encryption for sensitive metadata.

## Transport & CORS
- Enforce HTTPS in prod; configure CORS origins to frontend only.

## DoS & Abuse
- Rate limit endpoints; cap payload size.
- Timeout long-running jobs; cancel on client abort where possible.

## Auditing
- Persist job status transitions and errors for forensics.
- Structured logs with correlation `job_id`/`run_id`.
