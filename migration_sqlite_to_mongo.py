"""
One-time migration script: SQLite to MongoDB
Usage: python migration_sqlite_to_mongo.py
"""
import asyncio
import sqlite3
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

SQLITE_DB = "qgenome.db"
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "qgenome")
COLLECTION_NAME = "sequence_runs"


async def migrate():
    # Check if SQLite database exists
    if not os.path.exists(SQLITE_DB):
        print(f"SQLite database '{SQLITE_DB}' not found. Nothing to migrate.")
        return

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row  # Dict-like access
    cursor = sqlite_conn.cursor()

    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    db = mongo_client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    print(f"Starting migration from {SQLITE_DB} to MongoDB...")

    # Fetch all records from SQLite
    try:
        cursor.execute("SELECT * FROM sequencerun")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Error reading from SQLite: {e}")
        print("Make sure the table 'sequencerun' exists.")
        sqlite_conn.close()
        mongo_client.close()
        return

    if not rows:
        print("No records found in SQLite database.")
        sqlite_conn.close()
        mongo_client.close()
        return

    # Convert and insert into MongoDB
    documents = []
    for row in rows:
        try:
            # Parse the created_at field
            created_at = row["created_at"]
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            elif not isinstance(created_at, datetime):
                created_at = datetime.utcnow()

            doc = {
                "run_type": row["run_type"],
                "sequence_a": row["sequence_a"],
                "sequence_b": row["sequence_b"],
                "score": row["score"],
                "result": json.loads(row["result_json"]),  # Parse JSON string
                "created_at": created_at
            }
            documents.append(doc)
        except Exception as e:
            print(f"Error processing row {row['id']}: {e}")
            continue

    # Bulk insert
    if documents:
        result = await collection.insert_many(documents)
        print(f"Migrated {len(result.inserted_ids)} records successfully!")
    else:
        print("No valid documents to migrate.")

    # Create indexes
    print("Creating indexes...")
    await collection.create_index("run_type")
    await collection.create_index([("created_at", -1)])
    print("Indexes created.")

    # Cleanup
    sqlite_conn.close()
    mongo_client.close()

    print("Migration complete!")
    print(f"You can now verify the data in MongoDB using: mongosh")
    print(f"  > use {DATABASE_NAME}")
    print(f"  > db.{COLLECTION_NAME}.find()")


if __name__ == "__main__":
    asyncio.run(migrate())
