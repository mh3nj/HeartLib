#!/bin/bash

# HeartLib – Library Management System Auto-Setup
# For Linux and macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Store starting directory
STARTDIR=$(pwd)

echo "   HeartLib – Library with a Heart"
echo "        Auto-Setup & Launcher"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH!${NC}"
    echo ""
    echo "Please install Python 3.10+ from https://python.org"
    echo "Or use your system package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-virtualenv python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

# Check Python version (must be 3.10+)
PYVER=$(python3 --version 2>&1 | cut -d' ' -f2)
MAJOR=$(echo $PYVER | cut -d'.' -f1)
MINOR=$(echo $PYVER | cut -d'.' -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo -e "${RED}[ERROR] Python 3.10+ is required. Detected: $PYVER${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK] Python found: $PYVER${NC}"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}[ERROR] pip3 is not available!${NC}"
    echo "Please ensure Python is installed correctly"
    exit 1
fi
echo -e "${GREEN}[OK] pip found${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}[SETUP] Creating Python virtual environment...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment!${NC}"
        cd "$STARTDIR"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment created${NC}"
else
    echo -e "${GREEN}[OK] Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}[SETUP] Activating virtual environment...${NC}"
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to activate virtual environment!${NC}"
    cd "$STARTDIR"
    exit 1
fi
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# Check for requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[ERROR] requirements.txt not found!${NC}"
    echo "Please make sure you are in the correct HeartLib directory."
    cd "$STARTDIR"
    exit 1
fi

# Install/upgrade dependencies
echo -e "${BLUE}[INSTALL] Installing/updating dependencies...${NC}"
echo "This may take a moment..."
echo ""

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Some dependencies failed to install.${NC}"
    echo "Trying to continue anyway..."
else
    echo -e "${GREEN}[OK] All dependencies installed successfully${NC}"
fi

echo ""
echo -e "${BLUE}[SETUP] Checking database...${NC}"
if [ ! -f "heartlib.db" ]; then
    echo -e "${GREEN}[INFO] New database will be created on first run${NC}"
else
    echo -e "${GREEN}[INFO] Existing database found${NC}"
fi

echo ""
echo "   Setup Complete! Starting HeartLib..."
echo ""

# Start the application
python3 main.py

echo ""
echo -e "${GREEN}[DONE] HeartLib has been closed.${NC}"
echo "You can re-run this script anytime to update and launch."
echo ""

# Return to original directory
cd "$STARTDIR"