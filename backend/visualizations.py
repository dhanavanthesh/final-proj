from __future__ import annotations
import numpy as np
from typing import Dict, List


class VisualizationGenerator:
    """Generate data for 3D helix and circuit diagram visualizations."""

    @staticmethod
    def generate_helix_coordinates(sequence: str, radius: float = 1.0, with_complementary: bool = True) -> Dict:
        """Generate 3D coordinates for DNA helix visualization with hydrogen bonds.

        Args:
            sequence: DNA sequence (A, T, G, C)
            radius: Helix radius in coordinate units
            with_complementary: Include complementary strand and hydrogen bonds

        Returns:
            Dictionary with 3D coordinates, base colors, and hydrogen bonds
        """
        base_colors = {"A": "#FF6B6B", "T": "#4ECDC4", "G": "#45B7D1", "C": "#FFA07A"}
        complement_map = {"A": "T", "T": "A", "G": "C", "C": "G"}

        bases = []
        hydrogen_bonds = []

        for i, base in enumerate(sequence):
            angle = (i / len(sequence)) * 4 * np.pi  # Two full rotations per strand
            height = i * 0.34  # DNA rise: 0.34 nm per base pair
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = height

            bases.append({
                "position": [float(x), float(y), float(z)],
                "base": base,
                "color": base_colors.get(base, "#888888"),
                "index": i,
                "strand": 1
            })

            # Generate complementary strand with hydrogen bonds
            if with_complementary:
                comp_base = complement_map.get(base, "A")
                # Complementary strand is on opposite side
                comp_x = -radius * np.cos(angle)
                comp_y = -radius * np.sin(angle)
                comp_z = height

                bases.append({
                    "position": [float(comp_x), float(comp_y), float(comp_z)],
                    "base": comp_base,
                    "color": base_colors.get(comp_base, "#888888"),
                    "index": i,
                    "strand": 2
                })

                # Hydrogen bonds connect base pairs
                # A-T has 2 hydrogen bonds, G-C has 3 hydrogen bonds
                if base in ['A', 'T']:
                    bond_strength = 2
                else:  # G-C pair
                    bond_strength = 3

                hydrogen_bonds.append({
                    "from": [float(x), float(y), float(z)],
                    "to": [float(comp_x), float(comp_y), float(comp_z)],
                    "strength": bond_strength,
                    "bases": f"{base}-{comp_base}",
                    "index": i
                })

        # Generate sugar-phosphate backbone (both strands)
        backbone = []
        for i in range(0, len(sequence), 3):
            angle = (i / len(sequence)) * 4 * np.pi
            height = i * 0.34
            # Strand 1 backbone
            backbone.append({
                "x": float(radius * 0.5 * np.cos(angle)),
                "y": float(radius * 0.5 * np.sin(angle)),
                "z": float(height),
            })
            # Strand 2 backbone (if complementary enabled)
            if with_complementary:
                backbone.append({
                    "x": float(-radius * 0.5 * np.cos(angle)),
                    "y": float(-radius * 0.5 * np.sin(angle)),
                    "z": float(height),
                })

        result = {
            "bases": bases,
            "hydrogen_bonds": hydrogen_bonds if with_complementary else [],
            "backbone": backbone,
            "sequence_length": len(sequence),
            "helical_turn": len(sequence) / 10.5,  # B-form DNA: 10.5 bp per turn
            "with_complementary": with_complementary
        }

        return result

    @staticmethod
    def generate_circuit_diagram(sequence: str, algorithm: str = "vqe") -> Dict:
        """Generate quantum circuit representation for visualization.
        
        Args:
            sequence: DNA sequence
            algorithm: Algorithm type (vqe, qaoa, qcnn)
            
        Returns:
            Dictionary with circuit gates and topology
        """
        num_qubits = len(sequence) * 3
        gates = []
        
        if algorithm == "vqe":
            # VQE circuit: encode -> parameterized rotations -> measure
            gates.append({"type": "encoding", "qubits": list(range(num_qubits)), "label": "PhysioQ Encode"})
            for i in range(0, num_qubits, 3):
                gates.append({"type": "ry", "qubits": [i + 1], "angle": f"θ_{i//3}", "label": f"H-Bond"})
            gates.append({"type": "measurement", "qubits": list(range(num_qubits)), "label": "Measure"})
        
        elif algorithm == "qaoa":
            # QAOA circuit: encode -> cost -> mixer -> repeat -> measure
            gates.append({"type": "encoding", "qubits": list(range(min(num_qubits, 20))), "label": "Encode"})
            for p in range(2):
                gates.append({"type": "cost", "qubits": list(range(min(num_qubits, 20))), "label": f"Cost(γ_{p})"})
                gates.append({"type": "mixer", "qubits": list(range(min(num_qubits, 20))), "label": f"Mixer(β_{p})"})
            gates.append({"type": "measurement", "qubits": list(range(min(num_qubits, 20))), "label": "Measure"})
        
        elif algorithm == "qcnn":
            # QCNN circuit: encode -> convolution -> pooling -> classifier
            current_qubits = num_qubits
            layer = 0
            while current_qubits > 1:
                gates.append({"type": "conv", "qubits": list(range(min(current_qubits, 12))), "label": f"Conv_{layer}"})
                gates.append({"type": "pool", "qubits": list(range(min(current_qubits // 2, 6))), "label": f"Pool_{layer}"})
                current_qubits = current_qubits // 2
                layer += 1
            gates.append({"type": "classifier", "qubits": [0], "label": "Classify"})
            gates.append({"type": "measurement", "qubits": [0], "label": "Measure"})
        
        return {
            "algorithm": algorithm,
            "num_qubits": num_qubits,
            "gates": gates,
            "depth": len(gates),
            "sequence_length": len(sequence),
        }

    @staticmethod
    def generate_alignment_visualization(aligned_seq1: str, aligned_seq2: str, path: str) -> Dict:
        """Generate alignment visualization data.
        
        Args:
            aligned_seq1: First aligned sequence
            aligned_seq2: Second aligned sequence
            path: Alignment path (E for match, I for mismatch)
            
        Returns:
            Dictionary with visualization segments
        """
        segments = []
        color_map = {"E": "#4ECDC4", "I": "#FF6B6B"}  # Match/Mismatch colors
        
        current_color = None
        current_start = 0
        
        for i, p in enumerate(path):
            if current_color is None:
                current_color = p
                current_start = i
            elif p != current_color:
                segments.append({
                    "type": "E" if current_color == "E" else "I",
                    "start": current_start,
                    "end": i,
                    "length": i - current_start,
                    "color": color_map[current_color],
                    "label": "Match" if current_color == "E" else "Mismatch",
                })
                current_color = p
                current_start = i
        
        segments.append({
            "type": "E" if current_color == "E" else "I",
            "start": current_start,
            "end": len(path),
            "length": len(path) - current_start,
            "color": color_map[current_color],
            "label": "Match" if current_color == "E" else "Mismatch",
        })
        
        return {
            "segments": segments,
            "total_length": len(path),
            "match_count": path.count("E"),
            "mismatch_count": path.count("I"),
            "identity": (path.count("E") / len(path)) * 100,
        }
