from __future__ import annotations
import math
import numpy as np
from typing import Dict, List
from collections import defaultdict
from .physioq_encoder import PhysioQEncoder


class QAOAMotifFinder:
    """PWM-based motif finder approximating a QAOA cost landscape."""

    def __init__(self):
        self.encoder = PhysioQEncoder()

    def _validate(self, sequences: List[str], motif_length: int) -> List[str]:
        if not sequences:
            raise ValueError("Provide at least one sequence")
        normalized = []
        for s in sequences:
            clean = self.encoder.validate(s)
            if len(clean) < motif_length:
                raise ValueError("Sequences must be at least the motif length")
            normalized.append(clean)
        return normalized

    def _build_pwm(self, windows: List[str], motif_length: int) -> np.ndarray:
        base_index = {"A": 0, "C": 1, "G": 2, "T": 3}
        counts = np.ones((4, motif_length))  # Laplace smoothing
        for w in windows:
            for idx, base in enumerate(w):
                counts[base_index[base], idx] += 1
        probs = counts / counts.sum(axis=0, keepdims=True)
        return probs

    def _information_content(self, pwm: np.ndarray) -> float:
        total_ic = 0.0
        for col in pwm.T:
            entropy = -sum(p * math.log2(p) for p in col)
            total_ic += max(0.0, 2.0 - entropy)  # 2 bits max per DNA position
        return float(total_ic)

    def find_motif(self, sequences: List[str], motif_length: int = 6) -> Dict:
        sequences = self._validate(sequences, motif_length)
        candidate_windows: List[str] = []
        positions: defaultdict[int, List[int]] = defaultdict(list)
        # Collect all windows for PWM estimation
        for idx, seq in enumerate(sequences):
            for i in range(0, len(seq) - motif_length + 1):
                window = seq[i : i + motif_length]
                candidate_windows.append(window)
                positions[idx].append(i)
        pwm = self._build_pwm(candidate_windows, motif_length)
        ic = self._information_content(pwm)

        # Score each window using log-likelihood under the PWM
        base_index = {"A": 0, "C": 1, "G": 2, "T": 3}
        best_score = -1e9
        best_window = None
        best_pos = None
        for seq_idx, seq in enumerate(sequences):
            for pos in positions[seq_idx]:
                window = seq[pos : pos + motif_length]
                log_likelihood = 0.0
                for col, base in enumerate(window):
                    p = pwm[base_index[base], col]
                    log_likelihood += math.log(p)
                if log_likelihood > best_score:
                    best_score = log_likelihood
                    best_window = window
                    best_pos = {"sequence_index": seq_idx, "start": pos}

        return {
            "motif": best_window,
            "positions": best_pos,
            "score": float(best_score),
            "information_content": ic,
        }
