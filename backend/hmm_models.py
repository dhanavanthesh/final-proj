"""
HMM Model Configurations for QGENOME
Defines transition and emission probability matrices for DNA sequence analysis
"""

import numpy as np

# HMM model configurations for different genomic structures
HMM_CONFIGS = {
    "2-state-exon-intron": {
        "name": "2-State: Exon/Intron",
        "description": "Basic model for exon and intron regions",
        "states": ["E", "I"],  # Exon, Intron
        "n_states": 2,

        # Initial state probabilities
        "start_prob": np.array([0.5, 0.5]),

        # Transition probabilities: [from_state][to_state]
        # E→E: 0.9, E→I: 0.1
        # I→E: 0.2, I→I: 0.8
        "trans_prob": np.array([
            [0.9, 0.1],  # From Exon
            [0.2, 0.8]   # From Intron
        ]),

        # Emission probabilities: [state][nucleotide]
        # Nucleotide order: A, C, G, T (0, 1, 2, 3)
        "emit_prob": np.array([
            [0.3, 0.2, 0.3, 0.2],  # Exon: slightly GC-rich
            [0.25, 0.25, 0.25, 0.25]  # Intron: uniform distribution
        ])
    },

    "3-state-promoter-exon-intron": {
        "name": "3-State: Promoter/Exon/Intron",
        "description": "Extended model including promoter regions",
        "states": ["P", "E", "I"],  # Promoter, Exon, Intron
        "n_states": 3,

        # Initial state probabilities
        "start_prob": np.array([0.1, 0.5, 0.4]),

        # Transition probabilities: [from_state][to_state]
        # P→P, P→E, P→I
        # E→P, E→E, E→I
        # I→P, I→E, I→I
        "trans_prob": np.array([
            [0.7, 0.25, 0.05],  # From Promoter
            [0.05, 0.85, 0.1],  # From Exon
            [0.1, 0.2, 0.7]     # From Intron
        ]),

        # Emission probabilities
        "emit_prob": np.array([
            [0.2, 0.3, 0.3, 0.2],   # Promoter: GC-rich
            [0.3, 0.2, 0.3, 0.2],   # Exon: slightly GC-rich
            [0.25, 0.25, 0.25, 0.25]  # Intron: uniform
        ])
    }
}


def get_hmm_config(model_name: str) -> dict:
    """
    Get HMM configuration by name

    Args:
        model_name: Name of the HMM model

    Returns:
        Dictionary containing HMM parameters

    Raises:
        ValueError: If model name not found
    """
    if model_name not in HMM_CONFIGS:
        available = list(HMM_CONFIGS.keys())
        raise ValueError(f"Unknown HMM model: {model_name}. Available: {available}")

    return HMM_CONFIGS[model_name]


def list_available_models() -> list:
    """
    Get list of available HMM models

    Returns:
        List of model names with descriptions
    """
    return [
        {
            "id": key,
            "name": config["name"],
            "description": config["description"],
            "n_states": config["n_states"]
        }
        for key, config in HMM_CONFIGS.items()
    ]


def base_to_int(base: str) -> int:
    """
    Convert DNA base to integer index

    Args:
        base: DNA nucleotide (A, C, G, or T)

    Returns:
        Integer index (0-3)

    Raises:
        ValueError: If base is not valid
    """
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    base_upper = base.upper()

    if base_upper not in mapping:
        raise ValueError(f"Invalid nucleotide: {base}. Must be A, C, G, or T")

    return mapping[base_upper]


def int_to_base(index: int) -> str:
    """
    Convert integer index to DNA base

    Args:
        index: Integer (0-3)

    Returns:
        DNA nucleotide character
    """
    mapping = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
    return mapping[index]


def validate_sequence(sequence: str) -> str:
    """
    Validate and clean DNA sequence

    Args:
        sequence: DNA sequence string

    Returns:
        Cleaned uppercase sequence

    Raises:
        ValueError: If sequence contains invalid characters
    """
    # Remove whitespace and convert to uppercase
    cleaned = sequence.replace('\n', '').replace(' ', '').upper()

    # Check for invalid characters
    valid_bases = set('ACGT')
    invalid_bases = set(cleaned) - valid_bases

    if invalid_bases:
        raise ValueError(f"Sequence contains invalid nucleotides: {invalid_bases}")

    # Check length
    if len(cleaned) == 0:
        raise ValueError("Sequence is empty")

    if len(cleaned) > 500:
        raise ValueError(f"Sequence too long ({len(cleaned)} bases). Maximum: 500 bases")

    return cleaned
