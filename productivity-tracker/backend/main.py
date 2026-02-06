from datetime import date, datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Completion, Task, get_db, init_db
from metrics import get_metrics
from insights import generate_insights

app = FastAPI(title="Productivity Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic schemas ---

class TaskCreate(BaseModel):
    name: str


class TaskResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    is_archived: bool
    completed_today: bool


class ToggleComplete(BaseModel):
    date: str | None = None  # ISO date string, defaults to today


# --- Startup ---

@app.on_event("startup")
def on_startup():
    init_db()


# --- Static files ---

import os
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# --- Task endpoints ---

@app.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.is_archived == False).order_by(Task.created_at).all()
    today = date.today()
    result = []
    for t in tasks:
        completed = db.query(Completion).filter(
            Completion.task_id == t.id,
            Completion.date == today,
        ).first() is not None
        result.append({
            "id": t.id,
            "name": t.name,
            "created_at": t.created_at.isoformat(),
            "is_archived": t.is_archived,
            "completed_today": completed,
        })
    return result


@app.post("/api/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    name = task.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Task name cannot be empty")
    new_task = Task(name=name)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"id": new_task.id, "name": new_task.name, "created_at": new_task.created_at.isoformat()}


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_archived = True
    db.commit()
    return {"ok": True}


@app.post("/api/tasks/{task_id}/toggle")
def toggle_completion(task_id: int, body: ToggleComplete = None, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    target_date = date.today()
    if body and body.date:
        target_date = date.fromisoformat(body.date)

    existing = db.query(Completion).filter(
        Completion.task_id == task_id,
        Completion.date == target_date,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"completed": False, "date": target_date.isoformat()}
    else:
        completion = Completion(task_id=task_id, date=target_date)
        db.add(completion)
        db.commit()
        return {"completed": True, "date": target_date.isoformat()}


# --- Metrics ---

@app.get("/api/metrics")
def get_metrics_endpoint(db: Session = Depends(get_db)):
    return get_metrics(db)


# --- AI Insights ---

@app.post("/api/insights")
async def get_insights(db: Session = Depends(get_db)):
    metrics = get_metrics(db)
    text = await generate_insights(metrics)
    return {"insights": text}


# --- History for a specific task ---

@app.get("/api/tasks/{task_id}/history")
def task_history(task_id: int, days: int = 30, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    from datetime import timedelta
    today = date.today()
    completions = db.query(Completion).filter(
        Completion.task_id == task_id,
        Completion.date >= today - timedelta(days=days - 1),
    ).all()

    completed_dates = {c.date for c in completions}
    history = []
    for d in range(days - 1, -1, -1):
        check = today - timedelta(days=d)
        history.append({
            "date": check.isoformat(),
            "completed": check in completed_dates,
        })

    return {"task_id": task_id, "task_name": task.name, "history": history}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
