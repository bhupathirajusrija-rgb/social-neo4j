# Dataset Information

## 1. Dataset Name and URL

**Dataset Name:** Social Network Graph Dataset (Based on SNAP Twitter Follower Network Structure)

**Primary Reference Dataset:**
- **SNAP Twitter Follower Network Dataset**
- **URL:** https://snap.stanford.edu/data/twitter_combined.txt.gz
- **Description:** This dataset contains Twitter follower relationships. Our implementation uses a similar structure but with expanded synthetic data to meet scale requirements.

**Alternative Public Datasets (Similar Structure):**
- **SNAP Social Networks:** https://snap.stanford.edu/data/#socnets
  - Twitter Social Circles: https://snap.stanford.edu/data/egonets-Twitter.html
  - Google+ Social Circles: https://snap.stanford.edu/data/egonets-Gplus.html
- **Kaggle Social Network Datasets:** https://www.kaggle.com/datasets?search=social+network
- **Network Repository:** http://networkrepository.com/soc.php

**Our Dataset:**
- **Structure:** Based on SNAP Twitter follower network format (directed graph with user nodes and follow edges)
- **Scale:** Expanded to 4,040 users and 176,469 follow relationships (exceeds minimum requirements)
- **Format:** CSV files compatible with Neo4j import
- **Characteristics:**
  - User nodes with unique identifiers
  - Directed follow relationships (edges)
  - Timestamped relationship creation
  - Real-world network patterns (bidirectional follows, varying degrees)

## 2. Dataset Description

### Overview
This dataset represents a social network graph with users and their follow relationships. The dataset is designed to demonstrate graph database capabilities for social network analysis, including friend recommendations, mutual connections, and network traversal queries.

### Dataset Statistics
- **Nodes (Users):** 4,040
- **Edges (Follow Relationships):** 176,469
- **Average Degree:** ~43.7 (average connections per user)
- **Format:** CSV files

### Data Structure

#### Users Dataset (`users.csv`)
- **Columns:**
  - `userId`: Unique numeric identifier for each user
  - `username`: Unique username (e.g., "user_0", "user_1")
  - `name`: Display name (e.g., "User 0", "User 1")
- **Size:** 4,040 rows (including header)
- **Characteristics:**
  - Each user has a unique userId and username
  - Sequential user IDs from 0 to 4,039

#### Follows Dataset (`follows.csv`)
- **Columns:**
  - `srcUserId`: Source user ID (who follows)
  - `dstUserId`: Destination user ID (who is followed)
  - `createdAt`: ISO 8601 timestamp of when the relationship was created
- **Size:** 176,469 rows (including header)
- **Characteristics:**
  - Directed relationships (A follows B does not imply B follows A)
  - Some bidirectional relationships exist
  - All relationships have timestamps

### Additional Celebrity Dataset
- **Celebrities:** 50 Hollywood celebrities with bios and follow relationships
- **Celebrity Follows:** 207 additional follow relationships between celebrities
- **Purpose:** Demonstrates real-world use case with recognizable names

## 3. Data Processing and Loading

### Raw Data Format (SNAP Reference)

The SNAP Twitter dataset uses a simple edge list format:
```
user_id_1 user_id_2
user_id_3 user_id_4
...
```

### Processing Steps

1. **Data Generation/Expansion:**
   - Generated synthetic user data following SNAP dataset structure
   - Created 4,040 unique users with sequential IDs (0-4039)
   - Generated usernames in format "user_{id}" and names "User {id}"
   - Created follow relationships following real-world social network patterns:
     - Some bidirectional relationships (mutual follows)
     - Varying node degrees (some users more popular than others)
     - Timestamped relationship creation

2. **Data Transformation:**
   - Converted edge list format to structured CSV with headers
   - Split into two files: `users.csv` (nodes) and `follows.csv` (edges)
   - Added metadata: user names, relationship timestamps
   - Validated data integrity:
     - No duplicate usernames/userIds
     - All relationship endpoints reference valid users
     - Timestamp format validation (ISO 8601)

3. **CSV Structure:**
   - **users.csv:** `userId,username,name`
   - **follows.csv:** `srcUserId,dstUserId,createdAt`

4. **Import Process:**
   - Used batch processing for efficiency:
     - 100 users per batch
     - 500 relationships per batch
   - Implemented error handling for constraint violations
   - Used MERGE operations to handle duplicates gracefully
   - Progress tracking and statistics reporting

### Loading Scripts

#### Main Dataset Import (`backend/import_data.py`)
- Reads `data/users.csv` and `data/follows.csv`
- Processes data in batches for performance
- Creates User nodes and FOLLOWS relationships

#### Celebrity Dataset Import (`backend/import_celebrities.py`)
- Reads `data/celebrities.csv` and `data/celebrities_follows.csv`
- Generates unique UUIDs for new users
- Handles email, password, and bio fields
- Skips existing users to avoid conflicts

### Database Constraints Setup

Before importing data, database constraints and indexes are created:

```cypher
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE;
CREATE CONSTRAINT username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE;
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name);
CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.postId IS UNIQUE;
```

## 4. Cypher Statements Used

### 4.1 User Node Creation

**Batch User Import:**
```cypher
UNWIND $users AS user
MERGE (u:User {userId: user.userId})
SET u.username = user.username,
    u.name = user.name
```

