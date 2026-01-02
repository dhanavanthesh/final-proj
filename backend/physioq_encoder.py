import math
from typing import List, Tuple

VALID_BASES = {"A", "T", "G", "C"}


class PhysioQEncoder:
    """PhysioQ: biologically informed 3-qubit-per-base encoding."""

    hydrogen_angles = {
        "A": math.pi / 3,  # 2 bonds
        "T": math.pi / 3,  # 2 bonds
        "G": math.pi / 2,  # 3 bonds
        "C": math.pi / 2,  # 3 bonds,
    }

    def validate(self, seq: str) -> str:
        normalized = seq.strip().upper()
        invalid = [b for b in normalized if b not in VALID_BASES]
        if invalid:
            raise ValueError(f"Invalid bases found: {sorted(set(invalid))}")
        return normalized

    def encode_sequence(self, seq: str, start_qubit: int = 0) -> Tuple[List[tuple], int]:
        seq = self.validate(seq)
        ops: List[tuple] = []
        for i, base in enumerate(seq):
            q = start_qubit + i * 3
            # Qubit 0: chemical class (purine/pyrimidine)
            if base in {"C", "T"}:
                ops.append(("PauliX", q))
            # Qubit 1: hydrogen bonding strength
            theta = self.hydrogen_angles[base]
            ops.append(("RY", q + 1, theta))
            # Qubit 2: base identity marker
            if base in {"G", "T"}:
                ops.append(("PauliX", q + 2))
        return ops, len(seq) * 3
