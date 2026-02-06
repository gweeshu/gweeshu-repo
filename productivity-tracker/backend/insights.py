import os
import json

from dotenv import load_dotenv

load_dotenv()


async def generate_insights(metrics: dict) -> str:
    """Generate AI-powered productivity insights using Claude Sonnet."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_insights(metrics)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are a productivity coach analyzing a user's daily task completion data.
Be concise, specific, and actionable. Use the actual numbers. No fluff.

Here is their data:

**Today**: {metrics['today']['completed']}/{metrics['today']['total']} tasks done ({metrics['today']['rate']}%)
**Current streak**: {metrics['streaks']['current']} days of 100% completion
**Longest streak**: {metrics['streaks']['longest']} days
**7-day completion rate**: {metrics['rates']['seven_day']}%
**30-day completion rate**: {metrics['rates']['thirty_day']}%
**Average daily rate**: {metrics['rates']['average_daily']}%
**Best day of week**: {metrics['best_day']}
**Total active tasks**: {metrics['total_active_tasks']}
**Tracking since**: {metrics['tracking_since']}

**Per-task rates (last 30 days)**:
{json.dumps(metrics['per_task'], indent=2)}

**Day-of-week breakdown**:
{json.dumps(metrics['day_of_week'], indent=2)}

**Last 7 days history**:
{json.dumps(metrics['history'][-7:], indent=2)}

Provide 3-5 specific, data-backed insights about their productivity. Include:
1. A pattern you notice (positive or concerning)
2. Their strongest area and what makes it work
3. A specific, actionable recommendation
4. If relevant, a trend observation (improving/declining/stable)

Keep each insight to 1-2 sentences. Be direct. Format as a simple list with bullet points."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

    except Exception as e:
        print(f"Claude API error: {e}")
        return _fallback_insights(metrics)


def _fallback_insights(metrics: dict) -> str:
    """Generate basic insights without AI when API key is unavailable."""
    insights = []

    today = metrics["today"]
    streaks = metrics["streaks"]
    rates = metrics["rates"]

    if today["total"] == 0:
        return "Add some tasks to start tracking your productivity."

    # Today's progress
    if today["rate"] == 100:
        insights.append("All tasks completed today. Solid execution.")
    elif today["rate"] >= 75:
        insights.append(f"{today['completed']}/{today['total']} done today. Close to a clean sweep.")
    elif today["rate"] > 0:
        insights.append(f"Only {today['completed']}/{today['total']} done today. Push to finish the rest.")
    else:
        insights.append("Nothing checked off yet today. Start with the easiest task to build momentum.")

    # Streak
    if streaks["current"] >= 7:
        insights.append(f"Impressive {streaks['current']}-day streak. Consistency is compounding.")
    elif streaks["current"] >= 3:
        insights.append(f"{streaks['current']}-day streak going. Keep the momentum.")
    elif streaks["longest"] > 0:
        insights.append(f"Your best streak was {streaks['longest']} days. Aim to beat it.")

    # Trend
    if rates["seven_day"] > rates["thirty_day"] + 5:
        insights.append(f"Trending up: {rates['seven_day']}% this week vs {rates['thirty_day']}% monthly average.")
    elif rates["seven_day"] < rates["thirty_day"] - 5:
        insights.append(f"Slipping: {rates['seven_day']}% this week vs {rates['thirty_day']}% monthly average.")

    # Weakest task
    per_task = metrics.get("per_task", [])
    if per_task:
        weakest = per_task[-1]
        if weakest["rate"] < 50:
            insights.append(f"'{weakest['name']}' is at {weakest['rate']}% completion. Consider if it's realistic or needs restructuring.")

    # Best day
    best_day = metrics.get("best_day")
    if best_day:
        dow = metrics["day_of_week"]
        insights.append(f"Most productive on {best_day}s ({dow[best_day]}%). Schedule demanding tasks then.")

    return "\n".join(f"- {i}" for i in insights)
