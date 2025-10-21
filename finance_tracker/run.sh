#!/bin/bash

echo "Personal Finance Tracker"
echo "======================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://www.python.org/downloads/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Please run this script from the finance_tracker directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Run the application
echo "Starting Personal Finance Tracker..."
python main.py
