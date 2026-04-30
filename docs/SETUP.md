# Setup and Installation Guide

## System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk Space**: 2GB for dependencies and vector database

## Installation Steps

### Step 1: Clone/Navigate to Project

```bash
cd e:\python_projects\assignment-exl
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create `.env` file in project root:

```env
# Choose one LLM API
LLM_API=OPENAI
# LLM_API=GEMINI

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here

# Google Gemini Configuration
GOOGLE_API_KEY=AIza-your-key-here
```

### Step 5: Verify Installation

```bash
python -c "import streamlit; import langchain; import chroma; print('All dependencies installed successfully!')"
```

## Running the Application

### Start Streamlit

```bash
streamlit run app/main.py
```

The application will:
1. Initialize LLM and embeddings
2. Load or create vector database
3. Open browser to `http://localhost:8501`

### Managing Vector Database

**Reset Database**
```bash
# Delete database to start fresh
rmdir /s db\
```

## Troubleshooting Installation

### Issue: pip: command not found
- **Solution**: Ensure Python is added to PATH or use `python -m pip`

### Issue: Module not found errors
- **Solution**: Verify virtual environment is activated and dependencies are installed

### Issue: CUDA/GPU errors
- **Solution**: These are optional. CPU-only mode works fine

### Issue: API Key errors
- **Solution**: Double-check API key in `.env` file and ensure it's active

## Next Steps

1. Read [README.md](./README.md) for feature overview
2. Check [USAGE.md](./USAGE.md) for detailed usage instructions
3. Review [API.md](./API.md) for developer documentation
