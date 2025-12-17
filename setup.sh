#!/bin/bash

# SQL Agent MCP Server - Setup Script
# This script sets up the development environment for the MCP server

set -e  # Exit on error

echo "=============================================="
echo "SQL Agent MCP Server - Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

# Check if Python version is 3.10 or higher
REQUIRED_VERSION="3.10"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}Error: Python 3.10 or higher is required${NC}"
    exit 1
fi

echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated${NC}"

echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}pip upgraded${NC}"

echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed successfully${NC}"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

echo ""

# Check for .env file
echo "Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created${NC}"
        echo -e "${YELLOW}Please update .env with your actual database credentials${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        echo "Creating basic .env template..."
        cat > .env << EOF
# Database Connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=OMNI_STORE
DB_USER=postgres
DB_PASSWORD=your_password

# Server Configuration
LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}Basic .env template created${NC}"
        echo -e "${YELLOW}Please update .env with your actual database credentials${NC}"
    fi
else
    echo -e "${GREEN}.env file exists${NC}"
fi

echo ""

# Test database connection (optional)
echo "Testing database connection..."
read -p "Do you want to test the database connection? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 << EOF
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import sys

load_dotenv()

try:
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    if not all([db_host, db_name, db_user, db_password]):
        print("\033[0;31mError: Missing database credentials in .env file\033[0m")
        sys.exit(1)
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string, pool_pre_ping=True)
    
    # Test connection
    with engine.connect() as conn:
        print("\033[0;32mDatabase connection successful!\033[0m")
        
except Exception as e:
    print(f"\033[0;31mDatabase connection failed: {str(e)}\033[0m")
    print("\033[1;33mPlease check your .env file and database credentials\033[0m")
    sys.exit(1)
EOF
fi

echo ""
echo "=============================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Review and update .env with your database credentials"
echo "2. Review config.yaml for server configuration"
echo "3. Run the server with: python server.py"
echo "4. Or run: source venv/bin/activate && python server.py"
echo ""
echo "For deployment to mcp-cloud.ai, see DEPLOYMENT.md"
echo ""

