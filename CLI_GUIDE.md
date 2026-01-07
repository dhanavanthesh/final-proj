# QGENOME CLI Guide

## Overview

The QGENOME CLI provides command-line access to the Quantum Genome Analysis system, allowing you to manage datasets, create processing jobs, and interact with MongoDB storage directly.

## Installation

Ensure all dependencies are installed:

```bash
cd backend
pip install -r requirements.txt
```

## MongoDB Setup

Make sure MongoDB is running. You can use:
- Local MongoDB installation
- MongoDB Atlas (cloud)
- Docker: `docker run -d -p 27017:27017 mongo`

Configure connection in `.env` file:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=qgenome
```

## CLI Usage

### Dataset Commands

#### Create a Dataset
```bash
python -m backend.cli dataset create \
  --name "My Dataset" \
  --sequences ATGCGTACGATCG CGTAGCTAGCTA \
  --description "Sample DNA sequences" \
  --tags gene exon
```

#### List All Datasets
```bash
python -m backend.cli dataset list --limit 50
```

#### Get Dataset Details
```bash
python -m backend.cli dataset get <dataset_id>
```

#### Delete a Dataset
```bash
python -m backend.cli dataset delete <dataset_id>
```

#### Import from FASTA File
```bash
python -m backend.cli dataset import sequences.fasta --name "Imported Sequences"
```

### Processing Job Commands

#### Create a Processing Job
```bash
python -m backend.cli job create \
  --name "VQE Alignment Test" \
  --algorithm vqe_alignment \
  --sequences ATGCGTACG ATGCTTACG
```

Available algorithms:
- `vqe_alignment` - VQE-based sequence alignment
- `qaoa_motif` - QAOA motif finding
- `qcnn_variant` - QCNN variant detection
- `smith_waterman` - Classical Smith-Waterman alignment
- `blast` - BLAST-like search
- `classical_viterbi` - Classical Viterbi algorithm
- `quantum_viterbi` - Quantum Viterbi algorithm

#### List Processing Jobs
```bash
# List all jobs
python -m backend.cli job list

# Filter by status
python -m backend.cli job list --status completed
python -m backend.cli job list --status running
python -m backend.cli job list --status failed

# Filter by algorithm
python -m backend.cli job list --algorithm vqe_alignment
```

#### Get Job Details (with Processing Steps)
```bash
python -m backend.cli job get <job_id>
```

This shows:
- Job metadata
- Input sequences and parameters
- All processing steps with timing
- Results and scores
- Any errors

## Example Workflows

### 1. Import and Process Dataset

```bash
# Import sequences from FASTA
python -m backend.cli dataset import data/sequences.fasta --name "Gene Dataset"

# Get the dataset ID from output, then create a job
python -m backend.cli job create \
  --name "Align Gene Sequences" \
  --algorithm vqe_alignment \
  --sequences ATGCGTACGATCG ATGCTTACGATCG

# Monitor job progress
python -m backend.cli job get <job_id>
```

### 2. Batch Processing

```bash
# Create multiple datasets
python -m backend.cli dataset create --name "Set 1" --sequences ATGC CGTA
python -m backend.cli dataset create --name "Set 2" --sequences TGCA GCAT

# List all datasets
python -m backend.cli dataset list

# Create jobs for each
python -m backend.cli job create --name "Job 1" --algorithm quantum_viterbi --sequences ATGCGTACGATCGATCG
python -m backend.cli job create --name "Job 2" --algorithm classical_viterbi --sequences CGTAGCTAGCTAGCTA

# Check all jobs
python -m backend.cli job list
```

## Processing Visibility

When you create a job through the API or CLI, the system tracks:

1. **Input Validation** - Validates sequences and parameters
2. **Circuit Construction** - Builds quantum circuits (for quantum algorithms)
3. **Execution** - Runs the algorithm
4. **Post-processing** - Analyzes results
5. **Database Storage** - Saves results to MongoDB

Each step includes:
- Timestamp
- Duration (milliseconds)
- Status (completed/failed)
- Details (specific to each step)

## API Integration

The CLI works alongside the REST API. You can:

1. **Frontend → API**: Submit sequences via web interface
2. **API → MongoDB**: Store in database with full traceability
3. **CLI → MongoDB**: Query and analyze stored data
4. **CLI → API**: Create jobs that the API can process

## Real-time Processing Example

```bash
# Create a job with the API (via frontend or curl)
curl -X POST http://localhost:8000/align \
  -H "Content-Type: application/json" \
  -d '{"sequence1": "ATGCGTACG", "sequence2": "ATGCTTACG"}'

# The response includes a job_id and processing_summary
# {
#   "job_id": "64abc123...",
#   "processing_summary": {
#     "total_steps": 3,
#     "total_duration_ms": 1234.56,
#     "steps": [...]
#   }
# }

# Check the job details
python -m backend.cli job get 64abc123...
```

## MongoDB Collections

The system uses these collections:

1. **datasets** - Stores DNA sequence datasets
2. **processing_jobs** - Tracks all processing jobs with full history
3. **sequence_runs** - Legacy collection for runs (still supported)
4. **sequence_analysis** - Individual sequence analyses

## Troubleshooting

### Connection Issues

If you get MongoDB connection errors:

```bash
# Check if MongoDB is running
mongosh  # or mongo

# If using Docker
docker ps | grep mongo

# Check environment variables
echo $MONGODB_URL
```

### Import Errors

If you get relative import errors when running CLI:

```bash
# Always run from project root
cd c:\Users\harsh\final-proj

# Use module syntax
python -m backend.cli dataset list
```

## Advanced Usage

### Custom FASTA Import

Create a FASTA file `sequences.fasta`:
```
>Sequence1
ATGCGTACGATCGATCG
>Sequence2
CGTAGCTAGCTAGCTA
>Sequence3
TGCAGTCAGTCAGTCA
```

Import:
```bash
python -m backend.cli dataset import sequences.fasta --name "Custom Dataset"
```

### Programmatic Access

You can also use the CLI classes in your own Python scripts:

```python
import asyncio
from backend.cli import QGENOMECLI

async def main():
    cli = QGENOMECLI()
    
    # Create dataset
    dataset_id = await cli.create_dataset(
        name="My Dataset",
        sequences=["ATGC", "CGTA"],
        description="Test data"
    )
    
    # Create job
    job_id = await cli.create_job(
        name="Test Job",
        algorithm="vqe_alignment",
        sequences=["ATGC", "CGTA"]
    )
    
    # Get results
    await cli.get_job(job_id)
    
    await cli.disconnect()

asyncio.run(main())
```

## Next Steps

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Start MongoDB: `mongod` or use Docker
3. Set up `.env` file with MongoDB connection
4. Start backend API: `python -m backend.main`
5. Try CLI commands: `python -m backend.cli dataset list`
6. Use frontend at http://localhost:3000/

## Support

For issues or questions, check:
- Backend logs in console
- MongoDB logs: `mongod.log`
- API documentation: http://localhost:8000/docs
