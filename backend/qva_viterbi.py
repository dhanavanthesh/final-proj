"""
Quantum Viterbi Algorithm (QVA) Implementation
Uses Qiskit for quantum circuit simulation to decode DNA sequences
"""

import numpy as np
import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer
from .hmm_models import base_to_int, validate_sequence


def encode_dna_2qubit(base: str) -> str:
    """
    2-qubit basis encoding as specified in QGENOME PDF

    Args:
        base: DNA nucleotide (A, C, G, or T)

    Returns:
        2-qubit basis state string (e.g., '00', '01', '10', '11')
    """
    mapping = {
        'A': '00',
        'C': '01',
        'G': '10',
        'T': '11'
    }
    return mapping[base.upper()]


def build_qva_circuit(observations: str, hmm_config: dict, time_step: int, current_probs: np.ndarray) -> QuantumCircuit:
    """
    Build quantum circuit for one time step of Viterbi decoding

    Args:
        observations: DNA sequence
        hmm_config: HMM configuration
        time_step: Current time step index
        current_probs: Current state probabilities

    Returns:
        QuantumCircuit for this time step
    """
    n_states = hmm_config['n_states']
    emit_prob = hmm_config['emit_prob']

    # Create quantum circuit (n_states qubits)
    qc = QuantumCircuit(n_states, n_states)

    # Step 1: Initialize state superposition based on current probabilities
    for s in range(n_states):
        # Use RY rotation to encode probability amplitude
        # angle = 2 * arcsin(sqrt(p))
        prob = current_probs[s]
        # Ensure probability is valid
        prob = max(0.0, min(1.0, prob))
        angle = 2 * np.arcsin(np.sqrt(prob))
        qc.ry(angle, s)

    # Step 2: Apply emission probability for observed nucleotide
    obs_idx = base_to_int(observations[time_step])

    for s in range(n_states):
        # Encode emission probability as RZ rotation
        emission_prob = emit_prob[s][obs_idx]
        # Ensure valid probability
        emission_prob = max(0.01, min(0.99, emission_prob))
        # Convert to angle
        theta = np.arccos(2 * emission_prob - 1)
        qc.rz(theta, s)

    # Step 3: Measure all qubits
    qc.measure(range(n_states), range(n_states))

    return qc


