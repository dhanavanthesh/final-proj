from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
from .physioq_encoder import PhysioQEncoder


class QCNNVariantDetector:
    """QCNN-inspired classifier using biologically meaningful features."""

    def __init__(self):
        self.encoder = PhysioQEncoder()
        # Deterministic weights for reproducibility
        self.weights = np.array([0.6, 1.2, -0.8, 0.4, 0.9, -0.3])
        self.bias = -0.2

    def _gc_content(self, seq: str) -> float:
        gc = sum(1 for c in seq if c in {"G", "C"})
        return gc / len(seq)

    def _transition_transversion_ratio(self, seq: str) -> float:
        transitions = 0
        transversions = 0
        purines = {"A", "G"}
        pyrimidines = {"C", "T"}
        for a, b in zip(seq, seq[1:]):
            if a == b:
                continue
            if (a in purines and b in purines) or (a in pyrimidines and b in pyrimidines):
                transitions += 1
            else:
                transversions += 1
        if transversions == 0:
            return float(transitions) if transitions > 0 else 0.0
        return transitions / transversions

    def _longest_homopolymer(self, seq: str) -> int:
        longest = 1
        current = 1
        for a, b in zip(seq, seq[1:]):
            if a == b:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    def _kmer_entropy(self, seq: str, k: int = 3) -> float:
        counts = Counter(seq[i : i + k] for i in range(len(seq) - k + 1))
        total = sum(counts.values())
        if total == 0:
            return 0.0
        entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
        return entropy / k

    def _physioq_mean_angle(self, seq: str) -> float:
        angles = [self.encoder.hydrogen_angles[b] for b in seq]
        return float(sum(angles) / len(angles))

    def extract_features(self, seq: str) -> np.ndarray:
        length_norm = len(seq) / 500.0
        return np.array(
            [
                self._gc_content(seq),
                self._transition_transversion_ratio(seq),
                self._longest_homopolymer(seq) / len(seq),
                self._kmer_entropy(seq),
                self._physioq_mean_angle(seq) / math.pi,
                length_norm,
            ]
        )

    def train(self, training_data: List[Tuple[str, int]], epochs: int = 10) -> Dict:
        # Simple perceptron-style update using provided labels (1 pathogenic, 0 benign)
        lr = 0.1
        for _ in range(epochs):
            for seq, label in training_data:
                seq = self.encoder.validate(seq)
                x = self.extract_features(seq)
                logit = float(np.dot(self.weights, x) + self.bias)
                pred = 1 / (1 + math.exp(-logit))
                error = label - pred
                self.weights += lr * error * x
                self.bias += lr * error
        return {"training_complete": True, "weights": self.weights.tolist(), "bias": self.bias}

    def predict(self, sequence: str) -> Dict:
        sequence = self.encoder.validate(sequence)
        features = self.extract_features(sequence)
        logit = float(np.dot(self.weights, features) + self.bias)
        pathogenic_probability = 1 / (1 + math.exp(-logit))
        return {
            "pathogenic_probability": pathogenic_probability,
            "classification": "Pathogenic" if pathogenic_probability >= 0.5 else "Benign",
            "features": {
                "gc_content": features[0],
                "ti_tv_ratio": features[1],
                "homopolymer_fraction": features[2],
                "kmer_entropy": features[3],
                "mean_angle_pi": features[4],
                "length_norm": features[5],
            },
        }
