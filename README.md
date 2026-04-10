# social-neo4j

> A NoSQL project modeling a social network using Neo4j graph database and Python.

## Overview

This project explores graph database concepts by building a social network data model with [Neo4j](https://neo4j.com/). It uses Python to interact with the database, demonstrating how graph databases handle relationships more naturally than traditional relational databases.

## Features

- Social graph modeling (users, relationships, connections)
- Python-based database interaction via the Neo4j driver
- Cypher query examples for traversing the social graph
- Demonstrates NoSQL/graph DB concepts for a course or personal project

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic & DB interaction |
| Neo4j | Graph database |
| Cypher | Query language for Neo4j |

## Prerequisites

- Python 3.8+
- Neo4j Desktop or Neo4j Aura (cloud)
- `neo4j` Python driver

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/bhupathirajusrija-rgb/social-neo4j.git
cd social-neo4j
```

2. **Install dependencies**

```bash
pip install neo4j
```

3. **Set up Neo4j**

   - Download [Neo4j Desktop](https://neo4j.com/download/) or use [Neo4j Aura](https://neo4j.com/cloud/platform/aura-graph-database/)
   - Start a new database instance
   - Note your connection URI, username, and password

4. **Configure connection**

   Update the connection details in the script (or create a `.env` file):

```python
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "your_password"
```

## Usage

Run the main script to populate and query the social graph:

```bash
python main.py
```

## Example Queries (Cypher)

```cypher
-- Find all friends of a user
MATCH (u:User {name: "Alice"})-[:FRIENDS_WITH]->(friend)
RETURN friend.name

-- Find mutual friends between two users
MATCH (a:User {name: "Alice"})-[:FRIENDS_WITH]->(mutual)<-[:FRIENDS_WITH]-(b:User {name: "Bob"})
RETURN mutual.name

-- Shortest path between two users
MATCH path = shortestPath((a:User {name: "Alice"})-[*]-(b:User {name: "Bob"}))
RETURN path
```

## Project Structure

```
social-neo4j/
├── main.py          # Entry point
├── db.py            # Neo4j connection & query helpers
├── models.py        # Data model definitions
├── queries.py       # Cypher query functions
└── README.md        # Documentation
```

## Author

**Srija Bhupathiraju** — [@bhupathirajusrija-rgb](https://github.com/bhupathirajusrija-rgb)
