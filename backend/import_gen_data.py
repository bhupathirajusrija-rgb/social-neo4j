#!/usr/bin/env python3
"""
Import generated user data into Neo4j database.
This script imports users from gen_users.csv and follow relationships from follows.csv.
"""

import csv
import os
import sys
from db import run
import hashlib
import re

# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN_USERS_CSV = os.path.join(PROJECT_ROOT, "data", "gen_users.csv")
FOLLOWS_CSV = os.path.join(PROJECT_ROOT, "data", "follows.csv")

def hash_password(password: str) -> str:
    """Hash password if it's not already hashed"""
    # Check if already hashed (SHA256 produces 64 char hex string)
    if len(password) == 64 and all(c in '0123456789abcdef' for c in password.lower()):
        return password
    return hashlib.sha256(password.encode()).hexdigest()

def generate_username(name: str, email: str, user_id: str) -> str:
    """Generate a username from name, email, or id"""
    # Try to create username from name (first name + last name initial)
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        first = name_parts[0].lower()
        last = name_parts[-1].lower()
        base_username = f"{first}{last[0]}"
    else:
        # Fallback to email username part
        base_username = email.split('@')[0].replace('.', '')
    
    # Add id to ensure uniqueness
    username = f"{base_username}{user_id}"
    return username

def import_gen_users():
    """Import users from gen_users.csv file."""
    print("Importing users from gen_users.csv...")
    
    if not os.path.exists(GEN_USERS_CSV):
        print(f"Error: {GEN_USERS_CSV} not found!")
        return False
    
    users_imported = 0
    batch_size = 100
    batch = []
    
    with open(GEN_USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row['id']
            name = row['name']
            email = row['email']
            password = row['password']
            
            # Generate username
            username = generate_username(name, email, user_id)
            
            # Hash password if needed
            hashed_password = hash_password(password)
            
            batch.append({
                'userId': user_id,
                'username': username,
                'name': name,
                'email': email,
                'password': hashed_password
            })
            
            if len(batch) >= batch_size:
                # Import batch
                query = """
                UNWIND $users AS user
                MERGE (u:User {userId: user.userId})
                ON CREATE SET 
                    u.username = user.username,
                    u.name = user.name,
                    u.email = user.email,
                    u.password = user.password,
                    u.bio = '',
                    u.createdAt = datetime()
                ON MATCH SET
                    u.username = user.username,
                    u.name = user.name,
                    u.email = user.email,
                    u.password = user.password
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
            ON CREATE SET 
                u.username = user.username,
                u.name = user.name,
                u.email = user.email,
                u.password = user.password,
                u.bio = '',
                u.createdAt = datetime()
            ON MATCH SET
                u.username = user.username,
                u.name = user.name,
                u.email = user.email,
                u.password = user.password
            """
            run(query, {'users': batch})
            users_imported += len(batch)
    
    print(f"\n✓ Imported {users_imported} users")
    return True

def import_follows():
    """Import follow relationships from follows.csv file."""
    print("Importing follow relationships from follows.csv...")
    
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
            MATCH (src:User {userId: f.srcUserId})
            MATCH (dst:User {userId: f.dstUserId})
            MERGE (src)-[r:FOLLOWS]->(dst)
            ON CREATE SET r.since = f.createdAt
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
    print("Generated User Data Import Script")
    print("Database: so-net")
    print("=" * 60)
    print()
    
    # Check if files exist
    if not os.path.exists(GEN_USERS_CSV):
        print(f"Error: gen_users.csv not found at {GEN_USERS_CSV}")
        sys.exit(1)
    
    if not os.path.exists(FOLLOWS_CSV):
        print(f"Error: follows.csv not found at {FOLLOWS_CSV}")
        sys.exit(1)
    
    print("⚠️  IMPORTANT: Make sure your backend/.env is configured for the 'so-net' database!")
    print("   Update NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD if needed.\n")
    
    # Import users
    if not import_gen_users():
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

