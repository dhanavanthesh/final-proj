"""
Enhanced MongoDB operations with datasets and processing logs
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from .db import get_database
from .models import Dataset, ProcessingJob, SequenceAnalysis, ProcessingStatus, ProcessingStep


# Collection names
DATASETS_COLLECTION = "datasets"
PROCESSING_JOBS_COLLECTION = "processing_jobs"
SEQUENCE_ANALYSIS_COLLECTION = "sequence_analysis"


async def save_dataset(dataset: Dataset) -> Dataset:
    """Save a new dataset to MongoDB"""
    db = get_database()
    collection = db[DATASETS_COLLECTION]
    
    doc = dataset.dict(exclude={"id"})
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    
    result = await collection.insert_one(doc)
    dataset.id = str(result.inserted_id)
    
    return dataset


async def get_dataset(dataset_id: str) -> Optional[Dataset]:
    """Retrieve a dataset by ID"""
    db = get_database()
    collection = db[DATASETS_COLLECTION]
    
    try:
        doc = await collection.find_one({"_id": ObjectId(dataset_id)})
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return Dataset(**doc)
    except Exception:
        pass
    return None


async def list_datasets(limit: int = 50, skip: int = 0) -> List[Dataset]:
    """List all datasets with pagination"""
    db = get_database()
    collection = db[DATASETS_COLLECTION]
    
    cursor = collection.find().sort("created_at", -1).skip(skip).limit(limit)
    datasets = []
    
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        datasets.append(Dataset(**doc))
    
    return datasets


async def delete_dataset(dataset_id: str) -> bool:
    """Delete a dataset"""
    db = get_database()
    collection = db[DATASETS_COLLECTION]
    
    try:
        result = await collection.delete_one({"_id": ObjectId(dataset_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def create_processing_job(
    job_name: str,
    algorithm: str,
    input_sequences: List[str],
    input_parameters: Dict[str, Any] = None
) -> ProcessingJob:
    """Create a new processing job"""
    db = get_database()
    collection = db[PROCESSING_JOBS_COLLECTION]
    
    job = ProcessingJob(
        job_name=job_name,
        algorithm=algorithm,
        input_sequences=input_sequences,
        input_parameters=input_parameters or {},
        status=ProcessingStatus.PENDING
    )
    
    doc = job.dict(exclude={"id"})
    result = await collection.insert_one(doc)
    job.id = str(result.inserted_id)
    
    return job


async def update_processing_job(
    job_id: str,
    status: Optional[ProcessingStatus] = None,
    result: Optional[Dict[str, Any]] = None,
    score: Optional[float] = None,
    error_message: Optional[str] = None,
    processing_steps: Optional[List[ProcessingStep]] = None
) -> Optional[ProcessingJob]:
    """Update a processing job"""
    db = get_database()
    collection = db[PROCESSING_JOBS_COLLECTION]
    
    update_doc = {"updated_at": datetime.utcnow()}
    
    if status:
        update_doc["status"] = status
        if status == ProcessingStatus.RUNNING and not update_doc.get("started_at"):
            update_doc["started_at"] = datetime.utcnow()
        elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            update_doc["completed_at"] = datetime.utcnow()
    
    if result is not None:
        update_doc["result"] = result
    if score is not None:
        update_doc["score"] = score
    if error_message is not None:
        update_doc["error_message"] = error_message
    if processing_steps is not None:
        update_doc["processing_steps"] = [step.dict() for step in processing_steps]
    
    try:
        await collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_doc}
        )
        return await get_processing_job(job_id)
    except Exception:
        return None


async def add_processing_step(job_id: str, step: ProcessingStep) -> bool:
    """Add a processing step to a job"""
    db = get_database()
    collection = db[PROCESSING_JOBS_COLLECTION]
    
    try:
        await collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$push": {"processing_steps": step.dict()}}
        )
        return True
    except Exception:
        return False


async def get_processing_job(job_id: str) -> Optional[ProcessingJob]:
    """Get a processing job by ID"""
    db = get_database()
    collection = db[PROCESSING_JOBS_COLLECTION]
    
    try:
        doc = await collection.find_one({"_id": ObjectId(job_id)})
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return ProcessingJob(**doc)
    except Exception:
        pass
    return None


async def list_processing_jobs(
    status: Optional[ProcessingStatus] = None,
    algorithm: Optional[str] = None,
    limit: int = 50
) -> List[ProcessingJob]:
    """List processing jobs with filters"""
    db = get_database()
    collection = db[PROCESSING_JOBS_COLLECTION]
    
    query = {}
    if status:
        query["status"] = status
    if algorithm:
        query["algorithm"] = algorithm
    
    cursor = collection.find(query).sort("created_at", -1).limit(limit)
    jobs = []
    
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        jobs.append(ProcessingJob(**doc))
    
    return jobs


async def save_sequence_analysis(analysis: SequenceAnalysis) -> SequenceAnalysis:
    """Save sequence analysis result"""
    db = get_database()
    collection = db[SEQUENCE_ANALYSIS_COLLECTION]
    
    doc = analysis.dict(exclude={"id"})
    doc["created_at"] = datetime.utcnow()
    
    result = await collection.insert_one(doc)
    analysis.id = str(result.inserted_id)
    
    return analysis


async def get_sequence_analyses(sequence: str = None, limit: int = 50) -> List[SequenceAnalysis]:
    """Get sequence analyses, optionally filtered by sequence"""
    db = get_database()
    collection = db[SEQUENCE_ANALYSIS_COLLECTION]
    
    query = {}
    if sequence:
        query["sequence"] = sequence
    
    cursor = collection.find(query).sort("created_at", -1).limit(limit)
    analyses = []
    
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        analyses.append(SequenceAnalysis(**doc))
    
    return analyses
