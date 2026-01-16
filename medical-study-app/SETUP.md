# Quick Setup Guide

## Step 1: Get an Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (it starts with `sk-ant-`)

## Step 2: Install Python Dependencies

```bash
cd medical-study-app/backend
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

## Step 3: Configure API Key

```bash
# Still in backend directory
cp .env.example .env

# Edit .env file and replace 'your_api_key_here' with your actual API key
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

Your .env file should look like:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
DATABASE_PATH=../data/study_app.db
```

## Step 4: Install Node.js Dependencies

```bash
cd ../frontend
npm install
```

## Step 5: Run the App

### Option A: Use the launcher script (easiest)

```bash
# From the medical-study-app directory

# On macOS/Linux:
./start.sh

# On Windows:
start.bat
```

### Option B: Manual start (two terminals)

**Terminal 1 - Backend:**
```bash
cd medical-study-app/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd medical-study-app/frontend
npm start
```

## Verification

1. Backend should show: "INFO: Uvicorn running on http://127.0.0.1:8000"
2. Electron app window should open
3. Click "Upload Documents" and select some PDFs or PowerPoint files
4. Wait for processing (Claude will analyze and categorize them)
5. Browse subjects in the sidebar
6. Click a lecture and select a pass to see AI-generated summaries

## Troubleshooting

**"ANTHROPIC_API_KEY environment variable is not set"**
- Make sure you created `.env` file in the backend directory
- Verify the API key is correct and has no extra spaces

**"Module not found" errors**
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

**"Cannot connect to backend"**
- Verify backend is running on port 8000
- Check if another app is using port 8000
- Try accessing http://127.0.0.1:8000 in your browser (should show a message)

**File parsing errors**
- Some older .ppt and .doc files may have issues
- Try converting them to .pptx and .docx
- PDF extraction works best with text-based PDFs (not scanned images)

## System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for app + space for your documents
- **OS**: Windows 10+, macOS 10.13+, or modern Linux

## Cost Information

The app uses Claude API which has these costs:
- Input tokens: ~$15 per million tokens
- Output tokens: ~$75 per million tokens

Estimated costs for typical usage:
- Processing 100 pages of text: ~$0.50-$1.00
- Generating one Pass 1 summary: ~$0.05-$0.10
- Generating one Pass 2 summary: ~$0.10-$0.20
- Generating one Pass 3 summary: ~$0.20-$0.40

Summaries are cached, so you only pay once per lecture/pass combination.

For a typical medical school block with 30 lectures:
- Initial processing: ~$5-$10
- All summaries (30 lectures × 3 passes): ~$15-$30
- **Total: ~$20-$40 per block**

Much cheaper than textbooks! 📚

## Tips

1. **Upload all lectures at once** - More efficient for processing
2. **Start with Pass 1** - Get the overview before diving deep
3. **Use descriptive filenames** - Helps Claude categorize better (e.g., "Anatomy_Brainstem.pdf")
4. **Mark passes as complete** - Stay motivated by tracking progress!
5. **Summaries are cached** - You can review them anytime without extra cost

## Next Steps

- Read the full [README.md](README.md) for more details
- Start uploading your lecture materials
- Focus on Pass 1 to get broad understanding
- Come back for Pass 2 and 3 as you study

Happy studying! 🎓
