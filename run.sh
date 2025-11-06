#!/bin/bash
# Run script for Ayra TRQP Profile API

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Ayra TRQP Profile API...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Run the application
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo -e "${GREEN}API will be available at: http://localhost:8000${NC}"
echo -e "${GREEN}Swagger docs at: http://localhost:8000/docs${NC}"
echo -e "${GREEN}ReDoc at: http://localhost:8000/redoc${NC}"
echo ""

python -m app.main
