"""
MongoDB models and schemas for QGENOME project
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of a processing job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AlgorithmType(str, Enum):
    """Types of algorithms available"""
    VQE_ALIGNMENT = "vqe_alignment"
    QAOA_MOTIF = "qaoa_motif"
    QCNN_VARIANT = "qcnn_variant"
    SMITH_WATERMAN = "smith_waterman"
    BLAST = "blast"
    CLASSICAL_VITERBI = "classical_viterbi"
    QUANTUM_VITERBI = "quantum_viterbi"


class ProcessingStep(BaseModel):
    """Individual processing step with timing and details"""
    step_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    status: str = "completed"
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Dataset(BaseModel):
    """Dataset storage model"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    sequences: List[str]
    sequence_metadata: Optional[List[Dict[str, Any]]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProcessingJob(BaseModel):
    """Processing job with full traceability"""
    id: Optional[str] = None
    job_name: str
    algorithm: AlgorithmType
    status: ProcessingStatus = ProcessingStatus.PENDING
    
    # Input data
    input_sequences: List[str]
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing tracking
    processing_steps: List[ProcessingStep] = Field(default_factory=list)
    
    # Results
    result: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Quantum specifics
    quantum_circuit_depth: Optional[int] = None
    quantum_shots: Optional[int] = None
    backend_name: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SequenceAnalysis(BaseModel):
    """Individual sequence analysis result"""
    id: Optional[str] = None
    sequence: str
    sequence_length: int
    gc_content: Optional[float] = None
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