def run_quantum_viterbi(sequence: str, hmm_config: dict, shots: int = 1024) -> dict:
    """
    Run Quantum Viterbi Algorithm for DNA sequence decoding

    Uses iterative trellis-based simulation to limit qubit usage

    Args:
        sequence: DNA sequence string (A, C, G, T)
        hmm_config: HMM configuration dictionary
        shots: Number of measurement shots per time step

    Returns:
        Dictionary containing:
        - decoded_path: List of hidden states
        - decoded_path_string: String representation
        - runtime_ms: Execution time in milliseconds
        - method: 'quantum'
        - qubits_used: Number of qubits
        - circuit_depth: Average circuit depth
        - total_shots: Total measurements performed
    """
    # Validate and clean sequence
    cleaned_seq = validate_sequence(sequence)

    # Start timer
    start_time = time.perf_counter()

    # Extract HMM parameters
    n_states = hmm_config['n_states']
    states = hmm_config['states']
    start_prob = hmm_config['start_prob']
    trans_prob = hmm_config['trans_prob']

    # Initialize current state probabilities
    current_probs = np.array(start_prob, dtype=float)

    # Decoded path
    decoded_path = []

    # Get quantum simulator
    simulator = AerSimulator()

    # Circuit depth tracking
    total_depth = 0

    # Iterate through each position in the sequence
    for t in range(len(cleaned_seq)):
        # Build quantum circuit for this time step
        qc = build_qva_circuit(cleaned_seq, hmm_config, t, current_probs)

        # Track circuit depth
        total_depth += qc.depth()

        # Transpile circuit
        transpiled_qc = transpile(qc, simulator)

        # Execute circuit
        job = simulator.run(transpiled_qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        # Get most likely state from measurement results
        most_likely_bitstring = max(counts, key=counts.get)

        # Convert bitstring to state index
        # For 2-state HMM: '00' or '01' -> 0, '10' or '11' -> 1
        # Count number of '1' bits and take modulo n_states
        state_idx = sum(int(bit) for bit in most_likely_bitstring) % n_states

        # Append to decoded path
        decoded_path.append(state_idx)

        # Update probabilities for next time step using transition matrix
        current_probs = trans_prob[state_idx].copy()

    # Convert state indices to state labels
    decoded_path_labels = [states[idx] for idx in decoded_path]
    decoded_path_string = ''.join(decoded_path_labels)

    # End timer
    end_time = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    # Calculate average circuit depth
    avg_depth = total_depth / len(cleaned_seq) if len(cleaned_seq) > 0 else 0

    return {
        'decoded_path': decoded_path_labels,
        'decoded_path_string': decoded_path_string,
        'runtime_ms': round(runtime_ms, 2),
        'method': 'quantum',
        'qubits_used': n_states,
        'circuit_depth': round(avg_depth, 2),
        'total_shots': shots * len(cleaned_seq),
        'sequence_length': len(cleaned_seq),
        'n_states': n_states,
        'algorithm': 'Quantum Viterbi Algorithm (QVA)',
        'simulator': 'Qiskit Aer'
    }


def generate_circuit_diagram(sequence: str, hmm_config: dict, time_step: int = 0) -> str:
    """
    Generate quantum circuit diagram for visualization

    Args:
        sequence: DNA sequence
        hmm_config: HMM configuration
        time_step: Which time step to visualize

    Returns:
        Circuit diagram as string
    """
    # Validate sequence
    cleaned_seq = validate_sequence(sequence)

    if time_step >= len(cleaned_seq):
        time_step = 0

    # Build circuit for specified time step
    current_probs = np.array(hmm_config['start_prob'], dtype=float)
    qc = build_qva_circuit(cleaned_seq, hmm_config, time_step, current_probs)

    # Generate text-based circuit diagram
    circuit_str = str(qc.draw(output='text'))

    return circuit_str


def batch_quantum_viterbi(sequences: list, hmm_config: dict, shots: int = 1024) -> list:
    """
    Run quantum Viterbi on multiple sequences

    Args:
        sequences: List of DNA sequence strings
        hmm_config: HMM configuration
        shots: Number of shots per measurement

    Returns:
        List of result dictionaries
    """
    results = []

    for idx, seq in enumerate(sequences):
        try:
            result = run_quantum_viterbi(seq, hmm_config, shots)
            result['sequence_id'] = idx
            results.append(result)
        except Exception as e:
            results.append({
                'sequence_id': idx,
                'error': str(e),
                'method': 'quantum'
            })

    return results


if __name__ == "__main__":
    # Test the Quantum Viterbi implementation
    from hmm_models import get_hmm_config

    # Test sequence
    test_sequence = "ATGCCTACGCATGCTA"

    # Get HMM configuration
    hmm_config = get_hmm_config("2-state-exon-intron")

    # Run Quantum Viterbi
    print("Running Quantum Viterbi Algorithm...")
    result = run_quantum_viterbi(test_sequence, hmm_config, shots=1024)

    print("\nQuantum Viterbi Test Results:")
    print(f"Input sequence: {test_sequence}")
    print(f"Decoded path: {result['decoded_path_string']}")
    print(f"Runtime: {result['runtime_ms']:.2f} ms")
    print(f"Qubits used: {result['qubits_used']}")
    print(f"Circuit depth: {result['circuit_depth']:.2f}")
    print(f"Total shots: {result['total_shots']}")

    # Generate circuit diagram
    print("\nQuantum Circuit Diagram (first time step):")
    circuit_diagram = generate_circuit_diagram(test_sequence, hmm_config, time_step=0)
    print(circuit_diagram)
