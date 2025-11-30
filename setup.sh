#!/bin/bash

# Setup script for Social Neo4j Project

echo "Setting up Social Neo4j Project..."
echo ""

# Backend setup
echo "=== Backend Setup ==="
cd backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating backend/.env file..."
    cat > .env << EOF
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
EOF
    echo "✓ Created backend/.env"
    echo "⚠️  Please edit backend/.env with your Neo4j credentials!"
else
    echo "✓ backend/.env already exists"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Created virtual environment"
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
echo "✓ Python dependencies installed"
deactivate

cd ..

# Frontend setup
echo ""
echo "=== Frontend Setup ==="
cd app

# Create .env.local file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "Creating app/.env.local file..."
    cat > .env.local << EOF
VITE_API_BASE=http://localhost:8000
EOF
    echo "✓ Created app/.env.local"
else
    echo "✓ app/.env.local already exists"
fi

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo "✓ Node.js dependencies installed"
else
    echo "✓ Node.js dependencies already installed"
fi

cd ..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Neo4j connection details"
echo "2. Make sure Neo4j Desktop is running and your database is started"
echo "3. Start the backend: cd backend && source venv/bin/activate && uvicorn app:app --reload --port 8000"
echo "4. In another terminal, start the frontend: cd app && npm run dev"
echo "5. Visit http://localhost:8000/admin/setup to initialize the database"

