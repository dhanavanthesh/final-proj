"""
MongoDB Setup Helper Script
Checks MongoDB connection and creates indexes
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db import connect_to_mongo, close_mongo_connection, get_database


async def setup_mongodb():
    """Setup and verify MongoDB connection"""
    print("=" * 80)
    print("QGENOME - MongoDB Setup")
    print("=" * 80)
    
    try:
        print("\n[1/3] Connecting to MongoDB...")
        await connect_to_mongo()
        print("✓ Connected successfully!")
        
        print("\n[2/3] Verifying database access...")
        db = get_database()
        
        # List collections
        collections = await db.list_collection_names()
        print(f"✓ Database accessible. Collections: {collections if collections else 'None (new database)'}")
        
        print("\n[3/3] Creating indexes...")
        
        # Datasets collection
        datasets_col = db["datasets"]
        await datasets_col.create_index("name")
        await datasets_col.create_index([("created_at", -1)])
        print("✓ Datasets indexes created")
        
        # Processing jobs collection
        jobs_col = db["processing_jobs"]
        await jobs_col.create_index("status")
        await jobs_col.create_index("algorithm")
        await jobs_col.create_index([("created_at", -1)])
        print("✓ Processing jobs indexes created")
        
        # Sequence runs collection
        runs_col = db["sequence_runs"]
        await runs_col.create_index("run_type")
        await runs_col.create_index([("created_at", -1)])
        print("✓ Sequence runs indexes created")
        
        print("\n" + "=" * 80)
        print("MongoDB setup completed successfully!")
        print("=" * 80)
        print("\nYou can now:")
        print("1. Start the backend: python -m backend.main")
        print("2. Use the CLI: python -m backend.cli dataset list")
        print("3. Access frontend: http://localhost:3000/")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is running:")
        print("   - Local: mongod")
        print("   - Docker: docker run -d -p 27017:27017 mongo")
        print("2. Check your .env file for correct MONGODB_URL")
        print("3. Verify MongoDB is accessible on the configured port")
        sys.exit(1)
    
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(setup_mongodb())
