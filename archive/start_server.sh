#!/bin/bash
"""
Claude Code Vector Database Startup Script
Starts the FastAPI server with proper environment activation
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Claude Code Vector Database API Server${NC}"
echo "================================================================="

# Change to the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if required packages are installed
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
python -c "import chromadb, fastapi, uvicorn; print('✅ All dependencies found')" || {
    echo -e "${RED}❌ Missing dependencies. Please install them first.${NC}"
    exit 1
}

# Check if database directory exists
if [ ! -d "chroma_db" ]; then
    echo -e "${YELLOW}📁 Creating database directory...${NC}"
    mkdir -p chroma_db
fi

echo -e "${GREEN}✅ Environment ready${NC}"
echo ""
echo -e "${BLUE}📖 API Documentation will be available at: http://localhost:8000/docs${NC}"
echo -e "${BLUE}🔍 Health Check: http://localhost:8000/health${NC}"
echo -e "${BLUE}📊 Database Stats: http://localhost:8000/stats${NC}"
echo -e "${BLUE}🔧 Rebuild Database: POST http://localhost:8000/rebuild${NC}"
echo ""
echo -e "${YELLOW}💡 To rebuild the database index from scratch:${NC}"
echo "   curl -X POST http://localhost:8000/rebuild"
echo ""
echo -e "${YELLOW}💡 Example search queries:${NC}"
echo "   http://localhost:8000/search?q=React hooks error&project=tylergohr.com"
echo "   http://localhost:8000/search?q=performance optimization&limit=10"
echo ""
echo -e "${GREEN}🎯 Starting server...${NC}"
echo "================================================================="

# Start the server
python api_server.py