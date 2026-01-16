# Medical Study App

A desktop application for medical students to organize lecture materials, generate AI-powered summaries at different depth levels, and track study progress through multiple passes.

## Features

- **Automatic Organization**: Upload PDFs, PowerPoint slides, and Word documents - Claude AI automatically categorizes them by subject (Anatomy, Physiology, etc.) and extracts lecture titles
- **Multi-Pass Learning**: Study material in three progressive passes:
  - **Pass 1**: Broad overview of main concepts and topics
  - **Pass 2**: Detailed understanding with mechanisms and relationships
  - **Pass 3**: Granular, exam-ready knowledge with all details
- **AI-Generated Summaries**: Claude generates custom summaries tailored to each pass level
- **Progress Tracking**: Mark passes as complete and track your progress across all subjects and lectures
- **Runs Locally**: All your data stays on your computer, only summaries are generated via Claude API

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Anthropic API key (get one at https://console.anthropic.com/)

## Installation

### 1. Set Up the Backend

```bash
cd medical-study-app/backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Set Up the Frontend

```bash
cd ../frontend

# Install Node.js dependencies
npm install
```

## Running the App

You need to run both the backend server and the Electron app.

### Terminal 1 - Start the Backend Server

```bash
cd medical-study-app/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

The API server will start on http://127.0.0.1:8000

### Terminal 2 - Start the Desktop App

```bash
cd medical-study-app/frontend
npm start
```

The Electron desktop app will launch.

## Usage

### 1. Upload Documents

- Click "Upload Documents" button
- Select one or more files (PDF, PPTX, PPT, DOCX, DOC)
- The app will:
  - Parse the documents
  - Use Claude to classify them by subject
  - Extract meaningful lecture titles
  - Create progress tracking for 3 passes

### 2. Browse by Subject

- Subjects appear in the left sidebar
- Click a subject to see its lectures
- Progress indicators show completion status for each pass

### 3. Study a Lecture

- Click on any lecture to open it
- Select a pass level (1, 2, or 3)
- Claude will generate a summary appropriate for that pass:
  - **Pass 1**: High-level overview
  - **Pass 2**: Detailed explanations
  - **Pass 3**: Comprehensive, exam-ready content
- Mark the pass as complete when done

### 4. Track Progress

- Progress badges show which passes you've completed
- Subject stats show overall completion (e.g., "12/36 passes")
- Focus on incomplete passes first

## Project Structure

```
medical-study-app/
├── backend/
│   ├── models/
│   │   └── database.py          # SQLAlchemy models
│   ├── routes/
│   │   └── api.py               # FastAPI endpoints
│   ├── services/
│   │   ├── claude_service.py    # Claude API integration
│   │   └── document_service.py  # Document processing logic
│   ├── utils/
│   │   └── document_parser.py   # PDF/PPTX/DOCX parsers
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Configuration (API keys)
├── frontend/
│   ├── public/
│   │   ├── index.html          # Main UI
│   │   └── styles.css          # Styling
│   ├── src/
│   │   └── renderer.js         # Frontend logic
│   ├── main.js                 # Electron main process
│   └── package.json            # Node.js dependencies
└── data/
    ├── uploads/                # Uploaded documents
    └── study_app.db           # SQLite database

```

## API Endpoints

The backend exposes these REST API endpoints:

- `POST /api/upload` - Upload and process documents
- `GET /api/subjects` - Get all subjects with lectures and progress
- `GET /api/summary/{lecture_id}/{pass_number}` - Get or generate summary
- `POST /api/complete` - Mark a pass as completed
- `GET /api/health` - Health check

## Database Schema

- **subjects**: Medical subject categories (Anatomy, etc.)
- **lectures**: Individual lecture documents
- **summaries**: AI-generated summaries for each pass (cached)
- **progress**: Tracks completion status for each lecture/pass combination

## Development

To run in development mode with DevTools:

```bash
cd frontend
npm run dev
```

## Troubleshooting

### Backend won't start
- Make sure you activated the virtual environment
- Check that ANTHROPIC_API_KEY is set in backend/.env
- Verify Python 3.8+ is installed: `python --version`

### Frontend won't connect
- Ensure backend is running on port 8000
- Check browser console for errors
- Try refreshing the subjects list

### Upload fails
- Verify file format is supported (PDF, PPTX, PPT, DOCX, DOC)
- Check backend logs for parsing errors
- Ensure API key is valid

### Summaries not generating
- Check your Anthropic API key is valid
- Verify you have API credits available
- Look at backend terminal for error messages

## Future Enhancements

Possible features to add:
- Search functionality across all lectures
- Export summaries to PDF
- Flashcard generation from summaries
- Spaced repetition scheduling
- Quiz generation
- Dark mode
- Multi-user support
- Cloud sync

## License

MIT License - Feel free to modify and use for your studies!

## Credits

Built with:
- FastAPI (Python web framework)
- Electron (Desktop app framework)
- Claude API (AI summaries)
- SQLite (Local database)
