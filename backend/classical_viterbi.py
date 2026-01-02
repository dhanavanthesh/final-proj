"""
Classical Viterbi Algorithm Implementation
Uses hmmlearn library for baseline comparison with Quantum Viterbi
"""

import numpy as np
import time
from hmmlearn import hmm
from .hmm_models import base_to_int, validate_sequence


def run_classical_viterbi(sequence: str, hmm_config: dict) -> dict:
    """
    Run classical Viterbi algorithm using hmmlearn

    Args:
        sequence: DNA sequence string (A, C, G, T)
        hmm_config: HMM configuration dictionary from hmm_models.py

    Returns:
        Dictionary containing:
        - decoded_path: List of hidden states (e.g., ['E', 'E', 'I', 'I'])
        - decoded_path_string: String representation (e.g., "EEII")
        - log_probability: Log likelihood of the path
        - runtime_ms: Execution time in milliseconds
        - method: 'classical'
        - sequence_length: Length of input sequence
    """
    # Validate and clean sequence
    cleaned_seq = validate_sequence(sequence)

    # Start timer
    start_time = time.perf_counter()

    # Convert DNA sequence to integer observations
    # A=0, C=1, G=2, T=3
    observations = np.array([[base_to_int(base)] for base in cleaned_seq])

    # Extract HMM parameters
    n_states = hmm_config['n_states']
    states = hmm_config['states']
    start_prob = hmm_config['start_prob']
    trans_prob = hmm_config['trans_prob']
    emit_prob = hmm_config['emit_prob']

    # Create MultinomialHMM model
    model = hmm.MultinomialHMM(n_components=n_states, n_iter=100)

    # Set HMM parameters
    model.startprob_ = start_prob
    model.transmat_ = trans_prob
    model.emissionprob_ = emit_prob

    # Run Viterbi decoding
    log_probability, hidden_states = model.decode(observations, algorithm='viterbi')

    # Convert state indices to state labels
    decoded_path = [states[int(state)] for state in hidden_states]
    decoded_path_string = ''.join(decoded_path)

    # End timer
    end_time = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000  # Convert to milliseconds

    return {
        'decoded_path': decoded_path,
        'decoded_path_string': decoded_path_string,
        'log_probability': float(log_probability),
        'runtime_ms': round(runtime_ms, 2),
        'method': 'classical',
        'sequence_length': len(cleaned_seq),
        'n_states': n_states,
        'algorithm': 'Viterbi (Dynamic Programming)'
    }


def compare_with_ground_truth(decoded_path: list, ground_truth: list) -> dict:
    """
    Compare decoded path with ground truth (if available)

    Args:
        decoded_path: List of predicted states
        ground_truth: List of true states

    Returns:
        Dictionary with accuracy metrics
    """
    if len(decoded_path) != len(ground_truth):
        raise ValueError("Decoded path and ground truth must have same length")

    correct = sum(1 for pred, true in zip(decoded_path, ground_truth) if pred == true)
    total = len(decoded_path)
    accuracy = (correct / total) * 100

    return {
        'accuracy_percent': round(accuracy, 2),
        'correct_predictions': correct,
        'total_positions': total,
        'mismatches': total - correct
    }


def batch_classical_viterbi(sequences: list, hmm_config: dict) -> list:
    """
    Run classical Viterbi on multiple sequences

    Args:
        sequences: List of DNA sequence strings
        hmm_config: HMM configuration

    Returns:
        List of result dictionaries
    """
    results = []

    for idx, seq in enumerate(sequences):
        try:
            result = run_classical_viterbi(seq, hmm_config)
            result['sequence_id'] = idx
            results.append(result)
        except Exception as e:
            results.append({
                'sequence_id': idx,
                'error': str(e),
                'method': 'classical'
            })

    return results


if __name__ == "__main__":
    # Test the classical Viterbi implementation
    from hmm_models import get_hmm_config

    # Test sequence
    test_sequence = "ATGCCTACGCATGCTAGCTAGCTAGCTA"

    # Get HMM configuration
    hmm_config = get_hmm_config("2-state-exon-intron")

    # Run classical Viterbi
    result = run_classical_viterbi(test_sequence, hmm_config)

    print("Classical Viterbi Test Results:")
    print(f"Input sequence: {test_sequence}")
    print(f"Decoded path: {result['decoded_path_string']}")
    print(f"Log probability: {result['log_probability']:.4f}")
    print(f"Runtime: {result['runtime_ms']:.2f} ms")
    print(f"Sequence length: {result['sequence_length']} bases")
