#!/usr/bin/env python3
"""
Import celebrity data into Neo4j database.
This script imports celebrities and their follow relationships.
"""

import csv
import os
import sys
from db import run
import hashlib

# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELEBRITIES_CSV = os.path.join(PROJECT_ROOT, "data", "celebrities.csv")
CELEBRITIES_FOLLOWS_CSV = os.path.join(PROJECT_ROOT, "data", "celebrities_follows.csv")

def hash_password(password: str) -> str:
    """Simple password hashing (for demo purposes)"""
    return hashlib.sha256(password.encode()).hexdigest()

def import_celebrities():
    """Import celebrities from CSV file."""
    print("Importing celebrities...")
    
    if not os.path.exists(CELEBRITIES_CSV):
        print(f"Error: {CELEBRITIES_CSV} not found!")
        return False
    
    celebrities_imported = 0
    batch_size = 20
    batch = []
    
    with open(CELEBRITIES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip legendaryChris if already exists (user already created it)
            if row['username'] == 'legendaryChris':
                print(f"  Skipping {row['username']} (already exists)")
                continue
                
            # Generate a simple password from username for demo purposes
            password = hash_password(f"{row['username']}123")
            
            batch.append({
                'username': row['username'],
                'name': row['name'],
                'email': row['email'],
                'bio': row.get('bio', ''),
                'password': password
            })
            
            if len(batch) >= batch_size:
                # Import batch - use MERGE on username, generate userId only on CREATE
                query = """
                UNWIND $celebrities AS celeb
                MERGE (u:User {username: celeb.username})
                ON CREATE SET 
                    u.userId = randomUUID(),
                    u.name = celeb.name,
                    u.email = celeb.email,
                    u.bio = celeb.bio,
                    u.password = celeb.password,
                    u.createdAt = datetime()
                ON MATCH SET
                    u.name = celeb.name,
                    u.email = celeb.email,
                    u.bio = celeb.bio
                """
                run(query, {'celebrities': batch})
                celebrities_imported += len(batch)
                print(f"  Imported {celebrities_imported} celebrities...", end='\r')
                batch = []
        
        # Import remaining celebrities
        if batch:
            query = """
            UNWIND $celebrities AS celeb
            MERGE (u:User {username: celeb.username})
            ON CREATE SET 
                u.userId = randomUUID(),
                u.name = celeb.name,
                u.email = celeb.email,
                u.bio = celeb.bio,
                u.password = celeb.password,
                u.createdAt = datetime()
            ON MATCH SET
                u.name = celeb.name,
                u.email = celeb.email,
                u.bio = celeb.bio
            """
            run(query, {'celebrities': batch})
            celebrities_imported += len(batch)
    
    print(f"\n✓ Imported {celebrities_imported} celebrities")
    return True

def import_celebrities_follows():
    """Import follow relationships from CSV file."""
    print("Importing celebrity follow relationships...")
    
    if not os.path.exists(CELEBRITIES_FOLLOWS_CSV):
        print(f"Error: {CELEBRITIES_FOLLOWS_CSV} not found!")
        return False
    
    follows_imported = 0
    batch_size = 100
    batch = []
    
    with open(CELEBRITIES_FOLLOWS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({
                'srcUsername': row['srcUsername'],
                'dstUsername': row['dstUsername'],
                'createdAt': row['createdAt']
            })
            
            if len(batch) >= batch_size:
                # Import batch
                query = """
                UNWIND $follows AS f
                MATCH (src:User {username: f.srcUsername})
                MATCH (dst:User {username: f.dstUsername})
                MERGE (src)-[r:FOLLOWS]->(dst)
                ON CREATE SET r.since = datetime(f.createdAt)
                """
                try:
                    run(query, {'follows': batch})
                    follows_imported += len(batch)
                    print(f"  Imported {follows_imported} follow relationships...", end='\r')
                except Exception as e:
                    print(f"\n  Warning: Error importing batch: {e}")
                batch = []
        
        # Import remaining follows
        if batch:
            query = """
            UNWIND $follows AS f
            MATCH (src:User {username: f.srcUsername})
            MATCH (dst:User {username: f.dstUsername})
            MERGE (src)-[r:FOLLOWS]->(dst)
            ON CREATE SET r.since = datetime(f.createdAt)
            """
            try:
                run(query, {'follows': batch})
                follows_imported += len(batch)
            except Exception as e:
                print(f"\n  Warning: Error importing final batch: {e}")
    
    print(f"\n✓ Imported {follows_imported} follow relationships")
    return True

def main():
    """Main import function."""
    print("=" * 60)
    print("Celebrity Data Import Script")
    print("=" * 60)
    print()
    
    # Check if files exist
    if not os.path.exists(CELEBRITIES_CSV):
        print(f"Error: Celebrities CSV not found at {CELEBRITIES_CSV}")
        sys.exit(1)
    
    if not os.path.exists(CELEBRITIES_FOLLOWS_CSV):
        print(f"Error: Celebrity follows CSV not found at {CELEBRITIES_FOLLOWS_CSV}")
        sys.exit(1)
    
    # Import celebrities
    if not import_celebrities():
        print("Failed to import celebrities!")
        sys.exit(1)
    
    print()
    
    # Import follows
    if not import_celebrities_follows():
        print("Failed to import follow relationships!")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ Import completed successfully!")
    print("=" * 60)
    
    # Show some stats
    stats_query = """
    MATCH (u:User)
    WHERE u.bio IS NOT NULL AND u.bio <> ''
    WITH count(u) AS celeb_count
    MATCH ()-[f:FOLLOWS]->()
    WITH celeb_count, count(f) AS follow_count
    RETURN celeb_count, follow_count
    """
    result = run(stats_query)
    if result:
        stats = result[0]
        print(f"\nDatabase Statistics:")
        print(f"  Celebrities with bios: {stats['celeb_count']}")
        print(f"  Total follow relationships: {stats['follow_count']}")
    
    print("\nNote: Default password for celebrities is '{username}123'")
    print("Example: For 'leoDiCap', password is 'leoDiCap123'")

if __name__ == "__main__":
    main()

