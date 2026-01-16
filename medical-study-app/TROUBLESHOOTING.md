# Troubleshooting Installation Issues

## Python 3.13 - pydantic-core Build Error

If you're getting errors about `pydantic-core` and Rust when using Python 3.13, try these solutions:

### Solution 1: Upgrade pip and setuptools (Try this first)

```bash
cd medical-study-app/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Now try installing requirements again
pip install -r requirements.txt
```

### Solution 2: Use Python 3.11 or 3.12 (Recommended)

Python 3.13 is very new and some packages don't have pre-built wheels yet. Python 3.11 or 3.12 are more stable:

```bash
# Remove the old venv
rm -rf venv  # or rmdir /s venv on Windows

# Create new venv with Python 3.11 or 3.12
python3.11 -m venv venv
# or
python3.12 -m venv venv

source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Solution 3: Install with pre-built wheels from PyPI

```bash
# If you must use Python 3.13, force pip to use binary wheels
pip install --only-binary :all: -r requirements.txt

# If some packages still fail, install them individually:
pip install --only-binary :all: fastapi uvicorn anthropic sqlalchemy python-dotenv
pip install PyPDF2 python-pptx python-docx  # These usually work fine
```

### Solution 4: Install Rust (Last resort)

If you really want to build from source:

```bash
# macOS/Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Windows - download from https://rustup.rs/

# Then try pip install again
pip install -r requirements.txt
```

## Other Common Issues

### "command not found: python3.11" or "python3.12"

Check what Python versions you have:

```bash
# macOS/Linux
which python3
python3 --version
ls /usr/local/bin/python*

# Try these commands
python3.11 --version
python3.12 --version
python --version

# Install Python 3.11/3.12
# macOS with Homebrew:
brew install python@3.11

# Ubuntu/Debian:
sudo apt-get install python3.11

# Windows:
# Download from https://www.python.org/downloads/
```

### Port 8000 already in use

```bash
# Find what's using port 8000
# macOS/Linux:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Kill the process or change the port in backend/main.py:
# Change: uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# To:     uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
```

### Module import errors after installation

```bash
# Make sure venv is activated (you should see (venv) in your prompt)
source venv/bin/activate

# Verify packages are installed
pip list

# If missing, install again
pip install -r requirements.txt
```

### Electron won't start

```bash
cd medical-study-app/frontend

# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Document parsing errors

- **PDF extraction fails**: Some PDFs are scanned images. Try OCR tools or use text-based PDFs
- **.ppt (old PowerPoint) fails**: Convert to .pptx format first
- **.doc (old Word) fails**: Convert to .docx format first

### API key issues

```bash
# Verify .env file exists and has correct format
cat backend/.env

# Should look like:
# ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
# DATABASE_PATH=../data/study_app.db

# No quotes, no spaces around the = sign
```

## Quick Environment Check

Run this to verify your setup:

```bash
# Check Python version (should be 3.8-3.13)
python3 --version

# Check Node version (should be 16+)
node --version

# Check if virtual environment is activated
which python  # Should point to venv/bin/python

# Check if backend can start
cd medical-study-app/backend
python -c "from main import app; print('Backend imports OK')"

# Check if API key is set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API key:', 'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET')"
```

## Still Having Issues?

1. **Read the error message carefully** - it usually tells you what's wrong
2. **Check the terminal output** - both backend and frontend show helpful errors
3. **Verify all prerequisites** - Python, Node.js, API key
4. **Try the recommended Solution 2** - Use Python 3.11 or 3.12 for best compatibility
5. **Check your internet connection** - needed for pip install and API calls

## Recommended Setup (Most Compatible)

For the smoothest experience:

```bash
# Use Python 3.11 (most stable)
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Use Node.js 18 LTS or higher
node --version  # Should be v18.x or higher

# Use latest Anthropic API key from console.anthropic.com
```

This configuration has been tested and works on macOS, Windows, and Linux.
