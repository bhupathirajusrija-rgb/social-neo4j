# Social Network Neo4j Project

A full-stack social network application built with **FastAPI** (backend) and **React + Vite** (frontend), using **Neo4j** as the graph database. This project implements 11 use cases for social network functionality including user management, social graph features, and search capabilities.

## Features

### User Management
- **UC-1:** User Registration with email and password
- **UC-2:** User Login and authentication
- **UC-3:** View User Profile
- **UC-4:** Edit User Profile (name, email, bio)

### Social Graph Features
- **UC-5:** Follow Another User
- **UC-6:** Unfollow a User
- **UC-7:** View Friends/Connections (following and followers)
- **UC-8:** Mutual Connections (find common friends)
- **UC-9:** Friend Recommendations (graph-based suggestions)

### Search & Exploration
- **UC-10:** Search Users by username or name
- **UC-11:** Explore Popular Users (most followed)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** and **npm** ([Download](https://nodejs.org/))
- **Neo4j Desktop** ([Download](https://neo4j.com/download/))
- **Git** (for version control)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/bhupathirajusrija-rgb/social-neo4j.git
cd social-neo4j
```

### 2. Neo4j Database Setup

1. **Install and Open Neo4j Desktop**
   - Download from [neo4j.com/download](https://neo4j.com/download/)
   - Install and launch Neo4j Desktop

2. **Create a New Database**
   - Click "Add Database" or "New Database"
   - Name it (e.g., "social-network")
   - Set a password (remember this for later!)
   - Click "Create"

3. **Start the Database**
   - Click the play button (▶️) next to your database
   - Wait for it to show "RUNNING" status

4. **Note Connection Details**
   - Click the three dots (⋯) next to your database
   - Select "Details" or "Connection Details"
   - Note the URI (usually `bolt://localhost:7687`)
   - Username is typically `neo4j`
   - Password is what you set when creating the database

### 3. Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file:**
   ```bash
   # Create .env file in backend directory
   cat > .env << EOF
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password_here
   EOF
   ```
   
   **Important:** Replace `your_password_here` with your actual Neo4j database password!

6. **Start the backend server:**
   ```bash
   uvicorn app:app --reload --port 8000
   ```
   
   The API will be available at `http://localhost:8000`

7. **Initialize Database Constraints:**
   - Visit `http://localhost:8000/admin/setup` in your browser
   - Or use curl: `curl -X POST http://localhost:8000/admin/setup`
   - This creates necessary constraints and indexes (run once)

### 4. Frontend Setup

1. **Open a new terminal** (keep backend running)

2. **Navigate to app directory:**
   ```bash
   cd app
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Create environment file:**
   ```bash
   # Create .env.local file in app directory
   cat > .env.local << EOF
   VITE_API_BASE=http://localhost:8000
   EOF
   ```

5. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173` (or the port shown)

### 5. Import Sample Data (Optional)

The project includes sample data that exceeds the minimum requirements:
- **4,040 users** (nodes)
- **176,469 follow relationships** (edges)

To import the data:

```bash
# In backend directory with venv activated
cd backend
source venv/bin/activate  # if not already activated

# Import main dataset
python import_data.py

# Or import generated users dataset
python import_gen_data.py
```

## Project Structure

```
social-neo4j/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main API application
│   ├── db.py               # Neo4j database connection
│   ├── import_data.py      # Import script for users.csv
│   ├── import_gen_data.py  # Import script for gen_users.csv
│   ├── import_celebrities.py # Import script for celebrities
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Neo4j connection config (create this)
│
├── app/                    # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── App.css        # Styles
│   │   ├── api.js         # API client functions
│   │   ├── main.jsx       # React entry point
│   │   └── index.css      # Global styles
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.js     # Vite configuration
│   └── .env.local         # Frontend config (create this)
│
├── data/                   # Dataset files
│   ├── users.csv          # Main user dataset
│   ├── follows.csv        # Follow relationships
│   ├── gen_users.csv     # Generated users dataset
│   ├── celebrities.csv    # Celebrity users
│   └── celebrities_follows.csv # Celebrity relationships
│
├── DATASET_DOCUMENTATION.md  # Dataset information
├── IMPORT_INSTRUCTIONS.md    # Detailed import guide
├── setup.sh                  # Automated setup script
└── README.md                  # This file
```

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

### Frontend Configuration (`app/.env.local`)

```env
VITE_API_BASE=http://localhost:8000
```

## API Endpoints

### Health & Setup
- `GET /health` - Health check
- `GET/POST /admin/setup` - Initialize database constraints

### User Management
- `POST /users/register` - Register a new user
- `POST /users/login` - User login
- `GET /users/{username}/profile` - Get user profile
- `PUT /users/{username}/profile` - Update user profile

### Social Graph
- `POST /users/{me}/follow/{other}` - Follow a user
- `DELETE /users/{me}/follow/{other}` - Unfollow a user
- `GET /users/{username}/connections` - Get following/followers
- `GET /users/{username}/mutual?other={other}` - Get mutual connections
- `GET /users/{me}/recommendations` - Get friend recommendations

### Search & Exploration
- `GET /users/search?query={query}` - Search users
- `GET /users/popular?limit={limit}` - Get popular users
- `GET /users/{me}/feed` - Get user feed

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

##  Usage

### Using the Frontend

1. **Register a New User:**
   - Go to "UC-1: Register" tab
   - Fill in username, name, email, and password
   - Click "Register"

2. **Login:**
   - Go to "UC-2: Login" tab
   - Enter username and password
   - Click "Login"

3. **Explore Features:**
   - View and edit your profile
   - Follow other users
   - Get recommendations
   - Search for users
   - View popular users
   - See mutual connections

### Using the API Directly

You can test the API using:
- **Swagger UI:** Visit `http://localhost:8000/docs`
- **curl:** Use curl commands in terminal
- **Postman:** Import the API endpoints

## 📊 Dataset Information

This project uses a social network dataset with:
- **4,040 users** (nodes)
- **176,469 follow relationships** (edges)

The dataset follows the structure of SNAP Twitter follower networks. See `DATASET_DOCUMENTATION.md` for detailed information.

##  Development

### Running in Development Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

**Frontend:**
```bash
cd app
npm run dev
```

### Building for Production

**Frontend:**
```bash
cd app
npm run build
```

The built files will be in `app/dist/`

##  Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Verify Neo4j Desktop is running
   - Check database is started
   - Verify `.env` file has correct credentials
   - Check URI format (should be `bolt://localhost:7687`)

2. **Port Already in Use:**
   - Backend: Change port in uvicorn command: `--port 8001`
   - Frontend: Vite will automatically use next available port

3. **CORS Errors:**
   - Ensure backend CORS is configured (already set up)
   - Check frontend `.env.local` has correct API URL

4. **Import Errors:**
   - Make sure database constraints are initialized (`/admin/setup`)
   - Verify CSV files exist in `data/` directory
   - Check file formats match expected structure

5. **Module Not Found:**
   - Backend: Ensure virtual environment is activated
   - Frontend: Run `npm install` again

##  Scripts

### Automated Setup

Run the setup script for automated setup:

```bash
chmod +x setup.sh
./setup.sh
```

Then edit `backend/.env` with your Neo4j credentials.

### Import Scripts

- `python backend/import_data.py` - Import users.csv and follows.csv
- `python backend/import_gen_data.py` - Import gen_users.csv and follows.csv
- `python backend/import_celebrities.py` - Import celebrity data

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Test User Registration

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

##  Documentation

- **Dataset Documentation:** See `DATASET_DOCUMENTATION.md`
- **Import Instructions:** See `IMPORT_INSTRUCTIONS.md`
- **API Documentation:** Visit `http://localhost:8000/docs` when server is running

##  License

This project is for educational purposes.

## 🙏 Acknowledgments

- **Neo4j** for the graph database platform
- **FastAPI** for the modern Python web framework
- **React** and **Vite** for the frontend framework
- **SNAP Datasets** for dataset structure reference

**Commit early, regret often**
