from __future__ import annotations
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from bson import ObjectId

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "qgenome")
COLLECTION_NAME = "sequence_runs"

# Global MongoDB client and database instances
_mongodb_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


class SequenceRunResponse(BaseModel):
    """API response model for sequence runs"""
    id: str
    run_type: str
    sequence_a: str
    sequence_b: Optional[str] = None
    score: float
    result: dict
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


async def connect_to_mongo():
    """Initialize MongoDB connection on app startup"""
    global _mongodb_client, _database
    _mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    _database = _mongodb_client[DATABASE_NAME]

    # Create indexes for performance
    collection = _database[COLLECTION_NAME]
    await collection.create_index("run_type")
    await collection.create_index([("created_at", -1)])  # Descending for recent-first queries

    print(f"Connected to MongoDB at {MONGODB_URL}, database: {DATABASE_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection on app shutdown"""
    global _mongodb_client
    if _mongodb_client:
        _mongodb_client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return _database


async def get_collection():
    """Get the sequence_runs collection"""
    db = get_database()
    return db[COLLECTION_NAME]


async def save_run(
    run_type: str,
    sequence_a: str,
    sequence_b: Optional[str],
    score: float,
    result: dict
) -> SequenceRunResponse:
    """
    Create a new sequence run record.

    Args:
        run_type: Type of run ("align", "motif", "variant")
        sequence_a: Primary sequence
        sequence_b: Secondary sequence (optional)
        score: Numerical score result
        result: Full result dictionary (stored as native dict)

    Returns:
        SequenceRunResponse with generated ID
    """
    collection = await get_collection()

    # Create document
    doc = {
        "run_type": run_type,
        "sequence_a": sequence_a,
        "sequence_b": sequence_b,
        "score": score,
        "result": result,  # Native dict storage (no JSON stringification)
        "created_at": datetime.utcnow()
    }

    # Insert and get result
    insert_result = await collection.insert_one(doc)

    # Fetch the inserted document to return complete object
    created_doc = await collection.find_one({"_id": insert_result.inserted_id})

    # Convert to response model
    return SequenceRunResponse(
        id=str(created_doc["_id"]),
        run_type=created_doc["run_type"],
        sequence_a=created_doc["sequence_a"],
        sequence_b=created_doc.get("sequence_b"),
        score=created_doc["score"],
        result=created_doc["result"],
        created_at=created_doc["created_at"]
    )


async def fetch_runs(
    run_type: Optional[str] = None,
    limit: int = 10
) -> list[SequenceRunResponse]:
    """
    Fetch sequence runs with optional filtering and pagination.

    Args:
        run_type: Filter by run type (optional)
        limit: Maximum number of results (default 10, max 50)

    Returns:
        List of SequenceRunResponse objects, sorted by created_at descending
    """
    collection = await get_collection()

    # Build query filter
    query_filter = {}
    if run_type:
        query_filter["run_type"] = run_type

    # Execute query with sort and limit
    cursor = collection.find(query_filter).sort("created_at", -1).limit(min(limit, 50))

    # Convert cursor to list and map to response models
    documents = await cursor.to_list(length=limit)

    return [
        SequenceRunResponse(
            id=str(doc["_id"]),
            run_type=doc["run_type"],
            sequence_a=doc["sequence_a"],
            sequence_b=doc.get("sequence_b"),
            score=doc["score"],
            result=doc["result"],
            created_at=doc["created_at"]
        )
        for doc in documents
    ]


async def get_run_by_id(run_id: str) -> Optional[SequenceRunResponse]:
    """
    Fetch a single run by ID.

    Args:
        run_id: String representation of ObjectId

    Returns:
        SequenceRunResponse or None if not found
    """
    collection = await get_collection()

    # Validate and convert to ObjectId
    if not ObjectId.is_valid(run_id):
        return None

    doc = await collection.find_one({"_id": ObjectId(run_id)})

    if not doc:
        return None

    return SequenceRunResponse(
        id=str(doc["_id"]),
        run_type=doc["run_type"],
        sequence_a=doc["sequence_a"],
        sequence_b=doc.get("sequence_b"),
        score=doc["score"],
        result=doc["result"],
        created_at=doc["created_at"]
    )


async def update_run(
    run_id: str,
    score: Optional[float] = None,
    result: Optional[dict] = None
) -> Optional[SequenceRunResponse]:
    """
    Update a run's score and/or result.

    Args:
        run_id: String representation of ObjectId
        score: New score (optional)
        result: New result dict (optional)

    Returns:
        Updated SequenceRunResponse or None if not found
    """
    collection = await get_collection()

    # Validate ObjectId
    if not ObjectId.is_valid(run_id):
        return None

    # Build update document
    update_doc = {}
    if score is not None:
        update_doc["score"] = score
    if result is not None:
        update_doc["result"] = result

    if not update_doc:
        # Nothing to update, just return current document
        return await get_run_by_id(run_id)

    # Perform update using find_one_and_update
    updated_doc = await collection.find_one_and_update(
        {"_id": ObjectId(run_id)},
        {"$set": update_doc},
        return_document=True  # Return updated document
    )

    if not updated_doc:
        return None

    return SequenceRunResponse(
        id=str(updated_doc["_id"]),
        run_type=updated_doc["run_type"],
        sequence_a=updated_doc["sequence_a"],
        sequence_b=updated_doc.get("sequence_b"),
        score=updated_doc["score"],
        result=updated_doc["result"],
        created_at=updated_doc["created_at"]
    )


async def delete_run(run_id: str) -> bool:
    """
    Delete a run by ID.

    Args:
        run_id: String representation of ObjectId

    Returns:
        True if deleted, False if not found or invalid ID
    """
    collection = await get_collection()

    # Validate ObjectId
    if not ObjectId.is_valid(run_id):
        return False

    result = await collection.delete_one({"_id": ObjectId(run_id)})

    return result.deleted_count > 0
