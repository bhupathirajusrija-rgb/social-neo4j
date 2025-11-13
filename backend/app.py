from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import run

app = FastAPI(title="Social Network API", version="0.1.0")

# ---- Models ----
class RegisterIn(BaseModel):
    username: str
    name: str

# ---- Health ----
@app.get("/health")
def health():
    recs = run("RETURN 1 AS ok")
    return {"status": "ok", "db": recs[0]["ok"] == 1}

# ---- Setup: constraints you can call once ----
@app.post("/admin/setup")
def setup():
    queries = [
        "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE",
        "CREATE CONSTRAINT username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
        "CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)",
        "CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.postId IS UNIQUE",
    ]
    for q in queries:
        run(q)
    return {"status": "created_or_exists"}

# ---- Core endpoints ----
@app.post("/users/register")
def register_user(data: RegisterIn):
    q = """
    MERGE (u:User {username:$username})
    ON CREATE SET u.userId = randomUUID(), u.name = $name, u.createdAt = datetime()
    RETURN u { .userId, .username, .name, createdAt: toString(u.createdAt) } AS user
    """
    rows = run(q, data.dict())
    if not rows:
        raise HTTPException(500, "Failed to create or fetch user")
    return rows[0]["user"]

@app.post("/users/{me}/follow/{other}")
def follow(me: str, other: str):
    q = """
    MATCH (a:User {username:$me}),(b:User {username:$other})
    MERGE (a)-[r:FOLLOWS]->(b)
    ON CREATE SET r.since = datetime()
    RETURN 'ok' AS ok
    """
    run(q, {"me": me, "other": other})
    return {"status": "ok"}

@app.delete("/users/{me}/follow/{other}")
def unfollow(me: str, other: str):
    q = """
    MATCH (a:User {username:$me})-[r:FOLLOWS]->(b:User {username:$other})
    DELETE r
    """
    run(q, {"me": me, "other": other})
    return {"status": "ok"}

@app.get("/users/{me}/recommendations")
def recommendations(me: str):
    q = """
    MATCH (me:User {username:$me})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(cand:User)
    WHERE NOT (me)-[:FOLLOWS]->(cand) AND me <> cand
    RETURN cand.username AS username, count(*) AS score
    ORDER BY score DESC LIMIT 10
    """
    rows = run(q, {"me": me})
    return [{"username": r["username"], "score": int(r["score"])} for r in rows]

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

