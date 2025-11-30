#!/usr/bin/env python3
"""
Import CSV data into Neo4j database.
This script imports users and follow relationships from the data/ directory.
"""

import csv
import os
import sys
from datetime import datetime
from db import run

# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_CSV = os.path.join(PROJECT_ROOT, "data", "users.csv")
FOLLOWS_CSV = os.path.join(PROJECT_ROOT, "data", "follows.csv")

def import_users():
    """Import users from CSV file."""
    print("Importing users...")
    
    if not os.path.exists(USERS_CSV):
        print(f"Error: {USERS_CSV} not found!")
        return False
    
    users_imported = 0
    batch_size = 100
    batch = []
    
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({
                'userId': row['userId'],
                'username': row['username'],
                'name': row['name']
            })
            
            if len(batch) >= batch_size:
                # Import batch
                query = """
                UNWIND $users AS user
                MERGE (u:User {userId: user.userId})
                SET u.username = user.username,
                    u.name = user.name
                """
                run(query, {'users': batch})
                users_imported += len(batch)
                print(f"  Imported {users_imported} users...", end='\r')
                batch = []
        
        # Import remaining users
        if batch:
            query = """
            UNWIND $users AS user
            MERGE (u:User {userId: user.userId})
            SET u.username = user.username,
                u.name = user.name
            """
            run(query, {'users': batch})
            users_imported += len(batch)
    
    print(f"\n✓ Imported {users_imported} users")
    return True

def import_follows():
    """Import follow relationships from CSV file."""
    print("Importing follow relationships...")
    
    if not os.path.exists(FOLLOWS_CSV):
        print(f"Error: {FOLLOWS_CSV} not found!")
        return False
    
    follows_imported = 0
    batch_size = 500
    batch = []
    
    with open(FOLLOWS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({
                'srcUserId': row['srcUserId'],
                'dstUserId': row['dstUserId'],
                'createdAt': row['createdAt']
            })
            
            if len(batch) >= batch_size:
                # Import batch
                query = """
                UNWIND $follows AS f
                MATCH (src:User {userId: f.srcUserId})
                MATCH (dst:User {userId: f.dstUserId})
                MERGE (src)-[r:FOLLOWS]->(dst)
                ON CREATE SET r.since = f.createdAt
                """
                run(query, {'follows': batch})
                follows_imported += len(batch)
                print(f"  Imported {follows_imported} follow relationships...", end='\r')
                batch = []
        
        # Import remaining follows
        if batch:
            query = """
            UNWIND $follows AS f
            MATCH (src:User {userId: f.srcUserId})
            MATCH (dst:User {userId: f.dstUserId})
            MERGE (src)-[r:FOLLOWS]->(dst)
            ON CREATE SET r.since = datetime(f.createdAt)
            """
            run(query, {'follows': batch})
            follows_imported += len(batch)
    
    print(f"\n✓ Imported {follows_imported} follow relationships")
    return True

def main():
    """Main import function."""
    print("=" * 60)
    print("Neo4j Data Import Script")
    print("=" * 60)
    print()
    
    # Check if files exist
    if not os.path.exists(USERS_CSV):
        print(f"Error: Users CSV not found at {USERS_CSV}")
        sys.exit(1)
    
    if not os.path.exists(FOLLOWS_CSV):
        print(f"Error: Follows CSV not found at {FOLLOWS_CSV}")
        sys.exit(1)
    
    # Import users
    if not import_users():
        print("Failed to import users!")
        sys.exit(1)
    
    print()
    
    # Import follows
    if not import_follows():
        print("Failed to import follow relationships!")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ Import completed successfully!")
    print("=" * 60)
    
    # Show some stats
    stats_query = """
    MATCH (u:User)
    WITH count(u) AS user_count
    MATCH ()-[f:FOLLOWS]->()
    WITH user_count, count(f) AS follow_count
    RETURN user_count, follow_count
    """
    result = run(stats_query)
    if result:
        stats = result[0]
        print(f"\nDatabase Statistics:")
        print(f"  Users: {stats['user_count']}")
        print(f"  Follow relationships: {stats['follow_count']}")

if __name__ == "__main__":
    main()

