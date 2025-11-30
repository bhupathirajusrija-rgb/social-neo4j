import os
from typing import Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()  # loads from backend/.env

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    raise RuntimeError("Missing Neo4j env vars. Check backend/.env")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run(query: str, params: Optional[dict] = None):
    with driver.session() as session:
        return list(session.run(query, params or {}))

