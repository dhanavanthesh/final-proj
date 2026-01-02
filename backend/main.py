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
    sequence: str = Field(..., example="ATGC")


class AlignRequest(BaseModel):
    sequence1: str = Field(..., example="ATGC")
    sequence2: str = Field(..., example="ATCC")


class MotifRequest(BaseModel):
    sequences: List[str]
    motif_length: int = 6


class VariantRequest(BaseModel):
    sequence: str


class RunUpdate(BaseModel):
    score: Optional[float] = None
    result: Optional[dict] = None


class BatchAlignRequest(BaseModel):
    sequence_pairs: List[dict] = Field(..., example=[{"seq1": "ATGC", "seq2": "ATCC"}])


class BatchMotifRequest(BaseModel):
    sequences_list: List[List[str]] = Field(..., example=[[["ATGC", "ATCC"], ["ATGC", "ATCC"]]])
    motif_length: int = 6


class VisualizationRequest(BaseModel):
    sequence: str
    type: str = Field(..., example="helix")  # helix, circuit, alignment


# Viterbi-specific request models
class ViterbiRequest(BaseModel):
    sequence: str = Field(..., example="ATGCCTACGCATGCTA", description="DNA sequence (A, C, G, T only)")
    hmm_model: str = Field(default="2-state-exon-intron", example="2-state-exon-intron", description="HMM model to use")
    shots: int = Field(default=1024, example=1024, description="Number of quantum shots (quantum only)")


class CircuitDiagramRequest(BaseModel):
    sequence: str = Field(..., example="ATGCCTACGCATGCTA")
    hmm_model: str = Field(default="2-state-exon-intron", example="2-state-exon-intron")
    time_step: int = Field(default=0, example=0, description="Which time step to visualize")


class ViterbiAnimationRequest(BaseModel):
    sequence: str = Field(..., example="ATGCCTACGCATGCTA")
    hmm_model: str = Field(default="2-state-exon-intron", example="2-state-exon-intron")


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
    try:
        result = vqe_engine.align(req.sequence1, req.sequence2)
        await save_run("align", req.sequence1, req.sequence2, result["alignment_score"], result)
        return {"algorithm": "VQE", "results": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


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
        decoded_path = result["results"]["decoded_path"]

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
        raise HTTPException(status_code=500, detail=f"Animation generation failed: {str(exc)}")


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