**Explanation:** 
- Uses `UNWIND` to process batch of users
- `MERGE` ensures user is created only if doesn't exist (based on userId)
- Sets username and name properties

### 4.2 Follow Relationship Creation

**Batch Follow Relationship Import:**
```cypher
UNWIND $follows AS f
MATCH (src:User {userId: f.srcUserId})
MATCH (dst:User {userId: f.dstUserId})
MERGE (src)-[r:FOLLOWS]->(dst)
ON CREATE SET r.since = datetime(f.createdAt)
```

**Explanation:**
- Matches source and destination users by userId
- Creates FOLLOWS relationship if it doesn't exist
- Sets `since` property with timestamp on creation

### 4.3 Celebrity User Creation (with Extended Schema)

**Celebrity Import with Email, Password, Bio:**
```cypher
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
```

**Explanation:**
- Uses username as merge key (avoids userId conflicts)
- Generates UUID for userId on creation
- Updates existing users with new information if they exist

### 4.4 Data Verification Queries

**Count Total Users:**
```cypher
MATCH (u:User)
RETURN count(u) AS totalUsers
```

**Count Total Follow Relationships:**
```cypher
MATCH ()-[f:FOLLOWS]->()
RETURN count(f) AS totalFollows
```

**Get User Statistics:**
```cypher
MATCH (u:User)
WITH count(u) AS user_count
MATCH ()-[f:FOLLOWS]->()
WITH user_count, count(f) AS follow_count
RETURN user_count, follow_count
```

**Find Most Followed Users:**
```cypher
MATCH (u:User)<-[:FOLLOWS]-(follower)
RETURN u.username, count(follower) AS followers
ORDER BY followers DESC
LIMIT 10
```

**Find Users with Most Followings:**
```cypher
MATCH (u:User)-[:FOLLOWS]->(following)
RETURN u.username, count(following) AS following_count
ORDER BY following_count DESC
LIMIT 10
```

### 4.5 Application Query Examples

**Friend Recommendations (UC-9):**
```cypher
MATCH (me:User {username:$me})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(cand:User)
WHERE NOT (me)-[:FOLLOWS]->(cand) AND me <> cand
RETURN cand.username AS username, cand.name AS name, cand.bio AS bio, count(*) AS score
ORDER BY score DESC LIMIT 10
```

**Mutual Connections (UC-8):**
```cypher
MATCH (u1:User {username: $username})-[:FOLLOWS]->(mutual)<-[:FOLLOWS]-(u2:User {username: $other})
RETURN mutual {.username, .name, .bio} AS user
```

**View Connections (UC-7):**
```cypher
MATCH (u:User {username: $username})
OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
RETURN 
    collect(DISTINCT following {.username, .name, .bio}) AS following,
    collect(DISTINCT follower {.username, .name, .bio}) AS followers
```

**Search Users (UC-10):**
```cypher
MATCH (u:User)
WHERE toLower(u.username) CONTAINS toLower($query) 
   OR toLower(u.name) CONTAINS toLower($query)
RETURN u {.username, .name, .bio} AS user
ORDER BY u.username
LIMIT $limit
```

**Popular Users (UC-11):**
```cypher
MATCH (u:User)<-[:FOLLOWS]-(follower)
WITH u, count(follower) AS followersCount
RETURN u {.username, .name, .bio} AS user, followersCount
ORDER BY followersCount DESC
LIMIT $limit
```

## 5. Dataset Compliance

### Requirements Met:
✅ **Minimum 1,000 nodes:** 4,040 users (exceeds requirement by 4x)
✅ **Minimum 5,000 relationships:** 176,469 follow relationships (exceeds requirement by 35x)
✅ **Public dataset structure:** Follows standard social network dataset format
✅ **Graph database appropriate:** Directed graph with nodes and edges
✅ **Real-world patterns:** Includes bidirectional follows, varying degrees, timestamps

### Dataset Quality:
- **Completeness:** All users have required fields
- **Consistency:** All relationships reference valid user IDs
- **Uniqueness:** Enforced through database constraints
- **Timestamps:** All relationships have creation timestamps

## 6. Import Instructions

### Prerequisites:
1. Neo4j database running and accessible
2. Database constraints initialized (run `/admin/setup` endpoint)
3. Python environment with required packages

### Import Steps:

1. **Initialize Database Constraints:**
   ```bash
   curl -X POST http://localhost:8000/admin/setup
   ```

2. **Import Main Dataset:**
   ```bash
   cd backend
   source venv/bin/activate
   python import_data.py
   ```

3. **Import Celebrity Dataset (Optional):**
   ```bash
   python import_celebrities.py
   ```

### Expected Output:
- Main dataset: ~4,040 users, ~176,469 relationships
- Celebrity dataset: ~50 users, ~207 relationships
- Total: ~4,090 users, ~176,676 relationships

## 7. References

- **Neo4j Cypher Manual:** https://neo4j.com/docs/cypher-manual/
- **SNAP Datasets:** https://snap.stanford.edu/data/
- **Graph Database Use Cases:** https://neo4j.com/use-cases/

## 8. Dataset Files

All dataset files are located in the `data/` directory:

- `users.csv` - Main user dataset (4,040 users)
- `follows.csv` - Follow relationships (176,469 relationships)
- `celebrities.csv` - Celebrity users (50 users)
- `celebrities_follows.csv` - Celebrity follow relationships (207 relationships)

