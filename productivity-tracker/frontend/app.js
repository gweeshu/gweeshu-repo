// === Productivity Tracker Frontend ===

const API = "";

// --- State ---
let tasks = [];
let metrics = null;

// --- DOM refs ---
const taskInput = document.getElementById("task-input");
const btnAddTask = document.getElementById("btn-add-task");
const taskList = document.getElementById("task-list");
const taskCount = document.getElementById("task-count");
const todayDate = document.getElementById("today-date");
const btnInsights = document.getElementById("btn-insights");
const modalOverlay = document.getElementById("modal-overlay");
const modalClose = document.getElementById("modal-close");
const insightsContent = document.getElementById("insights-content");

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
    const now = new Date();
    todayDate.textContent = now.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
    });

    loadTasks();
    loadMetrics();

    // Event listeners
    btnAddTask.addEventListener("click", addTask);
    taskInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") addTask();
    });
    btnInsights.addEventListener("click", openInsights);
    modalClose.addEventListener("click", closeModal);
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) closeModal();
    });
});

// --- API calls ---

async function loadTasks() {
    try {
        const res = await fetch(`${API}/api/tasks`);
        tasks = await res.json();
        renderTasks();
    } catch (err) {
        console.error("Failed to load tasks:", err);
    }
}

async function loadMetrics() {
    try {
        const res = await fetch(`${API}/api/metrics`);
        metrics = await res.json();
        renderMetrics();
    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}

async function addTask() {
    const name = taskInput.value.trim();
    if (!name) return;

    try {
        const res = await fetch(`${API}/api/tasks`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        });
        if (res.ok) {
            taskInput.value = "";
            await loadTasks();
            await loadMetrics();
        }
    } catch (err) {
        console.error("Failed to add task:", err);
    }
}

async function toggleTask(taskId) {
    try {
        await fetch(`${API}/api/tasks/${taskId}/toggle`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
        });
        await loadTasks();
        await loadMetrics();
    } catch (err) {
        console.error("Failed to toggle task:", err);
    }
}

async function deleteTask(taskId) {
    try {
        await fetch(`${API}/api/tasks/${taskId}`, { method: "DELETE" });
        await loadTasks();
        await loadMetrics();
    } catch (err) {
        console.error("Failed to delete task:", err);
    }
}

async function openInsights() {
    modalOverlay.classList.add("active");
    insightsContent.innerHTML = '<div class="loading">Analyzing your data...</div>';

    try {
        const res = await fetch(`${API}/api/insights`, { method: "POST" });
        const data = await res.json();
        insightsContent.textContent = data.insights;
    } catch (err) {
        insightsContent.textContent = "Failed to generate insights. Check your API key configuration.";
    }
}

function closeModal() {
    modalOverlay.classList.remove("active");
}

// --- Rendering ---

function renderTasks() {
    taskCount.textContent = tasks.length;

    if (tasks.length === 0) {
        taskList.innerHTML = '<div class="empty-state">No tasks yet. Add one above.</div>';
        return;
    }

    taskList.innerHTML = tasks
        .map(
            (t) => `
        <div class="task-item ${t.completed_today ? "completed" : ""}" data-id="${t.id}">
            <div class="task-checkbox" onclick="toggleTask(${t.id})"></div>
            <span class="task-name" onclick="toggleTask(${t.id})">${escapeHtml(t.name)}</span>
            <button class="task-delete" onclick="event.stopPropagation(); deleteTask(${t.id})" title="Remove task">&times;</button>
        </div>
    `
        )
        .join("");
}

function renderMetrics() {
    if (!metrics) return;

    // Today card
    document.getElementById("metric-today-rate").textContent = `${metrics.today.rate}%`;
    document.getElementById("metric-today-detail").textContent = `${metrics.today.completed}/${metrics.today.total} tasks`;

    // Streak card
    document.getElementById("metric-streak").textContent = metrics.streaks.current;
    document.getElementById("metric-streak-best").textContent = `Best: ${metrics.streaks.longest}`;

    // 7-day rate
    document.getElementById("metric-7d").textContent = `${metrics.rates.seven_day}%`;
    document.getElementById("metric-30d").textContent = `30d: ${metrics.rates.thirty_day}%`;

    // Best day
    const bestDay = metrics.best_day || "--";
    document.getElementById("metric-best-day").textContent = bestDay === "--" ? "--" : bestDay.slice(0, 3);
    const bestDayRate = metrics.best_day ? metrics.day_of_week[metrics.best_day] : 0;
    document.getElementById("metric-best-day-rate").textContent = `${bestDayRate}%`;

    // Avg rate
    document.getElementById("avg-rate").textContent = `Avg: ${metrics.rates.average_daily}%`;

    // 30-day chart
    renderChart(metrics.history);

    // Per-task rates
    renderTaskRates(metrics.per_task);

    // Day of week
    renderDOW(metrics.day_of_week);
}

function renderChart(history) {
    const container = document.getElementById("chart-container");

    container.innerHTML = history
        .map((day) => {
            const height = Math.max(day.rate > 0 ? 4 : 1, (day.rate / 100) * 130);
            const color = barColor(day.rate);
            const dateStr = formatDate(day.date);
            return `
            <div class="chart-bar ${color}" style="height: ${height}px">
                <div class="tooltip">${dateStr}: ${day.completed}/${day.total} (${day.rate}%)</div>
            </div>
        `;
        })
        .join("");
}

function renderTaskRates(perTask) {
    const container = document.getElementById("task-rates");

    if (perTask.length === 0) {
        container.innerHTML = '<div class="empty-state">No task data yet.</div>';
        return;
    }

    container.innerHTML = perTask
        .map((t) => {
            const color = barColor(t.rate);
            return `
            <div class="rate-row">
                <span class="rate-name" title="${escapeHtml(t.name)}">${escapeHtml(t.name)}</span>
                <div class="rate-bar-bg">
                    <div class="rate-bar-fill ${color}" style="width: ${t.rate}%"></div>
                </div>
                <span class="rate-value">${t.rate}%</span>
            </div>
        `;
        })
        .join("");
}

function renderDOW(dayOfWeek) {
    const container = document.getElementById("dow-chart");
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const shortDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    container.innerHTML = days
        .map((day, i) => {
            const rate = dayOfWeek[day] || 0;
            const height = Math.max(rate > 0 ? 4 : 1, (rate / 100) * 72);
            const color = barColor(rate);
            return `
            <div class="dow-bar-wrapper">
                <div class="dow-value">${rate}%</div>
                <div class="dow-bar-container">
                    <div class="dow-bar-fill ${color}" style="height: ${height}px"></div>
                </div>
                <div class="dow-label">${shortDays[i]}</div>
            </div>
        `;
        })
        .join("");
}

// --- Helpers ---

function barColor(rate) {
    if (rate >= 80) return "bar-green";
    if (rate >= 50) return "bar-yellow";
    if (rate > 0) return "bar-red";
    return "bar-muted";
}

function formatDate(isoDate) {
    const d = new Date(isoDate + "T00:00:00");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
