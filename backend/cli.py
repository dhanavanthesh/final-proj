#!/usr/bin/env python
"""
QGENOME CLI - Command Line Interface for Quantum Genome Analysis
"""
import asyncio
import sys
import json
from typing import Optional, List
import argparse
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from db import connect_to_mongo, close_mongo_connection
from mongo_operations import (
    save_dataset, get_dataset, list_datasets, delete_dataset,
    create_processing_job, get_processing_job, list_processing_jobs,
    update_processing_job
)
from models import Dataset, ProcessingStatus, AlgorithmType
from processing_logger import create_job_logger


class QGENOMECLI:
    """Main CLI class for QGENOME operations"""
    
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        """Connect to MongoDB"""
        if not self.connected:
            await connect_to_mongo()
            self.connected = True
            print("✓ Connected to MongoDB")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.connected:
            await close_mongo_connection()
            self.connected = False
            print("✓ Disconnected from MongoDB")
    
    # Dataset operations
    async def create_dataset(self, name: str, sequences: List[str], description: str = None, tags: List[str] = None):
        """Create a new dataset"""
        await self.connect()
        
        dataset = Dataset(
            name=name,
            description=description or "",
            sequences=sequences,
            tags=tags or []
        )
        
        saved_dataset = await save_dataset(dataset)
        print(f"✓ Dataset created with ID: {saved_dataset.id}")
        print(f"  Name: {saved_dataset.name}")
        print(f"  Sequences: {len(saved_dataset.sequences)}")
        return saved_dataset.id
    
    async def list_datasets_cmd(self, limit: int = 50):
        """List all datasets"""
        await self.connect()
        
        datasets = await list_datasets(limit=limit)
        
        if not datasets:
            print("No datasets found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(datasets)} dataset(s)")
        print(f"{'='*80}\n")
        
        for i, ds in enumerate(datasets, 1):
            print(f"{i}. {ds.name} (ID: {ds.id})")
            print(f"   Sequences: {len(ds.sequences)}")
            print(f"   Created: {ds.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if ds.description:
                print(f"   Description: {ds.description}")
            if ds.tags:
                print(f"   Tags: {', '.join(ds.tags)}")
            print()
    
    async def get_dataset_cmd(self, dataset_id: str):
        """Get dataset details"""
        await self.connect()
        
        dataset = await get_dataset(dataset_id)
        
        if not dataset:
            print(f"Dataset {dataset_id} not found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Dataset: {dataset.name}")
        print(f"{'='*80}")
        print(f"ID: {dataset.id}")
        print(f"Description: {dataset.description or 'N/A'}")
        print(f"Created: {dataset.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {dataset.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tags: {', '.join(dataset.tags) if dataset.tags else 'None'}")
        print(f"\nSequences ({len(dataset.sequences)}):")
        for i, seq in enumerate(dataset.sequences, 1):
            print(f"  {i}. {seq[:50]}{'...' if len(seq) > 50 else ''} (length: {len(seq)})")
        print()
    
    async def delete_dataset_cmd(self, dataset_id: str):
        """Delete a dataset"""
        await self.connect()
        
        deleted = await delete_dataset(dataset_id)
        
        if deleted:
            print(f"✓ Dataset {dataset_id} deleted successfully")
        else:
            print(f"✗ Failed to delete dataset {dataset_id}")
    
    # Processing job operations
    async def create_job(self, name: str, algorithm: str, sequences: List[str], parameters: dict = None):
        """Create a processing job"""
        await self.connect()
        
        job = await create_processing_job(
            job_name=name,
            algorithm=algorithm,
            input_sequences=sequences,
            input_parameters=parameters or {}
        )
        
        print(f"✓ Job created with ID: {job.id}")
        print(f"  Name: {job.job_name}")
        print(f"  Algorithm: {job.algorithm}")
        print(f"  Status: {job.status}")
        return job.id
    
    async def list_jobs(self, status: str = None, algorithm: str = None, limit: int = 50):
        """List processing jobs"""
        await self.connect()
        
        status_filter = ProcessingStatus(status) if status else None
        jobs = await list_processing_jobs(status=status_filter, algorithm=algorithm, limit=limit)
        
        if not jobs:
            print("No jobs found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(jobs)} job(s)")
        print(f"{'='*80}\n")
        
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.job_name} (ID: {job.id})")
            print(f"   Algorithm: {job.algorithm}")
            print(f"   Status: {job.status}")
            print(f"   Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if job.score is not None:
                print(f"   Score: {job.score}")
            if job.processing_steps:
                print(f"   Processing Steps: {len(job.processing_steps)}")
            print()
    
    async def get_job(self, job_id: str):
        """Get job details"""
        await self.connect()
        
        job = await get_processing_job(job_id)
        
        if not job:
            print(f"Job {job_id} not found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Job: {job.job_name}")
        print(f"{'='*80}")
        print(f"ID: {job.id}")
        print(f"Algorithm: {job.algorithm}")
        print(f"Status: {job.status}")
        print(f"Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if job.started_at:
            print(f"Started: {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if job.completed_at:
            print(f"Completed: {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nInput Sequences ({len(job.input_sequences)}):")
        for i, seq in enumerate(job.input_sequences, 1):
            print(f"  {i}. {seq[:50]}{'...' if len(seq) > 50 else ''}")
        
        if job.input_parameters:
            print(f"\nInput Parameters:")
            for key, value in job.input_parameters.items():
                print(f"  {key}: {value}")
        
        if job.processing_steps:
            print(f"\nProcessing Steps ({len(job.processing_steps)}):")
            for i, step in enumerate(job.processing_steps, 1):
                print(f"  {i}. {step.step_name}")
                print(f"     Duration: {step.duration_ms:.2f}ms")
                print(f"     Status: {step.status}")
                if step.details:
                    print(f"     Details: {step.details}")
        
        if job.result:
            print(f"\nResult:")
            print(json.dumps(job.result, indent=2))
        
        if job.error_message:
            print(f"\nError: {job.error_message}")
        
        print()
    
    # Utility operations
    async def import_fasta(self, file_path: str, dataset_name: str = None):
        """Import sequences from FASTA file"""
        sequences = []
        current_seq = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('>'):
                        if current_seq:
                            sequences.append(''.join(current_seq))
                            current_seq = []
                    else:
                        current_seq.append(line)
                
                if current_seq:
                    sequences.append(''.join(current_seq))
            
            if not sequences:
                print("No sequences found in file.")
                return
            
            name = dataset_name or f"Import from {Path(file_path).name}"
            dataset_id = await self.create_dataset(name, sequences, description=f"Imported from {file_path}")
            
            print(f"✓ Imported {len(sequences)} sequences")
            return dataset_id
            
        except Exception as e:
            print(f"✗ Error importing file: {str(e)}")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="QGENOME CLI - Quantum Genome Analysis")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dataset commands
    dataset_parser = subparsers.add_parser('dataset', help='Dataset operations')
    dataset_subparsers = dataset_parser.add_subparsers(dest='dataset_command')
    
    create_ds = dataset_subparsers.add_parser('create', help='Create a new dataset')
    create_ds.add_argument('--name', required=True, help='Dataset name')
    create_ds.add_argument('--sequences', nargs='+', required=True, help='DNA sequences')
    create_ds.add_argument('--description', help='Dataset description')
    create_ds.add_argument('--tags', nargs='+', help='Dataset tags')
    
    list_ds = dataset_subparsers.add_parser('list', help='List all datasets')
    list_ds.add_argument('--limit', type=int, default=50, help='Maximum number of results')
    
    get_ds = dataset_subparsers.add_parser('get', help='Get dataset details')
    get_ds.add_argument('dataset_id', help='Dataset ID')
    
    delete_ds = dataset_subparsers.add_parser('delete', help='Delete a dataset')
    delete_ds.add_argument('dataset_id', help='Dataset ID')
    
    import_ds = dataset_subparsers.add_parser('import', help='Import from FASTA file')
    import_ds.add_argument('file_path', help='Path to FASTA file')
    import_ds.add_argument('--name', help='Dataset name')
    
    # Job commands
    job_parser = subparsers.add_parser('job', help='Processing job operations')
    job_subparsers = job_parser.add_subparsers(dest='job_command')
    
    create_job = job_subparsers.add_parser('create', help='Create a processing job')
    create_job.add_argument('--name', required=True, help='Job name')
    create_job.add_argument('--algorithm', required=True, choices=[a.value for a in AlgorithmType], help='Algorithm to use')
    create_job.add_argument('--sequences', nargs='+', required=True, help='DNA sequences to process')
    
    list_jobs = job_subparsers.add_parser('list', help='List processing jobs')
    list_jobs.add_argument('--status', choices=[s.value for s in ProcessingStatus], help='Filter by status')
    list_jobs.add_argument('--algorithm', choices=[a.value for a in AlgorithmType], help='Filter by algorithm')
    list_jobs.add_argument('--limit', type=int, default=50, help='Maximum number of results')
    
    get_job = job_subparsers.add_parser('get', help='Get job details')
    get_job.add_argument('job_id', help='Job ID')
    
    args = parser.parse_args()
    
    cli = QGENOMECLI()
    
    try:
        if args.command == 'dataset':
            if args.dataset_command == 'create':
                await cli.create_dataset(args.name, args.sequences, args.description, args.tags)
            elif args.dataset_command == 'list':
                await cli.list_datasets_cmd(args.limit)
            elif args.dataset_command == 'get':
                await cli.get_dataset_cmd(args.dataset_id)
            elif args.dataset_command == 'delete':
                await cli.delete_dataset_cmd(args.dataset_id)
            elif args.dataset_command == 'import':
                await cli.import_fasta(args.file_path, args.name)
        
        elif args.command == 'job':
            if args.job_command == 'create':
                await cli.create_job(args.name, args.algorithm, args.sequences)
            elif args.job_command == 'list':
                await cli.list_jobs(args.status, args.algorithm, args.limit)
            elif args.job_command == 'get':
                await cli.get_job(args.job_id)
        
        else:
            parser.print_help()
    
    finally:
        await cli.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
