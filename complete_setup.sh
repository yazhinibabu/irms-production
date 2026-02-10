#!/bin/bash

echo "====================================="
echo "IRMS Production Setup Script"
echo "====================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.11+
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "ERROR: Python 3.11 or higher is required"
    exit 1
fi

echo ""
echo "====================================="
echo "Setting up Backend"
echo "====================================="

# Backend setup
cd backend

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit backend/.env and add your Gemini API key if you want AI features"
fi

cd ..

echo ""
echo "====================================="
echo "Setting up Frontend"
echo "====================================="

# Frontend setup
cd frontend

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Installing frontend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

cd ..

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "To run the application:"
echo ""
echo "1. Start Backend:"
echo "   cd backend"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   python main.py"
echo ""
echo "2. Start Frontend (in a new terminal):"
echo "   cd frontend"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   streamlit run app.py"
echo ""
echo "3. Open browser to http://localhost:8501"
echo ""