# Performance

## Hot Paths
- DP matrix fills in Smith-Waterman and Viterbi recursion.
- Circuit simulation (shots × depth) for quantum-inspired calls.

## Recommendations
- Use classical methods for long sequences; cap length in API.
- Limit `shots` and circuit depth; reuse transpiled circuits.
- Vectorize NumPy operations; avoid Python loops in inner cores.
- Enable Mongo indexes on `created_at`, `dataset_id`, `job_id`.
- Batch inserts/updates for dataset loads.

## Complexity Summary
- Smith-Waterman: O(n·m) time/space.
- Viterbi: O(N·S^2) time, O(N·S) space.
- Quantum variants: roughly linear in shots × circuit_size per iteration.

## Monitoring
- Record algorithm durations and sizes; export Prometheus-friendly metrics if needed.
- Track queue times vs compute times for jobs.
