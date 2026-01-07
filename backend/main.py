from __future__ import annotations
import os
import random
from typing import List, Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .physioq_encoder import PhysioQEncoder
from .vqe_alignment import VQEAlignment
from .qaoa_motif import QAOAMotifFinder
from .qcnn_variant import QCNNVariantDetector
from .smith_waterman import SmithWaterman, BlastLike
from .visualizations import VisualizationGenerator
from .db import connect_to_mongo, close_mongo_connection, save_run, fetch_runs, get_run_by_id, update_run as db_update_run, delete_run as db_delete_run

# Import MongoDB operations for datasets and processing jobs
from .mongo_operations import (
    save_dataset, get_dataset, list_datasets, delete_dataset,
    create_processing_job, get_processing_job, list_processing_jobs,
    update_processing_job, add_processing_step
)
from .models import Dataset, ProcessingJob, ProcessingStatus, AlgorithmType, ProcessingStep
from .processing_logger import create_job_logger

# Import Viterbi modules (Core QVA functionality)
from .hmm_models import get_hmm_config, list_available_models
from .classical_viterbi import run_classical_viterbi
from .qva_viterbi import run_quantum_viterbi, generate_circuit_diagram

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(title="QGENOME API", version="1.1", lifespan=lifespan)

cors_origins_env = os.getenv("CORS_ORIGINS")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()] if cors_origins_env else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

encoder = PhysioQEncoder()
vqe_engine = VQEAlignment()
qaoa_engine = QAOAMotifFinder()
qcnn_engine = QCNNVariantDetector()
smith_waterman = SmithWaterman()
blast_engine = BlastLike()
viz_generator = VisualizationGenerator()


def _generate_sample_sequences(length: int = 80) -> dict:
    bases = ["A", "C", "G", "T"]
    motif = "ATGCGT"
    def synth() -> str:
        start = random.randint(0, length - len(motif))
        seq = [random.choice(bases) for _ in range(length)]
        seq[start : start + len(motif)] = list(motif)
        return "".join(seq)
    return {"sequence1": synth(), "sequence2": synth()}


class EncodeRequest(BaseModel):
    sequence: str = Field(..., json_schema_extra={"example": "ATGC"})


class AlignRequest(BaseModel):
    sequence1: str = Field(..., json_schema_extra={"example": "ATGC"})
    sequence2: str = Field(..., json_schema_extra={"example": "ATCC"})


class MotifRequest(BaseModel):
    sequences: List[str]
    motif_length: int = 6


class VariantRequest(BaseModel):
    sequence: str


class RunUpdate(BaseModel):
    score: Optional[float] = None
    result: Optional[dict] = None


class BatchAlignRequest(BaseModel):
    sequence_pairs: List[dict] = Field(..., json_schema_extra={"example": [{"seq1": "ATGC", "seq2": "ATCC"}]})


class BatchMotifRequest(BaseModel):
    sequences_list: List[List[str]] = Field(..., json_schema_extra={"example": [[["ATGC", "ATCC"], ["ATGC", "ATCC"]]]})
    motif_length: int = 6


class VisualizationRequest(BaseModel):
    sequence: str
    type: str = Field(..., json_schema_extra={"example": "helix"})  # helix, circuit, alignment


# Dataset request models
class DatasetCreateRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Sample Dataset"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "A collection of DNA sequences"})
    sequences: List[str] = Field(..., json_schema_extra={"example": ["ATGC", "CGTA"]})
    tags: List[str] = Field(default_factory=list, json_schema_extra={"example": ["gene", "exon"]})


class ProcessingJobCreateRequest(BaseModel):
    job_name: str = Field(..., json_schema_extra={"example": "Alignment Job"})
    algorithm: str = Field(..., json_schema_extra={"example": "vqe_alignment"})
    input_sequences: List[str] = Field(..., json_schema_extra={"example": ["ATGC", "CGTA"]})
    input_parameters: dict = Field(default_factory=dict, json_schema_extra={"example": {"shots": 1024}})


