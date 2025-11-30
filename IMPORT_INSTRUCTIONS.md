# Import Instructions for so-net Database

## Step 1: Configure Database Connection

Update your `backend/.env` file to connect to the **so-net** database:

```bash
cd backend
nano .env  # or use your preferred editor
```

Make sure it contains:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_so_net_database_password
```

**Important:** 
- The URI should point to your Neo4j instance (usually `bolt://localhost:7687`)
- Use the username and password for your **so-net** database
- You can find these in Neo4j Desktop by clicking on your so-net database → Details

## Step 2: Initialize Database Constraints

Before importing data, initialize the database constraints:

```bash
# Make sure your backend server is running, then:
curl -X POST http://localhost:8000/admin/setup
```

Or visit: `http://localhost:8000/admin/setup` in your browser.

This creates:
- Unique constraints on userId, username, and email
- Indexes on user names
- Post constraints (for future use)

## Step 3: Import Data

Run the import script:

```bash
cd backend
source venv/bin/activate
python import_gen_data.py
```

This will:
1. Import users from `data/gen_users.csv`
   - Generates usernames from names/emails
   - Hashes passwords
   - Creates User nodes with: userId, username, name, email, password, bio
   
2. Import follow relationships from `data/follows.csv`
   - Creates FOLLOWS relationships between users
   - Sets timestamps on relationships

## Step 4: Verify Import

After import, you can verify the data:

```cypher
// Count users
MATCH (u:User)
RETURN count(u) AS totalUsers

// Count relationships
MATCH ()-[f:FOLLOWS]->()
RETURN count(f) AS totalFollows

// Check a sample user
MATCH (u:User {userId: "0"})
RETURN u
```

## Troubleshooting

### Connection Issues
- Make sure Neo4j Desktop is running
- Verify the so-net database is started
- Check that your .env file has the correct credentials

### Import Errors
- Make sure constraints are initialized (Step 2)
- Check that CSV files exist in the `data/` directory
- Verify CSV file format matches expected structure

### Username Conflicts
- The script generates usernames automatically
- If conflicts occur, the script will update existing users
- Check the import output for any warnings

## Data Structure

### gen_users.csv Format:
```csv
id,name,email,password
0,Jennifer Perez,jennifer.perez.0@example.com,BO6vtaqLMV
1,Ashley Gonzalez,ashley.gonzalez.1@example.com,5Q3RTAXC2C
...
```

### follows.csv Format:
```csv
srcUserId,dstUserId,createdAt
0,1,2025-11-14T00:02:22.858924Z
1,0,2025-11-14T00:02:22.858924Z
...
```

## Expected Results

After successful import:
- All users from gen_users.csv will be in the database
- All follow relationships from follows.csv will be created
- Users will have generated usernames (e.g., "jenniferp0", "ashleyg1")
- Passwords will be hashed and stored securely
- Relationships will have timestamps

