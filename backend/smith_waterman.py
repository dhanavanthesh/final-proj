from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple
from .physioq_encoder import PhysioQEncoder


class SmithWaterman:
    """Smith-Waterman local sequence alignment algorithm."""

    def __init__(self):
        self.encoder = PhysioQEncoder()
        self.match_score = 2.0
        self.mismatch_penalty = -1.0
        self.gap_penalty = -2.0

    def _validate_inputs(self, seq1: str, seq2: str) -> Tuple[str, str]:
        seq1 = self.encoder.validate(seq1)
        seq2 = self.encoder.validate(seq2)
        if len(seq1) == 0 or len(seq2) == 0:
            raise ValueError("Sequences must be non-empty")
        return seq1, seq2

    def _init_matrices(self, n: int, m: int) -> Tuple[np.ndarray, np.ndarray]:
        scores = np.zeros((n + 1, m + 1))
        traceback = np.zeros((n + 1, m + 1), dtype=int)
        return scores, traceback

    def _traceback(self, traceback: np.ndarray, seq1: str, seq2: str, start_i: int, start_j: int) -> Tuple[str, str, str]:
        aligned1: List[str] = []
        aligned2: List[str] = []
        path: List[str] = []
        i, j = start_i, start_j
        while i > 0 and j > 0 and traceback[i, j] != 0:
            move = traceback[i, j]
            if move == 0:  # diagonal
                aligned1.append(seq1[i - 1])
                aligned2.append(seq2[j - 1])
                path.append("E" if seq1[i - 1] == seq2[j - 1] else "I")
                i -= 1
                j -= 1
            elif move == 1:  # up
                aligned1.append(seq1[i - 1])
                aligned2.append("-")
                path.append("I")
                i -= 1
            else:  # left
                aligned1.append("-")
                aligned2.append(seq2[j - 1])
                path.append("I")
                j -= 1
        return "".join(reversed(aligned1)), "".join(reversed(aligned2)), "".join(reversed(path))

    def align(self, seq1: str, seq2: str) -> Dict:
        seq1, seq2 = self._validate_inputs(seq1, seq2)
        n, m = len(seq1), len(seq2)
        scores, traceback = self._init_matrices(n, m)

        max_score = 0.0
        max_i, max_j = 0, 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                match = scores[i - 1, j - 1] + (self.match_score if seq1[i - 1] == seq2[j - 1] else self.mismatch_penalty)
                delete = scores[i - 1, j] + self.gap_penalty
                insert = scores[i, j - 1] + self.gap_penalty
                best = max(match, delete, insert, 0.0)
                scores[i, j] = best

                if best == 0.0:
                    traceback[i, j] = 0
                elif best == match:
                    traceback[i, j] = 0
                elif best == delete:
                    traceback[i, j] = 1
                else:
                    traceback[i, j] = 2

                if best > max_score:
                    max_score = best
                    max_i, max_j = i, j

        if max_i == 0 or max_j == 0:
            return {
                "algorithm": "Smith-Waterman",
                "score": 0.0,
                "aligned_sequence1": seq1,
                "aligned_sequence2": seq2,
                "alignment_path": "I" * len(seq1),
                "start_position": (0, 0),
                "end_position": (0, 0),
            }

        aligned1, aligned2, path = self._traceback(traceback, seq1, seq2, max_i, max_j)

        return {
            "algorithm": "Smith-Waterman",
            "score": float(max_score),
            "aligned_sequence1": aligned1,
            "aligned_sequence2": aligned2,
            "alignment_path": path,
            "start_position": (max_i, max_j),
            "end_position": (max_i - len(aligned1), max_j - len(aligned2)),
            "query_start": max(0, max_i - len(aligned1)),
            "subject_start": max(0, max_j - len(aligned2)),
        }


class BlastLike:
    """BLAST-like sequence similarity search."""

    def __init__(self, word_size: int = 11):
        self.encoder = PhysioQEncoder()
        self.word_size = word_size
        self.smith_waterman = SmithWaterman()

    def _generate_words(self, seq: str) -> Dict[str, List[int]]:
        words = {}
        for i in range(len(seq) - self.word_size + 1):
            word = seq[i : i + self.word_size]
            if word not in words:
                words[word] = []
            words[word].append(i)
        return words

    def search(self, query: str, database: List[str], top_k: int = 5) -> List[Dict]:
        query = self.encoder.validate(query)
        database = [self.encoder.validate(seq) for seq in database]

        query_words = self._generate_words(query)
        results = []

        for db_seq in database:
            db_words = self._generate_words(db_seq)
            hits = 0
            for word in query_words:
                if word in db_words:
                    hits += len(query_words[word]) * len(db_words[word])

            if hits > 0:
                sw_result = self.smith_waterman.align(query, db_seq)
                results.append({
                    "sequence": db_seq[:50] + "..." if len(db_seq) > 50 else db_seq,
                    "word_matches": hits,
                    "alignment_score": sw_result["score"],
                    "evalue": float(hits) / (len(query) * len(db_seq)),
                })

        results.sort(key=lambda x: x["alignment_score"], reverse=True)
        return results[:top_k]
