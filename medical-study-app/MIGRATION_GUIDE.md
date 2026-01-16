# Migration Guide - New Workflow

## Major Changes

The app has been completely redesigned to give you full control over organization:

### Before (Old Workflow)
1. Upload documents
2. Claude automatically classifies them
3. Study the auto-organized lectures

### After (New Workflow)
1. **You create courses** (Anatomy, Physiology, etc.)
2. **You create lectures** under courses
3. **You upload multiple documents per lecture**
4. Claude collates all documents for each lecture
5. Images automatically extracted and displayed

## Breaking Changes

### Backend
- Database schema completely changed
  - `subjects` table → `courses` table
  - Added `documents` table (multiple per lecture)
  - Added `images` table
- API endpoints changed:
  - `/api/subjects` → `/api/courses`
  - New: `/api/lectures`, `/api/lectures/{id}/upload`
  - New: `/api/images/{lecture_id}/{doc_id}/{filename}`

### Frontend
- Complete redesign
- New UI with modal dialogs
- Image gallery view
- Better formatted summaries
- Pass cards instead of button selector

## Migration Steps

### 1. Update Backend

```bash
cd medical-study-app/backend
source venv/bin/activate

# Pull latest code
git pull origin claude/medical-study-app-7cYTn

# Install new dependencies
pip install -r requirements.txt

# Install poppler for PDF image extraction (macOS)
brew install poppler

# Delete old database (schema changed)
rm -rf ../../data/study_app.db

# Restart backend
python main.py
```

### 2. Update Frontend

The frontend needs complete replacement. The files that need updating:
- `frontend/public/index.html` ✓ (already updated)
- `frontend/public/styles.css` (needs update)
- `frontend/src/renderer.js` (needs complete rewrite)

### 3. Test New Workflow

1. Start backend: `python main.py`
2. Start frontend: `npm start`
3. Click "+ Add Course"
4. Create a course (e.g., "Anatomy")
5. Click "+ Add Lecture"
6. Create a lecture (e.g., "Brainstem")
7. Click "+ Upload Documents"
8. Upload multiple PDFs/PowerPoints
9. Click "Study Pass 1" to generate summary
10. View extracted images in gallery

## New Features

### Multi-Document Support
- Upload multiple files per lecture
- Claude collates them into one comprehensive summary
- Better understanding from multiple sources

### Image Extraction
- Automatically extracts images from PDFs
- Extracts images from PowerPoint slides
- Images displayed in gallery alongside summary
- Click images for full-size view

### Better Summaries
- Larger context window (50k chars vs 15k)
- Better formatting with tables
- References to images
- Integration of multiple sources

### Improved UI
- Modal dialogs for creating courses/lectures
- Card-based pass selection
- Document management view
- Image lightbox
- Better progress indicators

## Cost Changes

Slightly higher per lecture due to:
- Processing multiple documents
- Larger context window
- More comprehensive summaries

Estimated:
- Pass 1: $0.10-$0.15 (was $0.05-$0.10)
- Pass 2: $0.15-$0.25 (was $0.10-$0.20)
- Pass 3: $0.25-$0.50 (was $0.20-$0.40)

Still caches summaries, so you only pay once per lecture/pass.

## Troubleshooting

### Images not extracting from PDFs
```bash
# Install poppler
brew install poppler  # macOS
sudo apt-get install poppler-utils  # Linux
```

### Old database conflicts
```bash
# Delete and recreate
rm -rf medical-study-app/data/study_app.db
# Restart backend to recreate
```

### Frontend not working
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

## What's Next

After completing the frontend updates, you'll have:
- Full control over course organization
- Multi-document lectures
- Automatic image extraction
- Better, more comprehensive summaries
- Modern, intuitive UI

The complete frontend code (styles.css and renderer.js) is being finalized now.
