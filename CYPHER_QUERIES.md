# Cypher Queries Documentation

This document provides detailed documentation of all Cypher queries used in the Social Network API, organized by use case.

---

## Table of Contents

1. [Setup & Constraints](#setup--constraints)
2. [User Management (UC-1 to UC-4)](#user-management-uc-1-to-uc-4)
3. [Social Graph Features (UC-5 to UC-9)](#social-graph-features-uc-5-to-uc-9)
4. [Search & Exploration (UC-10 to UC-11)](#search--exploration-uc-10-to-uc-11)
5. [Additional Features](#additional-features)

---

## Setup & Constraints

### Database Constraints and Indexes

**Endpoint:** `POST/GET /admin/setup`

**Purpose:** Creates necessary constraints and indexes for data integrity and query performance.

**Queries:**

```cypher
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE
```

**Description:** Ensures that each `User` node has a unique `userId` property. This prevents duplicate user IDs and enables efficient lookups.

---

```cypher
CREATE CONSTRAINT username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE
```

**Description:** Ensures that each `User` node has a unique `username` property. This is critical for user authentication and profile lookups.

---

```cypher
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE
```

**Description:** Ensures that each `User` node has a unique `email` property. This prevents multiple accounts with the same email address.

---

```cypher
CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)
```

**Description:** Creates an index on the `name` property of `User` nodes to improve search performance when querying by name.

---

```cypher
CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.postId IS UNIQUE
```

**Description:** Ensures that each `Post` node has a unique `postId` property. This constraint is set up for future post functionality.

---

## User Management (UC-1 to UC-4)

### UC-1: User Registration

**Endpoint:** `POST /users/register`

**Purpose:** Creates a new user account in the database.

#### Query 1: Check Username Availability

```cypher
MATCH (u:User {username: $username}) 
RETURN u.username AS username
```

**Description:** Checks if a username already exists in the database. This query uses the unique username constraint to quickly find existing users.

**Parameters:**
- `$username` (string): The username to check

**Returns:**
- If username exists: Returns the username
- If username doesn't exist: Returns empty result

---

#### Query 2: Check Email Availability

```cypher
MATCH (u:User {email: $email}) 
RETURN u.email AS email
```

**Description:** Checks if an email address is already registered. This prevents duplicate accounts with the same email.

**Parameters:**
- `$email` (string): The email address to check

**Returns:**
- If email exists: Returns the email
- If email doesn't exist: Returns empty result

---

#### Query 3: Create New User

```cypher
CREATE (u:User {
    userId: randomUUID(),
    username: $username,
    name: $name,
    email: $email,
    password: $password,
    createdAt: datetime(),
    bio: ''
})
RETURN u { 
    .userId, .username, .name, .email, 
    bio: u.bio,
    createdAt: toString(u.createdAt) 
} AS user
```

**Description:** Creates a new `User` node with all required properties. The `userId` is generated using `randomUUID()` to ensure uniqueness. The `createdAt` timestamp is set to the current datetime, and `bio` is initialized as an empty string.

**Parameters:**
- `$username` (string): Unique username for the user
- `$name` (string): Full name of the user
- `$email` (string): Email address (must be unique)
- `$password` (string): Hashed password

**Returns:**
- A user object containing `userId`, `username`, `name`, `email`, `bio`, and `createdAt`

---

### UC-2: User Login

**Endpoint:** `POST /users/login`

**Purpose:** Authenticates a user by verifying username and password.

#### Query: Authenticate User

```cypher
MATCH (u:User {username: $username, password: $password})
RETURN u { 
    .userId, .username, .name, .email,
    bio: u.bio,
    createdAt: toString(u.createdAt) 
} AS user
```

**Description:** Matches a user node where both username and password match the provided credentials. The password should be hashed before comparison.

**Parameters:**
- `$username` (string): Username to authenticate
- `$password` (string): Hashed password to verify

**Returns:**
- If credentials are valid: Returns user object with profile information
- If credentials are invalid: Returns empty result

---

### UC-3: View Profile

**Endpoint:** `GET /users/{username}/profile`

**Purpose:** Retrieves a user's profile information including follower and following counts.

#### Query: Get User Profile with Counts

```cypher
MATCH (u:User {username: $username})
OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
RETURN u { 
    .userId, .username, .name, .email,
    bio: u.bio,
    createdAt: toString(u.createdAt) 
} AS user,
count(DISTINCT following) AS followingCount,
count(DISTINCT follower) AS followersCount
```

**Description:** 
- First, matches the user by username
- Uses `OPTIONAL MATCH` to find all users that the target user follows (outgoing `FOLLOWS` relationships)
- Uses `OPTIONAL MATCH` to find all users that follow the target user (incoming `FOLLOWS` relationships)
- Counts distinct following and followers to get the statistics
- Returns the user profile along with counts

**Parameters:**
- `$username` (string): Username of the profile to view

**Returns:**
- `user`: User object with profile information
- `followingCount`: Number of users this user follows
- `followersCount`: Number of users following this user

**Note:** `OPTIONAL MATCH` ensures that even if a user has no followers or following, the query still returns the user profile with counts of 0.

---

### UC-4: Edit Profile

**Endpoint:** `PUT /users/{username}/profile`

**Purpose:** Updates user profile information (name, email, or bio).

#### Query 1: Check Email Availability (for email updates)

```cypher
MATCH (u:User {email: $email})
WHERE u.username <> $username
RETURN u.username AS username
```

**Description:** When updating an email, this query checks if the new email is already taken by another user. The `WHERE` clause ensures we exclude the current user from the check.

**Parameters:**
- `$email` (string): The new email address to check
- `$username` (string): The username of the user updating their profile

**Returns:**
- If email is taken by another user: Returns that user's username
- If email is available: Returns empty result

---

#### Query 2: Update User Profile (Dynamic)

```cypher
MATCH (u:User {username: $username})
SET u.name = $name, u.email = $email, u.bio = $bio
RETURN u { 
    .userId, .username, .name, .email,
    bio: u.bio,
    createdAt: toString(u.createdAt) 
} AS user
```

**Description:** Dynamically updates user properties. The `SET` clause is built based on which fields are provided in the request. Only non-null fields are updated.

**Parameters:**
- `$username` (string): Username of the user to update
- `$name` (string, optional): New name (if provided)
- `$email` (string, optional): New email (if provided)
- `$bio` (string, optional): New bio (if provided)

**Returns:**
- Updated user object with all profile information

**Note:** The actual query is dynamically constructed in the application code, so only the fields that need updating are included in the `SET` clause.

---

## Social Graph Features (UC-5 to UC-9)

### UC-5: Follow Another User

**Endpoint:** `POST /users/{me}/follow/{other}`

**Purpose:** Creates a `FOLLOWS` relationship between two users.

#### Query: Create Follow Relationship

```cypher
MATCH (a:User {username:$me}),(b:User {username:$other})
MERGE (a)-[r:FOLLOWS]->(b)
ON CREATE SET r.since = datetime()
RETURN 'ok' AS ok
```

**Description:**
- Matches both the follower (`a`) and followee (`b`) by their usernames
- Uses `MERGE` to create a `FOLLOWS` relationship if it doesn't exist, or use the existing one if it does
- `ON CREATE SET` sets a `since` timestamp only when the relationship is newly created
- This makes the operation idempotent (safe to call multiple times)

**Parameters:**
- `$me` (string): Username of the user who wants to follow
- `$other` (string): Username of the user to be followed

**Returns:**
- `ok`: Confirmation string if successful

**Note:** The application code prevents users from following themselves.

---

### UC-6: Unfollow a User

**Endpoint:** `DELETE /users/{me}/follow/{other}`

**Purpose:** Removes a `FOLLOWS` relationship between two users.

#### Query: Delete Follow Relationship

```cypher
MATCH (a:User {username:$me})-[r:FOLLOWS]->(b:User {username:$other})
DELETE r
RETURN count(r) AS deleted
```

**Description:**
- Matches the specific `FOLLOWS` relationship from the current user to the target user
- Deletes the relationship
- Returns the count of deleted relationships (should be 1 if successful, 0 if relationship didn't exist)

**Parameters:**
- `$me` (string): Username of the user who wants to unfollow
- `$other` (string): Username of the user to be unfollowed

**Returns:**
- `deleted`: Number of relationships deleted (0 or 1)

---

### UC-7: View Friends/Connections

**Endpoint:** `GET /users/{username}/connections`

**Purpose:** Retrieves all users that a given user follows and all users that follow them.

#### Query: Get Following and Followers

```cypher
MATCH (u:User {username: $username})
OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
RETURN 
    collect(DISTINCT following {.username, .name, .bio}) AS following,
    collect(DISTINCT follower {.username, .name, .bio}) AS followers
```

**Description:**
- Matches the target user by username
- Uses `OPTIONAL MATCH` to find all users the target follows (outgoing relationships)
- Uses `OPTIONAL MATCH` to find all users that follow the target (incoming relationships)
- Uses `collect()` to aggregate all following and followers into lists
- Returns only `username`, `name`, and `bio` for each connection

**Parameters:**
- `$username` (string): Username of the user whose connections to retrieve

**Returns:**
- `following`: List of users that the target user follows
- `followers`: List of users that follow the target user

**Note:** Each item in the lists contains `username`, `name`, and `bio` properties.

---

### UC-8: Mutual Connections

**Endpoint:** `GET /users/{username}/mutual?other={other}`

**Purpose:** Finds users that both the current user and another user follow (mutual connections).

#### Query: Find Mutual Connections

```cypher
MATCH (u1:User {username: $username})-[:FOLLOWS]->(mutual)<-[:FOLLOWS]-(u2:User {username: $other})
RETURN mutual {.username, .name, .bio} AS user
```

**Description:**
- Matches user `u1` (current user) and user `u2` (other user) by their usernames
- Finds all nodes `mutual` where:
  - `u1` follows `mutual` (via `-[:FOLLOWS]->`)
  - `u2` also follows `mutual` (via `<-[:FOLLOWS]-`)
- The pattern `(u1)-[:FOLLOWS]->(mutual)<-[:FOLLOWS]-(u2)` represents the mutual connection structure
- Returns profile information for each mutual connection

**Parameters:**
- `$username` (string): Username of the first user
- `$other` (string): Username of the second user

**Returns:**
- List of user objects representing mutual connections, each containing `username`, `name`, and `bio`

**Example:** If Alice follows Bob and Charlie, and Bob also follows Charlie, then Charlie is a mutual connection between Alice and Bob.

---

### UC-9: Friend Recommendations

**Endpoint:** `GET /users/{me}/recommendations`

**Purpose:** Recommends users to follow based on "friends of friends" algorithm.

#### Query: Get Friend Recommendations

```cypher
MATCH (me:User {username:$me})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(cand:User)
WHERE NOT (me)-[:FOLLOWS]->(cand) AND me <> cand
RETURN cand.username AS username, cand.name AS name, cand.bio AS bio, count(*) AS score
ORDER BY score DESC 
LIMIT 10
```

**Description:**
- Finds users (`cand`) that are followed by users that the current user (`me`) follows
- The pattern `(me)-[:FOLLOWS]->(:User)-[:FOLLOWS]->(cand)` represents:
  - `me` follows some user (anonymous node `:User`)
  - That user follows `cand` (candidate for recommendation)
- `WHERE NOT (me)-[:FOLLOWS]->(cand)` excludes candidates that the user already follows
- `me <> cand` prevents recommending the user to themselves
- `count(*)` counts how many mutual connections lead to each candidate (higher count = stronger recommendation)
- Results are ordered by score (descending) and limited to top 10

**Parameters:**
- `$me` (string): Username of the user requesting recommendations

**Returns:**
- List of recommended users, each containing:
  - `username`: Username of the recommended user
  - `name`: Name of the recommended user
  - `bio`: Bio of the recommended user
  - `score`: Number of mutual connections (higher = better recommendation)

**Algorithm:** This implements a "friends of friends" recommendation system. Users with more mutual connections are ranked higher.

---

## Search & Exploration (UC-10 to UC-11)

### UC-10: Search Users

**Endpoint:** `GET /users/search?query={query}&limit={limit}`

**Purpose:** Searches for users by username or name.

#### Query: Search Users by Username or Name

```cypher
MATCH (u:User)
WHERE toLower(u.username) CONTAINS toLower($query) 
   OR toLower(u.name) CONTAINS toLower($query)
RETURN u {.username, .name, .bio} AS user
ORDER BY u.username
LIMIT $limit
```

**Description:**
- Matches all `User` nodes
- Uses `WHERE` clause with `CONTAINS` to perform case-insensitive substring matching
- `toLower()` converts both the property and query to lowercase for case-insensitive search
- Searches in both `username` and `name` fields using `OR`
- Results are ordered alphabetically by username
- Limited to the specified number of results

**Parameters:**
- `$query` (string): Search term to match against usernames and names
- `$limit` (integer): Maximum number of results to return (default: 20)

**Returns:**
- List of user objects matching the search query, each containing `username`, `name`, and `bio`

**Note:** This is a substring search, so searching for "john" will match "johnsmith", "john_doe", "Johnny", etc.

---

### UC-11: Explore Popular Users

**Endpoint:** `GET /users/popular?limit={limit}`

**Purpose:** Retrieves users sorted by their number of followers (popularity).

#### Query: Get Popular Users

```cypher
MATCH (u:User)<-[:FOLLOWS]-(follower)
WITH u, count(follower) AS followersCount
RETURN u {.username, .name, .bio} AS user, followersCount
ORDER BY followersCount DESC
LIMIT $limit
```

**Description:**
- Matches all `User` nodes and their incoming `FOLLOWS` relationships
- Uses `WITH` to aggregate and count followers for each user
- `count(follower)` counts the number of incoming `FOLLOWS` relationships
- Results are ordered by `followersCount` in descending order (most popular first)
- Limited to the specified number of results

**Parameters:**
- `$limit` (integer): Maximum number of results to return (default: 20)

**Returns:**
- List of user objects with their follower counts, each containing:
  - `user`: User object with `username`, `name`, and `bio`
  - `followersCount`: Number of followers

**Note:** Users with no followers will not appear in the results. If you want to include all users, you would need to use `OPTIONAL MATCH` and handle null counts.

---

## Additional Features

### User Feed

**Endpoint:** `GET /users/{me}/feed`

**Purpose:** Retrieves posts from users that the current user follows (for future post functionality).

#### Query: Get User Feed

```cypher
MATCH (me:User {username:$me})-[:FOLLOWS]->(u)-[:POSTED]->(p:Post)
RETURN u.username AS author, p.text AS text, p.createdAt AS createdAt
ORDER BY p.createdAt DESC
LIMIT 50
```

**Description:**
- Matches the current user (`me`) and finds all users they follow
- Traverses to posts created by those users via `-[:POSTED]->(p:Post)`
- Returns post information including author, text, and creation timestamp
- Results are ordered by creation time (newest first)
- Limited to 50 most recent posts

**Parameters:**
- `$me` (string): Username of the user requesting their feed

**Returns:**
- List of post objects, each containing:
  - `author`: Username of the post author
  - `text`: Content of the post
  - `createdAt`: Timestamp when the post was created

**Note:** This endpoint is set up for future functionality. Currently, there are no `Post` nodes or `POSTED` relationships in the database, so this will return an empty result.

---

## Query Patterns and Best Practices

### 1. Using MERGE for Idempotency

The `MERGE` clause is used in the follow endpoint to ensure operations can be safely repeated:
```cypher
MERGE (a)-[r:FOLLOWS]->(b)
ON CREATE SET r.since = datetime()
```

### 2. Using OPTIONAL MATCH for Optional Relationships

`OPTIONAL MATCH` is used when relationships might not exist:
```cypher
OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
```

This ensures the query returns results even if a user has no connections.

### 3. Using DISTINCT to Avoid Duplicates

`DISTINCT` is used when aggregating to prevent duplicate counts:
```cypher
count(DISTINCT following) AS followingCount
```

### 4. Using collect() for Aggregation

`collect()` is used to aggregate multiple nodes into a list:
```cypher
collect(DISTINCT following {.username, .name, .bio}) AS following
```

### 5. Pattern Matching for Graph Traversals

Complex graph patterns are used to find relationships:
```cypher
(u1)-[:FOLLOWS]->(mutual)<-[:FOLLOWS]-(u2)
```

This pattern finds nodes that are connected to both `u1` and `u2` via `FOLLOWS` relationships.

### 6. Case-Insensitive Search

`toLower()` is used for case-insensitive string matching:
```cypher
WHERE toLower(u.username) CONTAINS toLower($query)
```

### 7. Dynamic Query Construction

For the update profile endpoint, queries are dynamically constructed based on which fields need updating. This is handled in the application code, not in Cypher directly.

---

## Performance Considerations

1. **Constraints and Indexes**: The setup creates unique constraints on `userId`, `username`, and `email`, and an index on `name`. These significantly improve lookup performance.

2. **LIMIT Clauses**: All search and exploration queries use `LIMIT` to prevent returning excessive results and improve response times.

3. **Pattern Matching**: The graph patterns used are optimized for Neo4j's traversal engine. Directional relationships (`->` and `<-`) help the query planner optimize execution.

4. **Aggregation**: Using `WITH` clauses for aggregation before final `RETURN` helps reduce intermediate result sets.

---

## Notes

- All timestamps use Neo4j's `datetime()` function, which returns a datetime object. When returning to the API, these are converted to strings using `toString()`.

- Password hashing is handled in the application code (using SHA-256), not in Cypher queries.

- The queries use parameterized inputs (`$param`) to prevent Cypher injection attacks and improve query plan caching.

- All user-facing queries return sanitized data (excluding sensitive information like passwords).

