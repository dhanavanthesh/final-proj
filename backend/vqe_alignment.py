from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple
from .physioq_encoder import PhysioQEncoder


class VQEAlignment:
    """Deterministic Needleman–Wunsch alignment with convergence trace.

    We keep the "VQE" naming for UI parity, but expose a real dynamic
    programming alignment, normalized scoring, and an energy-like trace
    derived from the running best alignment score.
    """

    def __init__(self, max_qubits: int = 4096):
        self.encoder = PhysioQEncoder()
        self.max_qubits = max_qubits
        self.match_score = 2.0
        self.mismatch_penalty = -1.0
        self.gap_penalty = -2.0

    def _validate_inputs(self, seq1: str, seq2: str) -> tuple[str, str]:
        seq1 = self.encoder.validate(seq1)
        seq2 = self.encoder.validate(seq2)
        if len(seq1) == 0 or len(seq2) == 0:
            raise ValueError("Sequences must be non-empty")
        if len(seq1) > 500 or len(seq2) > 500:
            raise ValueError("Sequences must be at most 500 bp for the demo budget")
        if (len(seq1) + len(seq2)) * 3 > self.max_qubits:
            raise ValueError(f"Sequence length exceeds qubit budget ({self.max_qubits} qubits)")
        return seq1, seq2

    def _init_matrices(self, n: int, m: int) -> Tuple[np.ndarray, np.ndarray]:
        scores = np.zeros((n + 1, m + 1))
        traceback = np.zeros((n + 1, m + 1), dtype=int)  # 0 diag, 1 up, 2 left
        for i in range(1, n + 1):
            scores[i, 0] = i * self.gap_penalty
            traceback[i, 0] = 1
        for j in range(1, m + 1):
            scores[0, j] = j * self.gap_penalty
            traceback[0, j] = 2
        return scores, traceback

    def _traceback(self, traceback: np.ndarray, seq1: str, seq2: str) -> Tuple[str, str, str]:
        aligned1: List[str] = []
        aligned2: List[str] = []
        path: List[str] = []
        i, j = len(seq1), len(seq2)
        while i > 0 or j > 0:
            move = traceback[i, j]
            if move == 0:
                aligned1.append(seq1[i - 1])
                aligned2.append(seq2[j - 1])
                path.append("E" if seq1[i - 1] == seq2[j - 1] else "I")
                i -= 1
                j -= 1
            elif move == 1:  # up => gap in seq2
                aligned1.append(seq1[i - 1])
                aligned2.append("-")
                path.append("I")
                i -= 1
            else:  # left => gap in seq1
                aligned1.append("-")
                aligned2.append(seq2[j - 1])
                path.append("I")
                j -= 1
        return "".join(reversed(aligned1)), "".join(reversed(aligned2)), "".join(reversed(path))

    def _fill(self, seq1: str, seq2: str) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
        n, m = len(seq1), len(seq2)
        scores, traceback = self._init_matrices(n, m)
        history: List[Dict] = []
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                match = scores[i - 1, j - 1] + (self.match_score if seq1[i - 1] == seq2[j - 1] else self.mismatch_penalty)
                delete = scores[i - 1, j] + self.gap_penalty
                insert = scores[i, j - 1] + self.gap_penalty
                best = max(match, delete, insert)
                scores[i, j] = best
                if best == match:
                    traceback[i, j] = 0
                elif best == delete:
                    traceback[i, j] = 1
                else:
                    traceback[i, j] = 2
            # After each row, capture an energy-like metric: negative of best score so far
            history.append({"iteration": i, "energy": float(-scores[i, :].max())})
        return scores, traceback, history

    def align_windowed(self, seq1: str, seq2: str, window_size: int = 100, overlap: int = 20) -> Dict:
        """Align long sequences using windowing approach."""
        seq1, seq2 = self._validate_inputs(seq1, seq2)
        
        if len(seq1) <= window_size and len(seq2) <= window_size:
            return self.align(seq1, seq2)
        
        all_alignments = []
        all_paths = []
        total_score = 0.0
        
        # Slide windows across sequences
        for start1 in range(0, len(seq1), window_size - overlap):
            end1 = min(start1 + window_size, len(seq1))
            for start2 in range(0, len(seq2), window_size - overlap):
                end2 = min(start2 + window_size, len(seq2))
                
                window_seq1 = seq1[start1:end1]
                window_seq2 = seq2[start2:end2]
                
                result = self.align(window_seq1, window_seq2)
                all_alignments.append({
                    "window": f"({start1}-{end1}, {start2}-{end2})",
                    "score": result["alignment_score"],
                    "length": len(result["alignment_path"]),
                })
                all_paths.append(result["alignment_path"])
                total_score += result["alignment_score"]
        
        avg_score = total_score / max(1, len(all_alignments))
        combined_path = "".join(all_paths)
        
        return {
            "algorithm": "VQE-Windowed",
            "windowed": True,
            "window_size": window_size,
            "overlap": overlap,
            "windows_processed": len(all_alignments),
            "average_score": avg_score,
            "alignment_score": avg_score,
            "final_energy": float(-avg_score),
            "alignment_path": combined_path,
            "convergence": [{"iteration": i, "energy": float(-s["score"])} for i, s in enumerate(all_alignments)],
            "window_results": all_alignments,
        }

    def align(self, seq1: str, seq2: str) -> Dict:
        seq1, seq2 = self._validate_inputs(seq1, seq2)
        scores, traceback, history = self._fill(seq1, seq2)
        score = float(scores[-1, -1])
        aligned1, aligned2, path = self._traceback(traceback, seq1, seq2)
        # Normalize alignment score to 0-100 based on possible extremes
        max_len = max(len(seq1), len(seq2))
        best_possible = max_len * self.match_score
        worst_possible = max_len * self.gap_penalty
        normalized = (score - worst_possible) / (best_possible - worst_possible)
        alignment_score = float(max(0.0, min(1.0, normalized)) * 100.0)
        final_energy = float(-score)
        return {
            "final_energy": final_energy,
            "alignment_score": alignment_score,
            "alignment_score_raw": score,
            "aligned_sequence1": aligned1,
            "aligned_sequence2": aligned2,
            "alignment_path": path,
            "convergence": history,
            "qubits": (len(seq1) + len(seq2)) * 3,
        }
