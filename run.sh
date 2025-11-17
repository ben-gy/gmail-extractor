#!/bin/bash

# Gmail Extractor - Auto venv runner
# This script automatically handles virtual environment setup

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Gmail Email Extractor${NC}"
echo "================================"

# Check if venv exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Check if dependencies are installed
if ! python -c "import google.auth" 2>/dev/null; then
    echo -e "${GREEN}Installing dependencies...${NC}"
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "✓ Dependencies installed"
fi

echo "================================"
echo ""

# Run the gmail extractor
python "$SCRIPT_DIR/gmail_extractor.py"

# Deactivate venv on exit
deactivate
