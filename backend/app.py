from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from db import run
import hashlib
import re

app = FastAPI(title="Social Network API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# ---- Helper Functions ----
def hash_password(password: str) -> str:
    """Simple password hashing (for demo purposes)"""
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Models ----
def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class RegisterIn(BaseModel):
    username: str
    name: str
    email: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class UpdateProfileIn(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None

# ---- Health ----
@app.get("/health")
def health():
    recs = run("RETURN 1 AS ok")
    return {"status": "ok", "db": recs[0]["ok"] == 1}

# ---- Setup: constraints you can call once ----
@app.post("/admin/setup")
@app.get("/admin/setup")
def setup():
    queries = [
        "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE",
        "CREATE CONSTRAINT username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
        "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
        "CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)",
        "CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.postId IS UNIQUE",
    ]
    for q in queries:
        run(q)
    return {"status": "created_or_exists"}

# ---- User Management (UC-1 to UC-4) ----
@app.post("/users/register")
def register_user(data: RegisterIn):
    """UC-1: User Registration"""
    # Validate email
    if not validate_email(data.email):
        raise HTTPException(400, "Invalid email format")
    
    # Check if username already exists
    check_q = "MATCH (u:User {username: $username}) RETURN u.username AS username"
    existing = run(check_q, {"username": data.username})
    if existing:
        raise HTTPException(400, "Username already exists")
    
    # Check if email already exists
    check_email_q = "MATCH (u:User {email: $email}) RETURN u.email AS email"
    existing_email = run(check_email_q, {"email": data.email})
    if existing_email:
        raise HTTPException(400, "Email already registered")
    
    q = """
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
    """
    rows = run(q, {
        "username": data.username,
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password)
    })
    if not rows:
        raise HTTPException(500, "Failed to create user")
    return rows[0]["user"]

@app.post("/users/login")
def login_user(data: LoginIn):
    """UC-2: User Login"""
    q = """
    MATCH (u:User {username: $username, password: $password})
    RETURN u { 
        .userId, .username, .name, .email,
        bio: u.bio,
        createdAt: toString(u.createdAt) 
    } AS user
    """
    rows = run(q, {
        "username": data.username,
        "password": hash_password(data.password)
    })
    if not rows:
        raise HTTPException(401, "Invalid username or password")
    return rows[0]["user"]

@app.get("/users/{username}/profile")
def get_profile(username: str):
    """UC-3: View Profile"""
    q = """
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
    """
    rows = run(q, {"username": username})
    if not rows:
        raise HTTPException(404, "User not found")
    result = rows[0]
    user = result["user"]
    user["followingCount"] = result["followingCount"]
    user["followersCount"] = result["followersCount"]
    return user

@app.put("/users/{username}/profile")
def update_profile(username: str, data: UpdateProfileIn):
    """UC-4: Edit Profile"""
    # Build dynamic update query
    updates = []
    params = {"username": username}
    
    if data.name is not None:
        updates.append("u.name = $name")
        params["name"] = data.name
    
    if data.email is not None:
        # Validate email
        if not validate_email(data.email):
            raise HTTPException(400, "Invalid email format")
        # Check if email is already taken by another user
        check_q = """
        MATCH (u:User {email: $email})
        WHERE u.username <> $username
        RETURN u.username AS username
        """
        existing = run(check_q, {"email": data.email, "username": username})
        if existing:
            raise HTTPException(400, "Email already registered to another user")
        updates.append("u.email = $email")
        params["email"] = data.email
    
    if data.bio is not None:
        updates.append("u.bio = $bio")
        params["bio"] = data.bio
    
    if not updates:
        raise HTTPException(400, "No fields to update")
    
    q = f"""
    MATCH (u:User {{username: $username}})
    SET {', '.join(updates)}
    RETURN u {{ 
        .userId, .username, .name, .email,
        bio: u.bio,
        createdAt: toString(u.createdAt) 
    }} AS user
    """
    rows = run(q, params)
    if not rows:
        raise HTTPException(404, "User not found")
    return rows[0]["user"]

# ---- Social Graph Features (UC-5 to UC-9) ----
@app.post("/users/{me}/follow/{other}")
def follow(me: str, other: str):
    """UC-5: Follow Another User"""
    if me == other:
        raise HTTPException(400, "Cannot follow yourself")
    q = """
    MATCH (a:User {username:$me}),(b:User {username:$other})
    MERGE (a)-[r:FOLLOWS]->(b)
    ON CREATE SET r.since = datetime()
    RETURN 'ok' AS ok
    """
    result = run(q, {"me": me, "other": other})
    if not result:
        raise HTTPException(404, "One or both users not found")
    return {"status": "ok"}

@app.delete("/users/{me}/follow/{other}")
def unfollow(me: str, other: str):
    """UC-6: Unfollow a User"""
    q = """
    MATCH (a:User {username:$me})-[r:FOLLOWS]->(b:User {username:$other})
    DELETE r
    RETURN count(r) AS deleted
    """
    result = run(q, {"me": me, "other": other})
    if not result or result[0]["deleted"] == 0:
        raise HTTPException(404, "Follow relationship not found")
    return {"status": "ok"}

@app.get("/users/{username}/connections")
def get_connections(username: str):
    """UC-7: View Friends/Connections"""
    q = """
    MATCH (u:User {username: $username})
    OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
    OPTIONAL MATCH (follower)-[:FOLLOWS]->(u)
    RETURN 
        collect(DISTINCT following {.username, .name, .bio}) AS following,
        collect(DISTINCT follower {.username, .name, .bio}) AS followers
    """
    rows = run(q, {"username": username})
    if not rows:
        raise HTTPException(404, "User not found")
    result = rows[0]
    return {
        "following": [f for f in result["following"] if f.get("username")],
        "followers": [f for f in result["followers"] if f.get("username")]
    }

@app.get("/users/{username}/mutual")
def get_mutual_connections(username: str, other: str):
    """UC-8: Mutual Connections"""
    q = """
    MATCH (u1:User {username: $username})-[:FOLLOWS]->(mutual)<-[:FOLLOWS]-(u2:User {username: $other})
    RETURN mutual {.username, .name, .bio} AS user
    """
    rows = run(q, {"username": username, "other": other})
    return [r["user"] for r in rows]

@app.get("/users/{me}/recommendations")
def recommendations(me: str):
    """UC-9: Friend Recommendations"""
    q = """
    MATCH (me:User {username:$me})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(cand:User)
    WHERE NOT (me)-[:FOLLOWS]->(cand) AND me <> cand
    RETURN cand.username AS username, cand.name AS name, cand.bio AS bio, count(*) AS score
    ORDER BY score DESC LIMIT 10
    """
    rows = run(q, {"me": me})
    return [{"username": r["username"], "name": r.get("name", ""), "bio": r.get("bio", ""), "score": int(r["score"])} for r in rows]

# ---- Search & Exploration (UC-10 to UC-11) ----
@app.get("/users/search")
def search_users(query: str, limit: int = 20):
    """UC-10: Search Users"""
    q = """
    MATCH (u:User)
    WHERE toLower(u.username) CONTAINS toLower($query) 
       OR toLower(u.name) CONTAINS toLower($query)
    RETURN u {.username, .name, .bio} AS user
    ORDER BY u.username
    LIMIT $limit
    """
    rows = run(q, {"query": query, "limit": limit})
    return [r["user"] for r in rows]

@app.get("/users/popular")
def get_popular_users(limit: int = 20):
    """UC-11: Explore Popular Users"""
    q = """
    MATCH (u:User)<-[:FOLLOWS]-(follower)
    WITH u, count(follower) AS followersCount
    RETURN u {.username, .name, .bio} AS user, followersCount
    ORDER BY followersCount DESC
    LIMIT $limit
    """
    rows = run(q, {"limit": limit})
    return [{"user": r["user"], "followersCount": r["followersCount"]} for r in rows]

@app.get("/users/{me}/feed")
def feed(me: str):
    q = """
    MATCH (me:User {username:$me})-[:FOLLOWS]->(u)-[:POSTED]->(p:Post)
    RETURN u.username AS author, p.text AS text, p.createdAt AS createdAt
    ORDER BY p.createdAt DESC
    LIMIT 50
    """
    rows = run(q, {"me": me})
    return [dict(r) for r in rows]

