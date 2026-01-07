# Algorithms

This project implements both classical and quantum-inspired algorithms for sequence analysis.

## Smith-Waterman (Local Alignment)
- File: backend/smith_waterman.py
- Input: two sequences, scoring params.
- Output: best local alignment, score, traceback path.
- Complexity: O(n·m) time, O(n·m) space (can be optimized to O(min(n,m)) space for score only).

## VQE-based Alignment (Global-ish with Quantum-inspired Features)
- File: backend/vqe_alignment.py
- Idea: Parameterized circuits encode subsequences and optimize cost via expectation values.
- Output: alignment proposal and score.
- Notes: Uses Qiskit Aer simulator; stochastic; tune shots/optimizer.

## Classical Viterbi (HMM)
- File: backend/classical_viterbi.py
- Input: HMM (states, start/transition/emission), observed sequence.
- Output: most likely hidden-state path + log-likelihood.
- Complexity: O(N·S^2) time, O(N·S) space.

## Quantum-inspired Viterbi Approximation
- File: backend/qva_viterbi.py
- Idea: Map transitions/emissions to quantum amplitude patterns; sample paths.
- Output: approximate path, likelihood proxies, statistics.
- Tuning: number of shots, circuit depth.

## QAOA Motif Discovery
- File: backend/qaoa_motif.py
- Goal: Find motifs satisfying constraints by minimizing a cost Hamiltonian.
- Output: candidate motifs with scores.

## QCNN Variant Classification
- File: backend/qcnn_variant.py
- Goal: Classify variant patterns using quantum convolutional layers on encodings.
- Output: class probabilities or scores.

## HMM Models
- File: backend/hmm_models.py
- Provides reusable HMM presets for DNA; supports plugging into Viterbi endpoints.

## Encoding Utilities
- File: backend/physioq_encoder.py
- Map nucleotides to numerical/angle encodings for circuit building.

## Selection Strategy
- File: backend/main.py (endpoints)
- Strategy pattern to select classical vs quantum Viterbi based on request.

## Performance Tips
- Prefer classical algorithms for length > 2k.
- Limit quantum shots and depth; cache compiled circuits.
- Use batch jobs for large datasets; stream results incrementally.
