# Testing

## Scope
- Unit tests for algorithms (scores, paths, edge cases).
- API tests for contracts and error codes.
- Integration tests with temporary Mongo instance.

## Strategy
- Build small synthetic sequences with known outcomes.
- Snapshot JSON responses for regression.
- Seed stochastic components for determinism.

## Example Cases
- Smith-Waterman identical strings → full match score.
- Viterbi with trivial HMM → known path.
- Quantum Viterbi with low shots → variance bounded within tolerance.

## Tooling
- `pytest` with `pytest-asyncio`.
- `httpx` for FastAPI test client.
- `mongomock` or Testcontainers for Mongo.

## CI Suggestions
- Lint, type-check, run tests on push.
- Cache Python/Node deps to speed builds.
