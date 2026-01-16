# Complete Setup Instructions - New Workflow

## What's Been Done

I've completely redesigned your medical study app with these improvements:

### Backend (✅ Complete)
- Manual course/lecture creation
- Multi-document support per lecture
- Automatic image extraction from PDFs and PowerPoints
- Better summary generation that collates multiple documents
- New API endpoints for full CRUD operations

### Frontend (⚠️ Needs Final Steps)
- HTML redesigned with modal dialogs (✅ done)
- New renderer.js created (✅ done - see NEW_RENDERER.js)
- CSS needs minor updates for new components

## Quick Start (5 Minutes)

### Step 1: Update Backend Dependencies

```bash
cd /Users/masonusher/Desktop/gweeshu-repo/medical-study-app/backend
source venv/bin/activate

# Pull latest changes
git pull origin claude/medical-study-app-7cYTn

# Install new packages
pip install -r requirements.txt

# Install poppler for PDF image extraction (macOS)
brew install poppler

# Delete old database (schema changed!)
rm -rf /Users/masonusher/Desktop/gweeshu-repo/medical-study-app/data/study_app.db
```

### Step 2: Replace Frontend Files

```bash
cd /Users/masonusher/Desktop/gweeshu-repo/medical-study-app/frontend

# Pull latest HTML
git pull origin claude/medical-study-app-7cYTn

# Replace renderer.js with new version
cp ../NEW_RENDERER.js src/renderer.js

# The CSS file needs these additions at the end:
```

Add this to the **end** of `frontend/public/styles.css`:

```css
/* New styles for redesigned workflow */
.workflow-guide { background: white; padding: 2rem; border-radius: 8px; margin-top: 2rem; }
.workflow-guide h3 { margin-bottom: 1rem; }
.workflow-guide ol { margin-left: 2rem; }
.workflow-guide li { margin-bottom: 1rem; }

.course-item { padding: 1rem; margin-bottom: 0.5rem; background: #f8f9fa; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
.course-item:hover { background: #e9ecef; border: 2px solid #3498db; }
.course-name { font-weight: 600; margin-bottom: 0.3rem; }
.course-stats { font-size: 0.85rem; opacity: 0.8; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; }
.modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 8px; min-width: 500px; z-index: 1001; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-body { padding: 1.5rem; }
.modal-body label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.modal-body input, .modal-body textarea { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem; }
.modal-footer { padding: 1.5rem; border-top: 1px solid #eee; display: flex; gap: 0.5rem; justify-content: flex-end; }
.modal-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; }

.btn-secondary-small, .btn-primary-small { padding: 0.4rem 0.8rem; font-size: 0.9rem; }
.btn-success-large { padding: 1rem 3rem; font-size: 1.1rem; }

.documents-section, .study-section { margin-top: 2rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.documents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.document-item { background: white; padding: 1rem; border-radius: 6px; border: 1px solid #eee; }
.document-icon { font-size: 2rem; margin-bottom: 0.5rem; }

.pass-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: 1rem; }
.pass-card { background: white; padding: 1.5rem; border-radius: 8px; border: 2px solid #eee; text-align: center; }
.pass-number { font-size: 1.5rem; font-weight: 600; color: #3498db; margin-bottom: 0.5rem; }
.pass-title { font-weight: 600; margin-bottom: 0.5rem; }
.pass-desc { font-size: 0.9rem; color: #666; margin-bottom: 1rem; }
.study-btn { width: 100%; padding: 0.8rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
.pass-status { margin-top: 0.5rem; font-weight: 600; }

.images-gallery { margin-top: 2rem; padding: 2rem; background: white; border-radius: 8px; }
.images-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }
.image-item { cursor: pointer; border-radius: 4px; overflow: hidden; border: 1px solid #eee; }
.image-item img { width: 100%; height: 150px; object-fit: cover; }
.image-caption { padding: 0.5rem; background: #f8f9fa; }

.spinner { border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.empty-message { text-align: center; padding: 3rem; color: #999; }
.pass-badge { background: #3498db; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.85rem; margin-right: 0.3rem; }
.lecture-subtitle { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }
```

### Step 3: Start the App

**Terminal 1 - Backend:**
```bash
cd /Users/masonusher/Desktop/gweeshu-repo/medical-study-app/backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/masonusher/Desktop/gweeshu-repo/medical-study-app/frontend
npm start
```

## Using the New App

### 1. Create a Course
- Click "+ Add Course"
- Enter name (e.g., "Anatomy", "Physiology")
- Optional: Add description
- Click "Create Course"

### 2. Add Lectures to Course
- Click on a course in the sidebar
- Click "+ Add Lecture"
- Enter lecture title (e.g., "Brainstem Anatomy")
- Optional: Add description
- Click "Create Lecture"

### 3. Upload Materials for Lecture
- Click on a lecture
- Click "+ Upload Documents"
- Select multiple PDFs, PowerPoints, Word docs
- Images will be automatically extracted
- Upload confirmation shows number of images found

### 4. Study with Multi-Pass System
- Click "Study Pass 1" to start with broad overview
- Review the summary generated from ALL your documents
- View extracted images in the gallery below
- Click "Mark Pass Complete ✓" when done
- Repeat for Pass 2 and Pass 3

## What's Different

### Before
- Upload → Auto-classify → Study
- One document per lecture
- No images
- Basic summaries

### Now
- Create course → Add lecture → Upload documents → Study
- Multiple documents per lecture
- Auto-extracted images
- Comprehensive summaries from all sources
- Better formatting with tables and structure

## Features

✅ Full control over organization
✅ Multi-document lectures
✅ Automatic image extraction (PDF & PowerPoint)
✅ Image gallery with lightbox view
✅ Better formatted summaries
✅ Collation of multiple sources
✅ Larger context window (50k chars)
✅ Progress tracking
✅ Modern, intuitive UI

## Troubleshooting

### "poppler not found"
```bash
brew install poppler  # macOS
```

### "Module not found: marked"
```bash
cd frontend
npm install marked
```

### Backend won't start
- Check venv is activated
- Check .env file exists with API key
- Delete old database: `rm -rf ../../data/study_app.db`

### Frontend shows old interface
- Make sure you copied NEW_RENDERER.js to src/renderer.js
- Make sure you added CSS to styles.css
- Hard refresh in Electron: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows)

## Next Steps

Once the app is running:
1. Create your first course
2. Add a lecture
3. Upload some PDFs or PowerPoints
4. Watch images get extracted automatically
5. Generate Pass 1 summary
6. View the comprehensive summary with images

The app is now much more powerful and gives you complete control over your study materials!

## Need Help?

Check these files:
- `MIGRATION_GUIDE.md` - Detailed migration info
- `README.md` - Full documentation
- `TROUBLESHOOTING.md` - Common issues

The backend is fully complete. The frontend just needs:
1. Copy NEW_RENDERER.js to src/renderer.js
2. Add CSS snippet to end of styles.css
3. Run `npm install marked` if needed

That's it! 🎉
