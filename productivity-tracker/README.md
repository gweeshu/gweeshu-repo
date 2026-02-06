# Productivity Tracker

A minimalist daily task tracker with quantitative metrics and AI-powered productivity insights.

## Features

- **Daily task management** - Add tasks, check them off each day
- **Streak tracking** - Current and longest 100%-completion streaks
- **Completion rates** - Per-task, 7-day, 30-day, and all-time rates
- **Day-of-week analysis** - See which days you're most productive
- **30-day history chart** - Visual daily completion trend
- **AI Insights** - Claude Sonnet analyzes your data and gives specific, actionable feedback

## Quick Start

```bash
./run.sh
```

Then open http://localhost:8000

## Setup

Requires Python 3.10+.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### AI Insights (Optional)

Add your Anthropic API key to `backend/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Without it, the app still works - insights fall back to rule-based analysis.

## Architecture

```
productivity-tracker/
├── backend/
│   ├── main.py          # FastAPI app, routes, static file serving
│   ├── database.py      # SQLAlchemy models (Task, Completion)
│   ├── metrics.py       # Quantitative metrics engine
│   ├── insights.py      # Claude Sonnet AI insights
│   └── data/            # SQLite database (auto-created)
├── frontend/
│   ├── index.html       # Single-page app
│   ├── styles.css       # Dark grey minimalist UI
│   └── app.js           # Frontend logic
└── run.sh               # One-command startup
```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/tasks` | GET | List active tasks with today's status |
| `/api/tasks` | POST | Create a task |
| `/api/tasks/:id` | DELETE | Archive a task |
| `/api/tasks/:id/toggle` | POST | Toggle completion for today |
| `/api/tasks/:id/history` | GET | Get task's daily completion history |
| `/api/metrics` | GET | All quantitative metrics |
| `/api/insights` | POST | AI-generated productivity insights |

## Metrics

- **Today's rate** - % of tasks completed today
- **Current streak** - Consecutive days at 100%
- **Longest streak** - All-time best streak
- **7-day / 30-day rates** - Rolling completion rates
- **Per-task rates** - Individual task consistency (30-day window)
- **Day-of-week analysis** - Productivity patterns by weekday
- **Daily history** - 30-day completion trend with visual chart