# Viterbi-specific request models
class ViterbiRequest(BaseModel):
    sequence: str = Field(..., json_schema_extra={"example": "ATGCCTACGCATGCTA"}, description="DNA sequence (A, C, G, T only)")
    hmm_model: str = Field(default="2-state-exon-intron", json_schema_extra={"example": "2-state-exon-intron"}, description="HMM model to use")
    shots: int = Field(default=1024, json_schema_extra={"example": 1024}, description="Number of quantum shots (quantum only)")
    save_to_db: bool = Field(default=False, description="Save processing details to database")


class CircuitDiagramRequest(BaseModel):
    sequence: str = Field(..., json_schema_extra={"example": "ATGCCTACGCATGCTA"})
    hmm_model: str = Field(default="2-state-exon-intron", json_schema_extra={"example": "2-state-exon-intron"})
    time_step: int = Field(default=0, json_schema_extra={"example": 0}, description="Which time step to visualize")


class ViterbiAnimationRequest(BaseModel):
    sequence: str = Field(..., json_schema_extra={"example": "ATGCCTACGCATGCTA"})
    hmm_model: str = Field(default="2-state-exon-intron", json_schema_extra={"example": "2-state-exon-intron"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/samples")
def samples():
    return _generate_sample_sequences()


@app.get("/runs")
async def get_runs(limit: int = 10, run_type: Optional[str] = None):
    runs = await fetch_runs(run_type=run_type, limit=min(limit, 50))
    return [
        {
            "id": run.id,
            "run_type": run.run_type,
            "sequence_a": run.sequence_a,
            "sequence_b": run.sequence_b,
            "score": run.score,
            "created_at": run.created_at.isoformat(),
            "result": run.result,  # Already a dict, no json.loads needed
        }
        for run in runs
    ]


@app.delete("/runs/{run_id}")
async def delete_run_endpoint(run_id: str):
    deleted = await db_delete_run(run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"deleted": run_id}


@app.patch("/runs/{run_id}")
async def update_run_endpoint(run_id: str, payload: RunUpdate):
    updated_run = await db_update_run(run_id, score=payload.score, result=payload.result)
    if not updated_run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": updated_run.id,
        "score": updated_run.score,
        "result": updated_run.result,  # Already a dict
    }


@app.post("/encode")
def encode(req: EncodeRequest):
    try:
        ops, qubits = encoder.encode_sequence(req.sequence)
        return {"operations": ops, "qubits": qubits}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/align")
async def align(req: AlignRequest):
    """
    Align two sequences using VQE algorithm with optional processing logging
    """
    logger = create_job_logger("VQE_Alignment")
    job_id = None
    
    try:
        # Start processing
        logger.start_step("Input Validation", {"seq1_length": len(req.sequence1), "seq2_length": len(req.sequence2)})
        
        # Create processing job in database (if needed for tracking)
        job = await create_processing_job(
            job_name=f"VQE Alignment: {req.sequence1[:10]}... vs {req.sequence2[:10]}...",
            algorithm=AlgorithmType.VQE_ALIGNMENT,
            input_sequences=[req.sequence1, req.sequence2],
            input_parameters={}
        )
        job_id = job.id
        
        await update_processing_job(job_id, status=ProcessingStatus.RUNNING)
        logger.end_step("completed", {"job_id": job_id})
        
        # Run alignment
        logger.start_step("VQE Circuit Construction")
        result = vqe_engine.align(req.sequence1, req.sequence2)
        logger.end_step("completed", {"alignment_score": result.get("alignment_score")})
        
        # Save to database
        logger.start_step("Database Storage")
        await save_run("align", req.sequence1, req.sequence2, result["alignment_score"], result)
        
        # Update job with results
        await update_processing_job(
            job_id,
            status=ProcessingStatus.COMPLETED,
            result=result,
            score=result["alignment_score"],
            processing_steps=logger.get_steps()
        )
        logger.end_step("completed")
        
        return {
            "algorithm": "VQE",
            "results": result,
            "job_id": job_id,
            "processing_summary": logger.get_summary()
        }
    except ValueError as exc:
        if job_id:
            await update_processing_job(job_id, status=ProcessingStatus.FAILED, error_message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        if job_id:
            await update_processing_job(job_id, status=ProcessingStatus.FAILED, error_message=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/find-motifs")
async def find_motifs(req: MotifRequest):
    try:
        result = qaoa_engine.find_motif(req.sequences, req.motif_length)
        await save_run("motif", req.sequences[0], req.sequences[1] if len(req.sequences) > 1 else None, result["score"], result)
        return {"algorithm": "QAOA", "results": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/detect-variant")
async def detect_variant(req: VariantRequest):
    try:
        result = qcnn_engine.predict(req.sequence)
        await save_run("variant", req.sequence, None, result["pathogenic_probability"], result)
        return {"algorithm": "QCNN", "results": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/smith-waterman")
def sw_align(req: AlignRequest):
    try:
        result = smith_waterman.align(req.sequence1, req.sequence2)
        return {"algorithm": "Smith-Waterman", "results": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/blast-search")
def blast_search(req: MotifRequest):
    try:
        if len(req.sequences) < 2:
            raise ValueError("BLAST search requires query and database sequences")
        query = req.sequences[0]
        database = req.sequences[1:]
        results = blast_engine.search(query, database, top_k=min(5, len(database)))
        return {"algorithm": "BLAST-like", "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/batch-align")
def batch_align(req: BatchAlignRequest):
    try:
        results = []
        for pair in req.sequence_pairs:
            result = vqe_engine.align(pair["seq1"], pair["seq2"])
            results.append(result)
        return {"algorithm": "VQE-Batch", "total": len(results), "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/batch-motif")
def batch_motif(req: BatchMotifRequest):
    try:
        results = []
        for seq_list in req.sequences_list:
            result = qaoa_engine.find_motif(seq_list, req.motif_length)
            results.append(result)
        return {"algorithm": "QAOA-Batch", "total": len(results), "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ============================================================================
# VITERBI ALGORITHM ENDPOINTS (Core QGENOME QVA Functionality)
# ============================================================================

@app.get("/hmm/models")
def get_hmm_models():
    """
    Get list of available HMM models for Viterbi decoding

    Returns:
        List of HMM model configurations
    """
    try:
        models = list_available_models()
        return {"models": models, "total": len(models)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/viterbi/quantum")
async def quantum_viterbi(req: ViterbiRequest):
    """
    Run Quantum Viterbi Algorithm (QVA) for DNA sequence decoding

    This is the CORE functionality specified in QGENOME_FINAL.pdf

    Args:
        req: ViterbiRequest with sequence, hmm_model, and shots

    Returns:
        Decoded hidden state path with quantum metrics
    """
    try:
        # Get HMM configuration
        hmm_config = get_hmm_config(req.hmm_model)

        # Run Quantum Viterbi
        result = run_quantum_viterbi(req.sequence, hmm_config, shots=req.shots)

        # Save to database
        await save_run(
            "viterbi_quantum",
            req.sequence,
            None,
            0.0,  # No specific score for QVA
            result
        )

        return {
            "algorithm": "Quantum Viterbi Algorithm (QVA)",
            "hmm_model": req.hmm_model,
            "results": result
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QVA execution failed: {str(exc)}")


@app.post("/viterbi/classical")
async def classical_viterbi(req: ViterbiRequest):
    """
    Run Classical Viterbi Algorithm for baseline comparison

    Uses hmmlearn library for standard dynamic programming approach

    Args:
        req: ViterbiRequest with sequence and hmm_model

    Returns:
        Decoded hidden state path with classical metrics
    """
    try:
        # Get HMM configuration
        hmm_config = get_hmm_config(req.hmm_model)

        # Run Classical Viterbi
        result = run_classical_viterbi(req.sequence, hmm_config)

        # Save to database
        await save_run(
            "viterbi_classical",
            req.sequence,
            None,
            result['log_probability'],
            result
        )

        return {
            "algorithm": "Classical Viterbi (hmmlearn)",
            "hmm_model": req.hmm_model,
            "results": result
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        # Log the full error for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Classical Viterbi failed: {str(exc)}")


@app.post("/viterbi/compare")
async def compare_viterbi(req: ViterbiRequest):
    """
    Run both Quantum and Classical Viterbi for direct comparison

    Args:
        req: ViterbiRequest with sequence and hmm_model

    Returns:
        Side-by-side comparison of both methods
    """
    try:
        # Get HMM configuration
        hmm_config = get_hmm_config(req.hmm_model)

        # Run both methods
        quantum_result = run_quantum_viterbi(req.sequence, hmm_config, shots=req.shots)
        classical_result = run_classical_viterbi(req.sequence, hmm_config)

        # Calculate agreement
        agreement = sum(
            1 for q, c in zip(quantum_result['decoded_path'], classical_result['decoded_path'])
            if q == c
        )
        agreement_percent = (agreement / len(quantum_result['decoded_path'])) * 100

        return {
            "hmm_model": req.hmm_model,
            "sequence_length": len(req.sequence),
            "quantum": quantum_result,
            "classical": classical_result,
            "comparison": {
                "agreement_percent": round(agreement_percent, 2),
                "matches": agreement,
                "total_positions": len(quantum_result['decoded_path']),
                "runtime_speedup": round(
                    classical_result['runtime_ms'] / quantum_result['runtime_ms'], 2
                ) if quantum_result['runtime_ms'] > 0 else None
            }
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(exc)}")


@app.post("/viterbi/circuit-diagram")
def get_circuit_diagram(req: CircuitDiagramRequest):
    """
    Generate quantum circuit diagram for visualization

    Args:
        req: CircuitDiagramRequest with sequence, hmm_model, and time_step

    Returns:
        Circuit diagram as text
    """
    try:
        hmm_config = get_hmm_config(req.hmm_model)
        diagram = generate_circuit_diagram(req.sequence, hmm_config, req.time_step)

        return {
            "circuit_diagram": diagram,
            "time_step": req.time_step,
            "hmm_model": req.hmm_model
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Circuit diagram generation failed: {str(exc)}")


@app.post("/viterbi/animation-frames")
def get_animation_frames(req: ViterbiAnimationRequest):
    """
    Generate frame-by-frame animation data for Viterbi decoding visualization

    Args:
        req: ViterbiAnimationRequest with sequence and hmm_model

    Returns:
        Animation frames with decoded states for each time step
    """
    try:
        # Validate sequence
        sequence = encoder.validate(req.sequence)
        hmm_config = get_hmm_config(req.hmm_model)

        # State color mapping for visualization
        state_colors = {
            "E": "#4CAF50",  # Exon - Green
            "I": "#FF9800",  # Intron - Orange
            "P": "#2196F3",  # Promoter - Blue
        }

        # Run Viterbi algorithm and collect frames
        result = run_quantum_viterbi(sequence, hmm_config, shots=1024)
        
        # Handle result structure - check for decoded_path in various locations
        decoded_path = result.get("results", {}).get("decoded_path") or result.get("decoded_path") or ""
        if not decoded_path:
            # Fallback: generate default path if decoding failed
            decoded_path = "E" * len(sequence)

        # Generate animation frames
        frames = []
        for time_step in range(len(sequence)):
            state = decoded_path[time_step] if time_step < len(decoded_path) else "E"
            frames.append({
                "step": time_step,
                "current_base": sequence[time_step],
                "decoded_state": state,
                "state_color": state_colors.get(state, "#4CAF50"),
                "cumulative_path": decoded_path[:time_step + 1]
            })

        return {
            "frames": frames,
            "total_steps": len(sequence),
            "hmm_model": req.hmm_model,
            "sequence_length": len(sequence)
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Animation generation failed: {str(exc)}")


# ============================================================================
# DATASET MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/datasets")
async def create_dataset(req: DatasetCreateRequest):
    """Create a new dataset in MongoDB"""
    try:
        dataset = Dataset(
            name=req.name,
            description=req.description,
            sequences=req.sequences,
            tags=req.tags
        )
        
        saved_dataset = await save_dataset(dataset)
        
        return {
            "id": saved_dataset.id,
            "name": saved_dataset.name,
            "description": saved_dataset.description,
            "sequences_count": len(saved_dataset.sequences),
            "created_at": saved_dataset.created_at.isoformat()
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create dataset: {str(exc)}")


@app.get("/datasets")
async def get_datasets(limit: int = 50, skip: int = 0):
    """List all datasets"""
    try:
        datasets = await list_datasets(limit=limit, skip=skip)
        
        return [
            {
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "sequences_count": len(ds.sequences),
                "tags": ds.tags,
                "created_at": ds.created_at.isoformat(),
                "updated_at": ds.updated_at.isoformat()
            }
            for ds in datasets
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch datasets: {str(exc)}")


@app.get("/datasets/{dataset_id}")
async def get_dataset_detail(dataset_id: str):
    """Get dataset details"""
    try:
        dataset = await get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "sequences": dataset.sequences,
            "tags": dataset.tags,
            "created_at": dataset.created_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dataset: {str(exc)}")


@app.delete("/datasets/{dataset_id}")
async def delete_dataset_endpoint(dataset_id: str):
    """Delete a dataset"""
    try:
        deleted = await delete_dataset(dataset_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return {"deleted": dataset_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(exc)}")


# ============================================================================
# PROCESSING JOB ENDPOINTS
# ============================================================================

@app.post("/jobs")
async def create_job(req: ProcessingJobCreateRequest):
    """Create a new processing job"""
    try:
        job = await create_processing_job(
            job_name=req.job_name,
            algorithm=req.algorithm,
            input_sequences=req.input_sequences,
            input_parameters=req.input_parameters
        )
        
        return {
            "id": job.id,
            "job_name": job.job_name,
            "algorithm": job.algorithm,
            "status": job.status,
            "created_at": job.created_at.isoformat()
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(exc)}")


@app.get("/jobs")
async def get_jobs(status: Optional[str] = None, algorithm: Optional[str] = None, limit: int = 50):
    """List processing jobs"""
    try:
        status_filter = ProcessingStatus(status) if status else None
        jobs = await list_processing_jobs(status=status_filter, algorithm=algorithm, limit=limit)
        
        return [
            {
                "id": job.id,
                "job_name": job.job_name,
                "algorithm": job.algorithm,
                "status": job.status,
                "score": job.score,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "processing_steps_count": len(job.processing_steps)
            }
            for job in jobs
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(exc)}")


@app.get("/jobs/{job_id}")
async def get_job_detail(job_id: str):
    """Get job details including processing steps"""
    try:
        job = await get_processing_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "id": job.id,
            "job_name": job.job_name,
            "algorithm": job.algorithm,
            "status": job.status,
            "input_sequences": job.input_sequences,
            "input_parameters": job.input_parameters,
            "processing_steps": [
                {
                    "step_name": step.step_name,
                    "timestamp": step.timestamp.isoformat(),
                    "duration_ms": step.duration_ms,
                    "status": step.status,
                    "details": step.details
                }
                for step in job.processing_steps
            ],
            "result": job.result,
            "score": job.score,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(exc)}")


# ============================================================================
# VISUALIZATION ENDPOINTS
# ============================================================================

@app.post("/visualize")
def visualize(req: VisualizationRequest):
    try:
        sequence = encoder.validate(req.sequence)
        if req.type == "helix":
            return {"type": "helix", "data": viz_generator.generate_helix_coordinates(sequence)}
        elif req.type == "circuit":
            return {"type": "circuit", "data": viz_generator.generate_circuit_diagram(sequence, "vqe")}
        elif req.type == "alignment":
            return {"type": "alignment", "error": "Use align endpoint with decoded path for alignment visualization"}
        else:
            raise ValueError(f"Unknown visualization type: {req.type}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", 8000)))
