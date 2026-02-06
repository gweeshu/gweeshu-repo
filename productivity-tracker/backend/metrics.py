from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Completion, Task


def get_metrics(db: Session) -> dict:
    """Calculate all productivity metrics."""
    today = date.today()
    active_tasks = db.query(Task).filter(Task.is_archived == False).all()
    total_active = len(active_tasks)

    if total_active == 0:
        return _empty_metrics(today)

    task_ids = [t.id for t in active_tasks]
    all_completions = (
        db.query(Completion)
        .filter(Completion.task_id.in_(task_ids))
        .all()
    )

    # Build lookup: date -> set of completed task_ids
    date_completions = defaultdict(set)
    for c in all_completions:
        date_completions[c.date].add(c.task_id)

    # Today's stats
    today_completed = len(date_completions.get(today, set()))
    today_rate = round(today_completed / total_active * 100) if total_active else 0

    # Find the date range we care about (from earliest task creation)
    earliest = min(t.created_at.date() for t in active_tasks)
    total_days = (today - earliest).days + 1

    # Current streak: consecutive days with 100% completion, going backwards from today
    current_streak = 0
    check_date = today
    while check_date >= earliest:
        # Get tasks that existed on this date
        tasks_on_date = [t for t in active_tasks if t.created_at.date() <= check_date]
        if not tasks_on_date:
            break
        task_ids_on_date = {t.id for t in tasks_on_date}
        completed_on_date = date_completions.get(check_date, set()) & task_ids_on_date
        if len(completed_on_date) == len(task_ids_on_date):
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # Longest streak
    longest_streak = 0
    streak = 0
    check_date = earliest
    while check_date <= today:
        tasks_on_date = [t for t in active_tasks if t.created_at.date() <= check_date]
        if not tasks_on_date:
            check_date += timedelta(days=1)
            continue
        task_ids_on_date = {t.id for t in tasks_on_date}
        completed_on_date = date_completions.get(check_date, set()) & task_ids_on_date
        if len(completed_on_date) == len(task_ids_on_date):
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0
        check_date += timedelta(days=1)

    # 7-day and 30-day completion rates
    rate_7d = _period_rate(active_tasks, date_completions, today, 7)
    rate_30d = _period_rate(active_tasks, date_completions, today, 30)

    # Per-task completion rates (last 30 days)
    per_task = []
    for task in active_tasks:
        task_start = max(task.created_at.date(), today - timedelta(days=29))
        task_days = (today - task_start).days + 1
        task_completed = sum(
            1 for d in range(task_days)
            if task.id in date_completions.get(task_start + timedelta(days=d), set())
        )
        rate = round(task_completed / task_days * 100) if task_days > 0 else 0
        per_task.append({
            "id": task.id,
            "name": task.name,
            "rate": rate,
            "completed": task_completed,
            "total_days": task_days,
        })

    # Day-of-week analysis
    dow_totals = defaultdict(int)
    dow_completed = defaultdict(int)
    for d in range(min(total_days, 90)):
        check = today - timedelta(days=d)
        dow = check.strftime("%A")
        tasks_on_date = [t for t in active_tasks if t.created_at.date() <= check]
        if tasks_on_date:
            dow_totals[dow] += len(tasks_on_date)
            dow_completed[dow] += len(date_completions.get(check, set()) & {t.id for t in tasks_on_date})

    day_of_week = {}
    for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        if dow_totals[dow] > 0:
            day_of_week[dow] = round(dow_completed[dow] / dow_totals[dow] * 100)
        else:
            day_of_week[dow] = 0

    best_day = max(day_of_week, key=day_of_week.get) if day_of_week else None

    # Daily history (last 30 days)
    history = []
    for d in range(29, -1, -1):
        check = today - timedelta(days=d)
        tasks_on_date = [t for t in active_tasks if t.created_at.date() <= check]
        total_on_date = len(tasks_on_date)
        completed_count = len(date_completions.get(check, set()) & {t.id for t in tasks_on_date}) if tasks_on_date else 0
        rate = round(completed_count / total_on_date * 100) if total_on_date > 0 else 0
        history.append({
            "date": check.isoformat(),
            "completed": completed_count,
            "total": total_on_date,
            "rate": rate,
        })

    # Average daily completion rate (last 30 days, only days with active tasks)
    rates_with_tasks = [h["rate"] for h in history if h["total"] > 0]
    avg_daily_rate = round(sum(rates_with_tasks) / len(rates_with_tasks)) if rates_with_tasks else 0

    # Total completions all time
    total_completions = len(all_completions)

    return {
        "today": {
            "completed": today_completed,
            "total": total_active,
            "rate": today_rate,
        },
        "streaks": {
            "current": current_streak,
            "longest": longest_streak,
        },
        "rates": {
            "seven_day": rate_7d,
            "thirty_day": rate_30d,
            "average_daily": avg_daily_rate,
        },
        "per_task": sorted(per_task, key=lambda x: x["rate"], reverse=True),
        "day_of_week": day_of_week,
        "best_day": best_day,
        "history": history,
        "total_active_tasks": total_active,
        "total_completions_all_time": total_completions,
        "tracking_since": earliest.isoformat(),
    }


def _period_rate(active_tasks, date_completions, today, days):
    """Completion rate over the last N days."""
    total = 0
    completed = 0
    for d in range(days):
        check = today - timedelta(days=d)
        tasks_on_date = [t for t in active_tasks if t.created_at.date() <= check]
        if tasks_on_date:
            total += len(tasks_on_date)
            completed += len(date_completions.get(check, set()) & {t.id for t in tasks_on_date})
    return round(completed / total * 100) if total > 0 else 0


def _empty_metrics(today):
    return {
        "today": {"completed": 0, "total": 0, "rate": 0},
        "streaks": {"current": 0, "longest": 0},
        "rates": {"seven_day": 0, "thirty_day": 0, "average_daily": 0},
        "per_task": [],
        "day_of_week": {d: 0 for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
        "best_day": None,
        "history": [
            {"date": (today - timedelta(days=29 - i)).isoformat(), "completed": 0, "total": 0, "rate": 0}
            for i in range(30)
        ],
        "total_active_tasks": 0,
        "total_completions_all_time": 0,
        "tracking_since": today.isoformat(),
    }
