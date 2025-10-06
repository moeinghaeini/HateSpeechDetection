#!/bin/bash

# Setup script for hate speech detection environment
# This script sets up the development environment for the MSc thesis project

echo "Setting up Hate Speech Detection Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $python_version is installed, but Python $required_version or higher is required."
    exit 1
fi

echo "Python version: $python_version ✓"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "
import nltk
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'Error downloading NLTK data: {e}')
"

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/raw data/processed data/external
mkdir -p models results logs checkpoints tensorboard_logs

# Create sample data
echo "Creating sample data..."
cat > data/raw/sample_data.csv << EOF
text,label
"This is a normal comment",0
"I hate you so much",1
"Have a great day!",0
"You are stupid and worthless",1
"Thanks for the help",0
"I wish you would die",1
EOF

echo "Sample data created at data/raw/sample_data.csv"

# Run tests
echo "Running tests..."
python3 -m pytest tests/ -v

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "⚠ Some tests failed. Please check the output above."
fi

echo ""
echo "Environment setup completed!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the basic example:"
echo "  python examples/basic_usage.py"
echo ""
echo "To run the advanced example:"
echo "  python examples/advanced_usage.py"
echo ""
echo "To train a model:"
echo "  python -m src.cli.train --data data/raw/sample_data.csv --text-column text --label-column label"
echo ""
echo "Happy coding! 🚀"
