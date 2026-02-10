# IRMS Production - Intelligent Release Management Scanner

A production-ready system for analyzing codebases and managing releases with AI-enhanced insights.

## Architecture Overview

IRMS follows a clean, modular architecture:

- **Frontend**: Streamlit-based thin client (easily replaceable)
- **Backend**: FastAPI REST API with pluggable analysis modules
- **AI Engine**: Optional Gemini 2.5 Flash integration
- **Language Support**: Extensible handler system for multiple languages

## Features

✅ **Multi-Language Support**
- Python, Java, JavaScript, C, C++ (extensible)

✅ **Comprehensive Analysis**
- Code structure & complexity
- Security vulnerability scanning
- Change detection
- Risk assessment

✅ **AI Enhancement (Optional)**
- Powered by Gemini 2.5 Flash
- Enhanced insights and recommendations
- Graceful degradation when unavailable

✅ **Automated Reporting**
- Release notes generation
- Security reports
- Release checklists

## Prerequisites

- Python 3.11 or higher
- Git (optional, for change detection)
- Gemini API key (optional, for AI features)

## Quick Start

### Option 1: Automated Setup (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Gemini API key (optional)
```

#### Frontend Setup
```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Start Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Backend will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Start Frontend

In a new terminal:
```bash
cd frontend
source venv/bin/activate  # or venv\Scripts\activate on Windows
streamlit run app.py
```

Frontend will open automatically at: `http://localhost:8501`

## Configuration

### Environment Variables

Edit `backend/.env`:
```env
# AI Configuration
AI_ENABLED=false                    # Set to true to enable AI
GEMINI_API_KEY=your_api_key_here   # Your Gemini API key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Analysis Configuration
MAX_FILE_SIZE_MB=10
ANALYSIS_TIMEOUT_SECONDS=300

# Logging
LOG_LEVEL=INFO
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to `backend/.env`

## Usage

1. **Start both backend and frontend** (see above)

2. **Open the frontend** in your browser (http://localhost:8501)

3. **Enter repository path** - Full path to your git repository or project folder

4. **Enable AI (optional)** - Toggle AI analysis for enhanced insights

5. **Click Analyze** - Wait for analysis to complete

6. **Review results** across multiple tabs:
   - Overview
   - Code Analysis
   - Security
   - Changes
   - Risks
   - Reports

## API Usage

The backend provides a REST API that can be used independently:

### Analyze Repository
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "enable_ai": false
  }'
```

### Get Analysis History
```bash
curl "http://localhost:8000/api/history"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## Project Structure
```
irms-production/
├── frontend/              # Streamlit UI
│   ├── app.py            # Main frontend app
│   └── requirements.txt
│
├── backend/              # FastAPI backend
│   ├── main.py          # API server
│   ├── api/             # API routes
│   ├── models/          # Data schemas
│   ├── services/        # Business logic
│   └── core/            # Core modules
│       ├── modules/     # Analysis modules
│       │   └── languages/ # Language handlers
│       └── utils/       # Utilities
│
├── setup.sh             # Setup script
└── README.md
```

## Extending the System

### Adding a New Language

1. Create handler in `backend/core/modules/languages/`:
```python
from core.modules.languages.base import LanguageHandler

class MyLanguageHandler(LanguageHandler):
    async def analyze(self, file_info):
        # Implement analysis
        pass
```

2. Register in `language_registry.py`:
```python
self.register("MyLanguage", MyLanguageHandler())
```

### Adding New Analysis Modules

Create module in `backend/core/modules/` and integrate in `analysis_service.py`

## Performance Considerations

- **Heavy operations are isolated** - Can be replaced with faster implementations
- **AI is optional** - System works fully without AI
- **Async-safe design** - Supports concurrent analysis
- **Rate limiting** - Built-in for AI calls
- **Graceful degradation** - Failures don't block the pipeline

## Troubleshooting

### Backend won't start

- Check Python version: `python3 --version` (must be 3.11+)
- Verify virtual environment is activated
- Check port 8000 is not in use

### Frontend shows "Backend not running"

- Ensure backend is started first
- Check backend is running on port 8000
- Check firewall settings

### AI features not working

- Verify `AI_ENABLED=true` in `.env`
- Check `GEMINI_API_KEY` is set correctly
- Review backend logs for API errors
- Note: System works without AI

### Analysis fails

- Check repository path is correct
- Ensure read permissions on repository
- Check backend logs for specific errors
- Try with smaller repository first

## Security Notes

⚠️ **Important Security Considerations:**

- Never commit `.env` file with API keys
- Review detected secrets before storing results
- Use environment variables for sensitive config
- Run in isolated environment for untrusted code

## Contributing

To contribute or extend this system:

1. Follow the existing module structure
2. Add appropriate error handling
3. Update tests and documentation
4. Ensure AI features remain optional
5. Maintain backward compatibility

## License

This is a production-ready template. Adjust licensing as needed for your organization.

## Support

For issues or questions:

1. Check backend logs: `backend/` directory
2. Check frontend logs: Streamlit console
3. Review API documentation: `http://localhost:8000/docs`
4. Verify configuration in `.env`

---

**Version**: 1.0.0  
**Status**: Production Ready  
**AI Model**: Gemini 2.5 Flash (Optional)
```

---- .gitignore ----
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# Environment files
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
*.tmp

# Analysis outputs
outputs/
reports/
*.pdf

# Streamlit
.streamlit/secrets.toml