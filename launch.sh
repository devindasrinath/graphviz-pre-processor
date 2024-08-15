#!/bin/bash

# Define the virtual environment directory
VENV_DIR="venv"

# Define the requirements file
REQUIREMENTS_FILE="requirements/requirements.txt"

# Define the Python script to run
PYTHON_SCRIPT="src/main.py"

# Check if the virtual environment directory already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
    echo "Virtual environment created."
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing required libraries..."
    pip install -r $REQUIREMENTS_FILE
    echo "Required libraries installed."
else
    echo "Requirements file not found!"
    exit 1
fi

# Run the Python script
if [ -f "$PYTHON_SCRIPT" ]; then
    echo "Running the Python script..."
    python $PYTHON_SCRIPT
    echo "Python script executed."
else
    echo "Python script not found!"
    exit 1
fi

# Deactivate the virtual environment
deactivate
