# Pitfalls

- Unbounded sequence length causing memory/latency spikes.
- Mismatched HMM model names leading to 422s.
- Quantum simulator parameters (shots/depth) set too high.
- Blocking CPU work in async endpoints causing event-loop stalls.
- Missing Mongo indexes causing slow list queries.
- Storing huge DP matrices in DB bloats storage; persist summaries.
- Non-deterministic results without fixed seeds complicate testing.
- CORS too permissive or secrets committed to repo.
