import { Api, Storage } from "./api.js";
import { Auth } from "./auth.js";

// Global Application State
const State = {
    currentDate: new Date().toISOString().split("T")[0],
    activeView: "dashboard",
    charts: {},
    workoutFilter: "",
};

// ==========================================================================
// Toast Notification Utility
// ==========================================================================
export function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${type === "success" 
                ? '<polyline points="20 6 9 17 4 12"/>' 
                : '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'}
        </svg>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 250);
    }, 3500);
}

// ==========================================================================
// Modal Helpers
// ==========================================================================
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("active");
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("active");
}

// ==========================================================================
// View Router & Navigation
// ==========================================================================
function openMobileMoreSheet() {
    const sheet = document.getElementById("mobile-more-sheet");
    const backdrop = document.getElementById("mobile-more-backdrop");
    if (sheet) sheet.classList.add("active");
    if (backdrop) backdrop.classList.add("active");
}

function closeMobileMoreSheet() {
    const sheet = document.getElementById("mobile-more-sheet");
    const backdrop = document.getElementById("mobile-more-backdrop");
    if (sheet) sheet.classList.remove("active");
    if (backdrop) backdrop.classList.remove("active");
}

function toggleMobileMoreSheet() {
    const sheet = document.getElementById("mobile-more-sheet");
    if (sheet && sheet.classList.contains("active")) {
        closeMobileMoreSheet();
    } else {
        openMobileMoreSheet();
    }
}

function switchView(viewName) {
    State.activeView = viewName;

    // Update Nav item states in desktop sidebar, mobile bar, and mobile sheet
    document.querySelectorAll(".nav-item, .mobile-nav-item, .mobile-more-item").forEach(item => {
        if (item.dataset.view === viewName) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    // Check if current view is in the More menu to highlight the "More" button
    const moreViews = ["nutrition", "hydration", "sleep", "analytics", "profile"];
    const mobileMoreBtn = document.getElementById("btn-mobile-more");
    if (mobileMoreBtn) {
        if (moreViews.includes(viewName)) {
            mobileMoreBtn.classList.add("active");
        } else {
            mobileMoreBtn.classList.remove("active");
        }
    }

    // Always close sheet on view switch
    closeMobileMoreSheet();

    // Update section visibility
    document.querySelectorAll(".view-section").forEach(sec => {
        sec.classList.remove("active");
    });
    const targetSection = document.getElementById(`view-${viewName}`);
    if (targetSection) {
        targetSection.classList.add("active");
    }

    // Refresh data for active view
    refreshActiveView();
}

async function refreshActiveView() {
    if (!Auth.currentUser) return;

    switch (State.activeView) {
        case "dashboard":
            await loadDashboard();
            break;
        case "weight":
            await loadWeightView();
            break;
        case "workouts":
            await loadWorkouts();
            await loadExerciseCatalog();
            break;
        case "activity":
            await loadActivityView();
            break;
        case "nutrition":
            await loadNutrition();
            break;
        case "hydration":
            await loadHydrationView();
            break;
        case "sleep":
            await loadSleepView();
            break;
        case "analytics":
            await loadAnalyticsView();
            break;
        case "profile":
            await loadProfileView();
            break;
    }
}

// ==========================================================================
// 1. DASHBOARD CONTROLLER
// ==========================================================================
async function loadDashboard() {
    try {
        const data = await Api.getDashboard(State.currentDate);

        // Header greeting
        document.getElementById("dashboard-greeting").textContent = data.greeting.toUpperCase();
        document.getElementById("dashboard-user-greeting").textContent = `Welcome back, ${data.user_name}!`;
        document.getElementById("dashboard-date-display").textContent = `Fitness summary for ${State.currentDate}`;

        // Weight KPI
        const weightVal = document.getElementById("kpi-weight-val");
        const weightSub = document.getElementById("kpi-weight-subtext");
        if (data.current_weight) {
            weightVal.textContent = data.current_weight.toFixed(1);
            let changeText = "";
            if (data.weight_change !== null && data.weight_change !== undefined) {
                const sign = data.weight_change > 0 ? "+" : "";
                changeText = `(${sign}${data.weight_change.toFixed(1)} kg from start)`;
            }
            weightSub.textContent = changeText || "Latest weigh-in";
        } else {
            weightVal.textContent = "--";
            weightSub.textContent = "No weigh-ins logged";
        }

        // Steps KPI
        document.getElementById("kpi-steps-val").textContent = data.steps.current.toLocaleString();
        document.getElementById("kpi-steps-target").textContent = `/ ${data.steps.target.toLocaleString()}`;
        document.getElementById("kpi-steps-bar").style.width = `${data.steps.percentage}%`;
        document.getElementById("kpi-steps-subtext").textContent = `${data.steps.actual_percentage.toFixed(0)}% of daily target`;

        // Water KPI
        document.getElementById("kpi-water-val").textContent = data.water.current.toLocaleString();
        document.getElementById("kpi-water-target").textContent = `/ ${data.water.target.toLocaleString()} ml`;
        document.getElementById("kpi-water-bar").style.width = `${data.water.percentage}%`;
        document.getElementById("kpi-water-subtext").textContent = `${data.water.actual_percentage.toFixed(0)}% completed`;

        // Sleep KPI
        document.getElementById("kpi-sleep-val").textContent = data.sleep.current.toFixed(1);
        document.getElementById("kpi-sleep-target").textContent = `/ ${data.sleep.target.toFixed(1)} hrs`;
        document.getElementById("kpi-sleep-bar").style.width = `${data.sleep.percentage}%`;
        document.getElementById("kpi-sleep-subtext").textContent = `${data.sleep.actual_percentage.toFixed(0)}% of recovery goal`;

        // Calories KPI
        document.getElementById("kpi-calories-in").textContent = Math.round(data.calories_consumed);
        document.getElementById("kpi-calories-burned").textContent = `Burned: ${Math.round(data.calories_burned)} kcal (${data.workouts_count} workouts, ${data.workouts_duration_minutes}m)`;

        // Workouts KPI
        const workoutDurEl = document.getElementById("kpi-workout-duration-val");
        const workoutSubEl = document.getElementById("kpi-workout-sessions-subtext");
        if (workoutDurEl) workoutDurEl.textContent = data.workouts_duration_minutes || 0;
        if (workoutSubEl) workoutSubEl.textContent = `${data.workouts_count || 0} session(s) completed today`;

        // Render Charts
        renderWeeklyActivityChart(data.weekly_activity_trend);
        renderWeightTrendChart(data.weight_trend);

        // Render Recent Workouts
        renderRecentWorkoutsList(data.recent_workouts);
    } catch (err) {
        showToast(err.message || "Failed to load dashboard data", "error");
    }
}

function renderWeeklyActivityChart(trends) {
    const ctx = document.getElementById("chart-weekly-activity");
    if (!ctx) return;

    if (State.charts.weeklyActivity) {
        State.charts.weeklyActivity.destroy();
    }

    const labels = trends.map(t => t.day_name);
    const stepsData = trends.map(t => t.steps);
    const workoutMins = trends.map(t => t.workout_minutes);

    State.charts.weeklyActivity = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Steps",
                    data: stepsData,
                    backgroundColor: "rgba(198, 255, 77, 0.22)",
                    borderColor: "#C6FF4D",
                    borderWidth: 1.5,
                    borderRadius: 6,
                    yAxisID: "ySteps",
                },
                {
                    label: "Workout Mins",
                    data: workoutMins,
                    type: "line",
                    borderColor: "#38bdf8",
                    backgroundColor: "rgba(56, 189, 248, 0.12)",
                    borderWidth: 2.5,
                    pointBackgroundColor: "#38bdf8",
                    pointRadius: 4,
                    tension: 0.35,
                    yAxisID: "yMins",
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "#A0A79B", font: { family: "Plus Jakarta Sans", size: 12 } }
                }
            },
            scales: {
                x: {
                    grid: { color: "#292F27" },
                    ticks: { color: "#737B70" }
                },
                ySteps: {
                    type: "linear",
                    position: "left",
                    grid: { color: "#292F27" },
                    ticks: { color: "#737B70" }
                },
                yMins: {
                    type: "linear",
                    position: "right",
                    grid: { drawOnChartArea: false },
                    ticks: { color: "#38bdf8" }
                }
            }
        }
    });
}

function renderWeightTrendChart(trendData) {
    const ctx = document.getElementById("chart-weight-trend");
    if (!ctx) return;

    if (State.charts.weightTrend) {
        State.charts.weightTrend.destroy();
    }

    const labels = trendData.map(t => t.date.slice(5)); // MM-DD
    const weights = trendData.map(t => t.weight);

    State.charts.weightTrend = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Weight (kg)",
                data: weights,
                borderColor: "#C6FF4D",
                backgroundColor: "rgba(198, 255, 77, 0.08)",
                borderWidth: 2.5,
                pointBackgroundColor: "#C6FF4D",
                pointRadius: 4,
                fill: true,
                tension: 0.3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: "#292F27" },
                    ticks: { color: "#737B70" }
                },
                y: {
                    grid: { color: "#292F27" },
                    ticks: { color: "#737B70" }
                }
            }
        }
    });
}

function renderRecentWorkoutsList(workouts) {
    const container = document.getElementById("dashboard-recent-workouts-list");
    if (!container) return;

    if (!workouts || workouts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No workouts logged yet. Click "Log Workout" above to start tracking!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = workouts.map(w => `
        <div class="workout-card">
            <div class="workout-header">
                <div>
                    <strong style="color:var(--text-primary); font-size:1.05rem;">${escapeHtml(w.workout_name)}</strong>
                    <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">
                        ${new Date(w.start_time).toLocaleDateString()} • ${w.duration_minutes} mins • ${w.estimated_calories ? `${Math.round(w.estimated_calories)} kcal` : "Custom"}
                    </div>
                </div>
                <span class="badge ${getBadgeColor(w.workout_type)}">${escapeHtml(w.workout_type)}</span>
            </div>
            ${w.exercises && w.exercises.length > 0 ? `
                <div style="margin-top:10px;">
                    ${w.exercises.map(ex => `
                        <div class="exercise-row">
                            <span style="font-weight:600;">${escapeHtml(ex.exercise_name)}</span>
                            <span style="color:var(--text-secondary);">${ex.sets} sets × ${ex.repetitions} reps @ ${ex.weight_used} kg</span>
                        </div>
                    `).join("")}
                </div>
            ` : ""}
        </div>
    `).join("");
}

// ==========================================================================
// 2. WORKOUTS CONTROLLER
// ==========================================================================
async function loadWorkouts() {
    try {
        const params = State.workoutFilter ? `workout_type=${encodeURIComponent(State.workoutFilter)}` : "";
        const workouts = await Api.getWorkouts(params);
        const container = document.getElementById("workouts-list-container");
        document.getElementById("workout-count-label").textContent = `${workouts.length} workouts found`;

        if (!workouts || workouts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No Workouts Logged</h3>
                    <p>Start recording your strength, cardio, and endurance sessions.</p>
                    <button class="btn btn-primary" id="btn-empty-add-workout">Log First Workout</button>
                </div>
            `;
            document.getElementById("btn-empty-add-workout")?.addEventListener("click", () => openModal("modal-workout"));
            return;
        }

        container.innerHTML = workouts.map(w => `
            <div class="workout-card">
                <div class="workout-header">
                    <div>
                        <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">${escapeHtml(w.workout_name)}</h3>
                        <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:4px;">
                            ${new Date(w.start_time).toLocaleString()} • ${w.duration_minutes} min duration • ${w.estimated_calories ? `${Math.round(w.estimated_calories)} kcal` : "Unspecified cals"}
                        </div>
                        ${w.notes ? `<div style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;">Notes: ${escapeHtml(w.notes)}</div>` : ""}
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="badge ${getBadgeColor(w.workout_type)}">${escapeHtml(w.workout_type)}</span>
                        <button class="btn btn-danger btn-sm btn-delete-workout" data-id="${w.id}" title="Delete Workout">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                        </button>
                    </div>
                </div>

                ${w.exercises && w.exercises.length > 0 ? `
                    <div style="margin-top:14px; border-top:1px solid rgba(255,255,255,0.06); padding-top:12px;">
                        <div style="font-size:0.8rem; font-weight:600; color:var(--text-muted); text-transform:uppercase; margin-bottom:8px;">Exercises:</div>
                        <div style="display:flex; flex-direction:column; gap:6px;">
                            ${w.exercises.map(ex => `
                                <div class="exercise-row">
                                    <span style="font-weight:600; color:var(--text-primary);">${escapeHtml(ex.exercise_name)}</span>
                                    <span style="color:var(--text-secondary);">${ex.sets} sets × ${ex.repetitions} reps • ${ex.weight_used} kg ${ex.duration_minutes ? `• ${ex.duration_minutes} min` : ""}</span>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                ` : ""}
            </div>
        `).join("");

        // Attach delete events
        container.querySelectorAll(".btn-delete-workout").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = e.currentTarget.dataset.id;
                if (confirm("Are you sure you want to delete this workout?")) {
                    await Api.deleteWorkout(id);
                    showToast("Workout deleted successfully");
                    loadWorkouts();
                }
            });
        });
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function loadExerciseCatalog(query = "", muscle = "") {
    try {
        const list = await Api.getExerciseCatalog(query, muscle);
        const container = document.getElementById("exercise-catalog-results");
        if (!container) return;

        container.innerHTML = list.slice(0, 12).map(ex => `
            <div style="background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:12px; padding:14px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                    <strong style="color:var(--text-primary); font-size:0.95rem;">${escapeHtml(ex.name)}</strong>
                    <span class="badge blue">${escapeHtml(ex.muscle_group)}</span>
                </div>
                <div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:10px;">${escapeHtml(ex.instructions)}</div>
                <button class="btn btn-secondary btn-sm btn-quick-add-exercise" data-name="${escapeHtml(ex.name)}" style="width:100%;">
                    + Add to Workout
                </button>
            </div>
        `).join("");

        container.querySelectorAll(".btn-quick-add-exercise").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const name = e.currentTarget.dataset.name;
                openModal("modal-workout");
                addExerciseRow(name);
            });
        });
    } catch {
        // Silently tolerate catalog loading glitches
    }
}

function addExerciseRow(prefillName = "") {
    const container = document.getElementById("workout-exercises-rows-container");
    if (!container) return;

    const row = document.createElement("div");
    row.className = "exercise-form-row";
    row.style = "display:grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap:8px; align-items:center; margin-bottom:8px;";
    row.innerHTML = `
        <input type="text" class="form-input ex-name" placeholder="Exercise name" value="${escapeHtml(prefillName)}" required>
        <input type="number" class="form-input ex-sets" placeholder="Sets" value="3" min="1" max="50" required>
        <input type="number" class="form-input ex-reps" placeholder="Reps" value="10" min="0" max="500">
        <input type="number" class="form-input ex-weight" placeholder="kg" value="20" step="0.5" min="0">
        <button type="button" class="btn btn-danger btn-sm btn-remove-ex-row" style="padding:8px;">&times;</button>
    `;
    row.querySelector(".btn-remove-ex-row").addEventListener("click", () => row.remove());
    container.appendChild(row);
}

// ==========================================================================
// 3. NUTRITION CONTROLLER
// ==========================================================================
async function loadNutrition() {
    try {
        const summary = await Api.getFood(State.currentDate);

        document.getElementById("nutrition-total-cals").textContent = `${Math.round(summary.total_calories)} kcal`;
        document.getElementById("macro-protein-val").textContent = `${Math.round(summary.total_protein_g)}g`;
        document.getElementById("macro-carbs-val").textContent = `${Math.round(summary.total_carbs_g)}g`;
        document.getElementById("macro-fat-val").textContent = `${Math.round(summary.total_fat_g)}g`;

        renderMacroDoughnut(summary.total_protein_g, summary.total_carbs_g, summary.total_fat_g);

        const tbody = document.getElementById("food-table-body");
        if (!summary.entries || summary.entries.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:24px; color:var(--text-muted);">No food logged for this date. Use the search or form above to log meals.</td></tr>`;
            return;
        }

        tbody.innerHTML = summary.entries.map(e => `
            <tr>
                <td><span class="badge ${getMealBadgeColor(e.meal_category)}">${escapeHtml(e.meal_category)}</span></td>
                <td><strong>${escapeHtml(e.food_name)}</strong></td>
                <td>${e.serving_quantity}</td>
                <td>${Math.round(e.calories)} kcal</td>
                <td>${e.protein_g.toFixed(1)}g</td>
                <td>${e.carbs_g.toFixed(1)}g</td>
                <td>${e.fat_g.toFixed(1)}g</td>
                <td>
                    <button class="btn btn-danger btn-sm btn-delete-food" data-id="${e.id}">&times;</button>
                </td>
            </tr>
        `).join("");

        tbody.querySelectorAll(".btn-delete-food").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = e.currentTarget.dataset.id;
                if (confirm("Delete this food entry?")) {
                    await Api.deleteFood(id);
                    showToast("Food entry deleted");
                    loadNutrition();
                }
            });
        });
    } catch (err) {
        showToast(err.message, "error");
    }
}

function renderMacroDoughnut(protein, carbs, fat) {
    const ctx = document.getElementById("chart-macro-doughnut");
    if (!ctx) return;

    if (State.charts.macroDoughnut) {
        State.charts.macroDoughnut.destroy();
    }

    const hasData = protein > 0 || carbs > 0 || fat > 0;
    const dataValues = hasData ? [protein * 4, carbs * 4, fat * 9] : [1, 1, 1];
    const bgColors = hasData ? ["#C6FF4D", "#38bdf8", "#fb923c"] : ["#151915", "#151915", "#151915"];

    State.charts.macroDoughnut = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Protein (kcal)", "Carbs (kcal)", "Fat (kcal)"],
            datasets: [{
                data: dataValues,
                backgroundColor: bgColors,
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#A0A79B", font: { family: "Plus Jakarta Sans", size: 11 } }
                }
            },
            cutout: "70%"
        }
    });
}

// ==========================================================================
// 4. ACTIVITY CONTROLLER
// ==========================================================================
async function loadActivityView() {
    try {
        const activities = await Api.getActivities();
        const tbody = document.getElementById("activity-history-table-body");
        
        // Find today's activity or default
        const todayAct = activities.find(a => a.activity_date === State.currentDate);
        const steps = todayAct ? todayAct.steps : 0;
        const activeMins = todayAct ? todayAct.active_minutes : 0;
        const cardioMins = todayAct ? todayAct.cardio_minutes : 0;
        const burnedCals = todayAct && todayAct.calories_burned ? Math.round(todayAct.calories_burned) : 0;
        
        const profile = Auth.currentUser?.profile;
        const targetSteps = profile?.daily_step_target || 10000;
        const pct = Math.min(100, Math.round((steps / targetSteps) * 100));

        document.getElementById("activity-steps-val").textContent = steps.toLocaleString();
        document.getElementById("activity-steps-target").textContent = `/ ${targetSteps.toLocaleString()}`;
        document.getElementById("activity-steps-bar").style.width = `${pct}%`;
        document.getElementById("activity-steps-subtext").textContent = `${((steps / targetSteps) * 100).toFixed(0)}% achieved`;

        document.getElementById("activity-active-mins").textContent = activeMins;
        document.getElementById("activity-cardio-mins").textContent = cardioMins;
        document.getElementById("activity-calories-burned").textContent = burnedCals;

        if (!activities || activities.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-muted);">No activity records found. Use "Log Activity" to record steps and movement!</td></tr>`;
            return;
        }

        tbody.innerHTML = activities.map(a => `
            <tr>
                <td><strong>${a.activity_date}</strong></td>
                <td><span style="font-weight:700; color:var(--cyan);">${a.steps.toLocaleString()}</span></td>
                <td>${a.active_minutes} mins</td>
                <td>${a.cardio_minutes} mins</td>
                <td>${a.calories_burned ? `${Math.round(a.calories_burned)} kcal` : "—"}</td>
                <td><span class="badge ${a.data_source === 'manual' ? 'purple' : 'green'}">${escapeHtml(a.data_source || 'manual')}</span></td>
            </tr>
        `).join("");
    } catch (err) {
        showToast(err.message, "error");
    }
}

// ==========================================================================
// 5. HYDRATION CONTROLLER
// ==========================================================================
async function loadHydrationView() {
    try {
        const waterData = await Api.getWater(State.currentDate);
        const badge = document.getElementById("hydration-page-total-badge");
        if (badge) badge.textContent = `${waterData.total_ml.toLocaleString()} / ${waterData.target_ml.toLocaleString()} ml`;

        const percentage = Math.min(100, Math.round(waterData.percentage));
        const fillEl = document.getElementById("visual-water-fill-hydration");
        if (fillEl) fillEl.style.height = `${percentage}%`;

        const listEl = document.getElementById("hydration-entries-list");
        if (!listEl) return;

        if (!waterData.entries || waterData.entries.length === 0) {
            listEl.innerHTML = `<div style="color:var(--text-muted); font-size:0.88rem; padding:12px 0;">No water entries logged for this date. Use the quick-add buttons above!</div>`;
            return;
        }

        listEl.innerHTML = waterData.entries.map(w => `
            <div style="display:flex; justify-content:space-between; align-items:center; background:var(--bg-input); border:1px solid var(--border-subtle); padding:10px 14px; border-radius:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="color:var(--accent-primary); font-weight:700; font-size:1.05rem;">+${w.quantity_ml} ml</span>
                    <span style="font-size:0.82rem; color:var(--text-secondary);">${new Date(w.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <button class="btn btn-danger btn-sm btn-delete-water" data-id="${w.id}" title="Remove entry" style="padding:4px 10px;">&times;</button>
            </div>
        `).join("");

        listEl.querySelectorAll(".btn-delete-water").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = e.currentTarget.dataset.id;
                await Api.deleteWater(id);
                showToast("Water entry removed");
                loadHydrationView();
            });
        });
    } catch (err) {
        showToast(err.message, "error");
    }
}

// ==========================================================================
// 6. SLEEP CONTROLLER
// ==========================================================================
async function loadSleepView() {
    try {
        const sleeps = await Api.getSleep(30);
        const listEl = document.getElementById("sleep-history-list-page");
        if (!listEl) return;

        if (!sleeps || sleeps.length === 0) {
            listEl.innerHTML = `<div style="color:var(--text-muted); font-size:0.88rem; padding:12px 0;">No sleep sessions recorded yet. Record your last night's sleep to calculate recovery scores.</div>`;
            return;
        }

        listEl.innerHTML = sleeps.map(s => {
            const hrs = (s.duration_minutes / 60).toFixed(1);
            const startDate = new Date(s.sleep_start).toLocaleDateString([], { month: 'short', day: 'numeric' });
            const startTime = new Date(s.sleep_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const endTime = new Date(s.sleep_end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            return `
                <div style="display:flex; justify-content:space-between; align-items:center; background:var(--bg-card); border:1px solid var(--border-subtle); padding:12px 16px; border-radius:12px;">
                    <div>
                        <div style="font-weight:700; font-size:1.05rem; color:var(--text-primary);">${hrs} hrs <span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">(${Math.floor(s.duration_minutes / 60)}h ${s.duration_minutes % 60}m)</span></div>
                        <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:2px;">
                            ${startDate} • ${startTime} → ${endTime}
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span>${s.quality_rating ? "⭐".repeat(s.quality_rating) : ""}</span>
                        <button class="btn btn-danger btn-sm btn-delete-sleep" data-id="${s.id}" title="Remove entry" style="padding:4px 10px;">&times;</button>
                    </div>
                </div>
            `;
        }).join("");

        listEl.querySelectorAll(".btn-delete-sleep").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = e.currentTarget.dataset.id;
                await Api.deleteSleep(id);
                showToast("Sleep session removed");
                loadSleepView();
            });
        });
    } catch (err) {
        showToast(err.message, "error");
    }
}

// ==========================================================================
// 5. WEIGHT & BODY CONTROLLER
// ==========================================================================
async function loadWeightView() {
    try {
        const data = await Api.getWeightAnalytics();

        document.getElementById("weight-view-latest").textContent = data.latest_weight ? data.latest_weight.toFixed(1) : "--";
        document.getElementById("weight-view-first").textContent = data.earliest_weight ? `Starting: ${data.earliest_weight.toFixed(1)} kg` : "Starting: -- kg";

        const changeVal = document.getElementById("weight-view-change");
        if (data.weight_change !== null && data.weight_change !== undefined) {
            const sign = data.weight_change > 0 ? "+" : "";
            changeVal.textContent = `${sign}${data.weight_change.toFixed(1)}`;
        } else {
            changeVal.textContent = "--";
        }

        document.getElementById("weight-view-target").textContent = data.target_weight ? `${data.target_weight.toFixed(1)}` : "None";
        if (data.progress_percentage !== null && data.progress_percentage !== undefined) {
            document.getElementById("weight-view-progress-bar").style.width = `${data.progress_percentage}%`;
            document.getElementById("weight-view-progress-text").textContent = `${data.progress_percentage.toFixed(0)}% towards target weight`;
        } else {
            document.getElementById("weight-view-progress-bar").style.width = "0%";
            document.getElementById("weight-view-progress-text").textContent = "Set target weight in profile";
        }

        // BMI Screening
        const profile = Auth.currentUser?.profile;
        if (data.latest_weight && profile && profile.height_cm) {
            const hm = profile.height_cm / 100.0;
            const bmi = (data.latest_weight / (hm * hm)).toFixed(1);
            document.getElementById("weight-view-bmi").textContent = `${bmi} BMI`;
        } else {
            document.getElementById("weight-view-bmi").textContent = "--";
        }

        // Full Historical Chart
        renderFullWeightHistoryChart(data.history);

        // Table
        const tbody = document.getElementById("weight-history-table-body");
        if (!data.history || data.history.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px; color:var(--text-muted);">No weight entries recorded yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = [...data.history].reverse().map(w => `
            <tr>
                <td><strong>${w.measurement_date}</strong></td>
                <td>${w.weight_kg.toFixed(1)} kg</td>
                <td style="color:var(--text-secondary);">${escapeHtml(w.note || "—")}</td>
                <td>
                    <button class="btn btn-danger btn-sm btn-delete-weight" data-id="${w.id}">&times;</button>
                </td>
            </tr>
        `).join("");

        tbody.querySelectorAll(".btn-delete-weight").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = e.currentTarget.dataset.id;
                if (confirm("Delete this weight record?")) {
                    await Api.deleteWeight(id);
                    showToast("Weight record deleted");
                    loadWeightView();
                }
            });
        });
    } catch (err) {
        showToast(err.message, "error");
    }
}

function renderFullWeightHistoryChart(history) {
    const ctx = document.getElementById("chart-weight-full-history");
    if (!ctx) return;

    if (State.charts.fullWeightHistory) {
        State.charts.fullWeightHistory.destroy();
    }

    const labels = history.map(w => w.measurement_date);
    const weights = history.map(w => w.weight_kg);

    State.charts.fullWeightHistory = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Recorded Weight (kg)",
                data: weights,
                borderColor: "#C6FF4D",
                backgroundColor: "rgba(198, 255, 77, 0.12)",
                borderWidth: 2.5,
                pointBackgroundColor: "#C6FF4D",
                pointRadius: 5,
                fill: true,
                tension: 0.25,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: "#292F27" },
                    ticks: { color: "#737B70" }
                },
                y: {
                    grid: { color: "#292F27" },
                    ticks: { color: "#737B70" }
                }
            }
        }
    });
}

// ==========================================================================
// 6. ANALYTICS & AI INSIGHTS CONTROLLER
// ==========================================================================
async function loadAnalyticsView() {
    try {
        const weekly = await Api.getWeeklyAnalytics(State.currentDate);

        document.getElementById("analytics-total-steps").textContent = weekly.total_steps.toLocaleString();
        document.getElementById("analytics-avg-steps").textContent = `Avg: ${weekly.avg_daily_steps.toLocaleString()} / day`;

        document.getElementById("analytics-total-workouts").textContent = weekly.total_workouts;
        document.getElementById("analytics-workout-mins").textContent = `${weekly.total_workout_minutes} total minutes`;

        document.getElementById("analytics-avg-sleep").textContent = weekly.avg_sleep_hours.toFixed(1);
        document.getElementById("analytics-goal-rate").textContent = `${weekly.goal_completion_rate}%`;
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function generateAIInsights() {
    const btn = document.getElementById("btn-generate-ai-insights");
    const container = document.getElementById("ai-insights-container");
    btn.disabled = true;
    btn.textContent = "Analyzing fitness data...";

    try {
        const res = await Api.getWeeklyInsights(State.currentDate);
        if (!res.insights || res.insights.length === 0) {
            container.innerHTML = `<div style="color:var(--text-muted);">No insights generated. Log more activity across the week.</div>`;
            return;
        }

        container.innerHTML = res.insights.map(item => `
            <div style="background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:12px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="color:var(--text-primary); font-size:0.92rem;">${escapeHtml(item.category)}</strong>
                    <span class="badge green">${escapeHtml(item.badge)}</span>
                </div>
                <p style="font-size:0.86rem; color:var(--text-secondary); line-height:1.45;">${escapeHtml(item.insight)}</p>
            </div>
        `).join("");
        showToast("AI fitness analysis updated!");
    } catch (err) {
        showToast(err.message || "Failed to generate AI insights", "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
            Generate AI Weekly Summary
        `;
    }
}

// ==========================================================================
// 7. PROFILE CONTROLLER
// ==========================================================================
async function loadProfileView() {
    try {
        const profile = await Api.getProfile();
        if (!profile) return;

        document.getElementById("prof-fitness-goal").value = profile.fitness_goal || "maintain";
        document.getElementById("prof-preferred-units").value = profile.preferred_units || "metric";
        document.getElementById("prof-height").value = profile.height_cm || "";
        document.getElementById("prof-target-weight").value = profile.target_weight || "";
        document.getElementById("prof-daily-steps").value = profile.daily_step_target || 10000;
        document.getElementById("prof-daily-water").value = profile.daily_water_target || 2500;
        document.getElementById("prof-daily-sleep").value = profile.daily_sleep_target || 8.0;
    } catch (err) {
        showToast(err.message, "error");
    }
}

// ==========================================================================
// Live Weather Pill
// ==========================================================================
async function loadWeatherAdvisory() {
    try {
        const weather = await Api.getWeatherSuggestion(40.7128, -74.0060);
        const pillText = document.getElementById("weather-text");
        if (weather.available) {
            pillText.textContent = `${weather.temperature_c}°C, ${weather.condition} — ${weather.workout_suggestion}`;
        } else {
            pillText.textContent = "Indoor & Gym training recommended";
        }
    } catch {
        document.getElementById("weather-text").textContent = "Gym training ready";
    }
}

// ==========================================================================
// Helpers & Utilities
// ==========================================================================
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getBadgeColor(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("strength")) return "green";
    if (t.includes("cardio") || t.includes("running")) return "blue";
    if (t.includes("hiit")) return "orange";
    return "purple";
}

function getMealBadgeColor(category) {
    const c = (category || "").toLowerCase();
    if (c === "breakfast") return "orange";
    if (c === "lunch") return "blue";
    if (c === "dinner") return "purple";
    return "green";
}

// ==========================================================================
// Event Listeners Initialization
// ==========================================================================
document.addEventListener("DOMContentLoaded", async () => {
    // 1. Initialize Date picker with today
    const datePicker = document.getElementById("active-date-picker");
    datePicker.value = State.currentDate;
    datePicker.addEventListener("change", (e) => {
        State.currentDate = e.target.value;
        refreshActiveView();
    });

    document.getElementById("btn-prev-day").addEventListener("click", () => {
        const d = new Date(State.currentDate);
        d.setDate(d.getDate() - 1);
        State.currentDate = d.toISOString().split("T")[0];
        datePicker.value = State.currentDate;
        refreshActiveView();
    });

    document.getElementById("btn-next-day").addEventListener("click", () => {
        const d = new Date(State.currentDate);
        d.setDate(d.getDate() + 1);
        State.currentDate = d.toISOString().split("T")[0];
        datePicker.value = State.currentDate;
        refreshActiveView();
    });

    // 2. Navigation Item clicks
    document.querySelectorAll(".nav-item, .mobile-nav-item").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            if (view) switchView(view);
        });
    });

    // 3. Close Modal handlers
    document.querySelectorAll("[data-close-modal]").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const modalId = e.currentTarget.dataset.closeModal;
            closeModal(modalId);
        });
    });

    // 4. Auth Modal Toggles
    const btnToggleLogin = document.getElementById("btn-toggle-login");
    const btnToggleRegister = document.getElementById("btn-toggle-register");
    const formLogin = document.getElementById("form-auth-login");
    const formRegister = document.getElementById("form-auth-register");

    btnToggleLogin.addEventListener("click", () => {
        btnToggleLogin.className = "btn btn-sm btn-primary auth-toggle-btn";
        btnToggleRegister.className = "btn btn-sm btn-secondary auth-toggle-btn";
        formLogin.style.display = "block";
        formRegister.style.display = "none";
    });

    btnToggleRegister.addEventListener("click", () => {
        btnToggleRegister.className = "btn btn-sm btn-primary auth-toggle-btn";
        btnToggleLogin.className = "btn btn-sm btn-secondary auth-toggle-btn";
        formRegister.style.display = "block";
        formLogin.style.display = "none";
    });

    // 5. Auth form submissions
    formLogin.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        try {
            await Auth.login(email, password);
            closeModal("modal-auth");
            showToast("Welcome back!");
            updateUserUI();
            refreshActiveView();
        } catch (err) {
            showToast(err.message || "Failed to sign in", "error");
        }
    });

    formRegister.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("reg-name").value;
        const email = document.getElementById("reg-email").value;
        const password = document.getElementById("reg-password").value;
        try {
            await Auth.register(name, email, password);
            closeModal("modal-auth");
            showToast("Account created successfully!");
            updateUserUI();
            refreshActiveView();
        } catch (err) {
            showToast(err.message || "Failed to create account", "error");
        }
    });

    document.getElementById("btn-logout-sidebar").addEventListener("click", () => {
        if (confirm("Log out of FitTrack?")) {
            Auth.logout();
        }
    });

    // 6. Quick Action buttons
    document.getElementById("btn-quick-workout")?.addEventListener("click", () => openModal("modal-workout"));
    document.getElementById("btn-add-workout-modal")?.addEventListener("click", () => openModal("modal-workout"));
    document.getElementById("qa-log-weight")?.addEventListener("click", () => openModal("modal-weight"));
    document.getElementById("btn-open-log-weight-modal")?.addEventListener("click", () => openModal("modal-weight"));
    document.getElementById("qa-log-food")?.addEventListener("click", () => openModal("modal-food"));
    document.getElementById("btn-open-log-food-modal")?.addEventListener("click", () => openModal("modal-food"));
    document.getElementById("qa-log-workout")?.addEventListener("click", () => openModal("modal-workout"));
    document.getElementById("qa-log-activity")?.addEventListener("click", () => openModal("modal-activity"));
    document.getElementById("btn-open-log-activity-modal")?.addEventListener("click", () => openModal("modal-activity"));
    document.getElementById("qa-log-sleep")?.addEventListener("click", () => switchView("sleep"));

    // Mobile More Drawer controls
    document.getElementById("btn-mobile-more")?.addEventListener("click", toggleMobileMoreSheet);
    document.getElementById("btn-close-more-sheet")?.addEventListener("click", closeMobileMoreSheet);
    document.getElementById("mobile-more-backdrop")?.addEventListener("click", closeMobileMoreSheet);
    document.getElementById("btn-logout-mobile-sheet")?.addEventListener("click", () => {
        if (confirm("Log out of FitTrack?")) {
            Auth.logout();
        }
    });
    document.querySelectorAll(".mobile-more-item[data-view]").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            if (view) switchView(view);
        });
    });

    document.getElementById("qa-quick-water-250")?.addEventListener("click", async () => {
        try {
            await Api.logWater({ quantity_ml: 250 });
            showToast("+250ml water logged!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // 7. Workout Exercises Dynamic Row
    document.getElementById("btn-add-exercise-row")?.addEventListener("click", () => addExerciseRow());

    // 8. Workout Form Submission
    document.getElementById("form-workout")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("w-input-name").value;
        const type = document.getElementById("w-input-type").value;
        const duration = parseInt(document.getElementById("w-input-duration").value, 10);
        const startTime = document.getElementById("w-input-start-time").value;
        const calories = document.getElementById("w-input-calories").value;
        const notes = document.getElementById("w-input-notes").value;

        const exerciseRows = document.querySelectorAll("#workout-exercises-rows-container .exercise-form-row");
        const exercises = Array.from(exerciseRows).map(row => ({
            exercise_name: row.querySelector(".ex-name").value.trim(),
            sets: parseInt(row.querySelector(".ex-sets").value, 10) || 1,
            repetitions: parseInt(row.querySelector(".ex-reps").value, 10) || 0,
            weight_used: parseFloat(row.querySelector(".ex-weight").value) || 0.0,
        })).filter(ex => ex.exercise_name.length > 0);

        try {
            await Api.createWorkout({
                workout_name: name,
                workout_type: type,
                duration_minutes: duration,
                start_time: new Date(startTime).toISOString(),
                estimated_calories: calories ? parseFloat(calories) : null,
                notes: notes || null,
                exercises,
            });
            closeModal("modal-workout");
            document.getElementById("form-workout").reset();
            document.getElementById("workout-exercises-rows-container").innerHTML = "";
            showToast("Workout saved!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // Set default workout start time to now
    const nowIso = new Date().toISOString().slice(0, 16);
    const startInput = document.getElementById("w-input-start-time");
    if (startInput) startInput.value = nowIso;

    // 9. Weight Form Submission
    document.getElementById("input-weight-date").value = State.currentDate;
    document.getElementById("form-log-weight")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const weight = parseFloat(document.getElementById("input-weight-kg").value);
        const dateVal = document.getElementById("input-weight-date").value;
        const note = document.getElementById("input-weight-note").value;

        try {
            await Api.createWeight({
                weight_kg: weight,
                measurement_date: dateVal,
                note: note || null,
            });
            closeModal("modal-weight");
            document.getElementById("form-log-weight").reset();
            showToast("Weight logged successfully!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // 10. Food Form Submission
    document.getElementById("form-log-food")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("food-input-name").value;
        const category = document.getElementById("food-input-category").value;
        const calories = parseFloat(document.getElementById("food-input-calories").value);
        const protein = parseFloat(document.getElementById("food-input-protein").value) || 0;
        const carbs = parseFloat(document.getElementById("food-input-carbs").value) || 0;
        const fat = parseFloat(document.getElementById("food-input-fat").value) || 0;

        try {
            await Api.logFood({
                food_name: name,
                meal_category: category,
                serving_quantity: 1.0,
                calories,
                protein_g: protein,
                carbs_g: carbs,
                fat_g: fat,
                consumed_at: new Date(State.currentDate).toISOString(),
            });
            closeModal("modal-food");
            document.getElementById("form-log-food").reset();
            showToast("Food entry logged!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // 11. Food Search Action
    const searchFoodAction = async () => {
        const query = document.getElementById("food-search-input").value.trim();
        if (!query) return;
        const resultsContainer = document.getElementById("food-search-results");
        resultsContainer.innerHTML = `<div style="color:var(--text-secondary); font-size:0.9rem;">Searching database...</div>`;

        try {
            const data = await Api.searchFood(query);
            if (!data.results || data.results.length === 0) {
                resultsContainer.innerHTML = `<div style="color:var(--text-muted); font-size:0.9rem;">No matching foods found.</div>`;
                return;
            }

            resultsContainer.innerHTML = data.results.map(f => `
                <div style="background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:10px; padding:12px;">
                    <strong style="color:var(--text-primary); font-size:0.92rem;">${escapeHtml(f.name)}</strong>
                    <div style="font-size:0.8rem; color:var(--text-secondary); margin:4px 0 8px;">
                        ${f.calories} kcal • P: ${f.protein_g}g • C: ${f.carbs_g}g • F: ${f.fat_g}g
                    </div>
                    <button class="btn btn-secondary btn-sm btn-quick-add-food" 
                        data-name="${escapeHtml(f.name)}"
                        data-calories="${f.calories}"
                        data-protein="${f.protein_g}"
                        data-carbs="${f.carbs_g}"
                        data-fat="${f.fat_g}"
                        style="width:100%;">
                        + Log This Food
                    </button>
                </div>
            `).join("");

            resultsContainer.querySelectorAll(".btn-quick-add-food").forEach(btn => {
                btn.addEventListener("click", async (e) => {
                    const ds = e.currentTarget.dataset;
                    await Api.logFood({
                        food_name: ds.name,
                        meal_category: "snack",
                        serving_quantity: 1.0,
                        calories: parseFloat(ds.calories),
                        protein_g: parseFloat(ds.protein),
                        carbs_g: parseFloat(ds.carbs),
                        fat_g: parseFloat(ds.fat),
                        consumed_at: new Date(State.currentDate).toISOString(),
                        data_source: "USDA / Food Database"
                    });
                    showToast(`Added ${ds.name} to meal log!`);
                    loadNutrition();
                });
            });
        } catch (err) {
            resultsContainer.innerHTML = `<div style="color:var(--danger); font-size:0.85rem;">${err.message}</div>`;
        }
    };

    document.getElementById("btn-search-food-action")?.addEventListener("click", searchFoodAction);
    document.getElementById("food-search-input")?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            searchFoodAction();
        }
    });

    // Activity Form Submission
    const actDateInput = document.getElementById("act-input-date");
    if (actDateInput) actDateInput.value = State.currentDate;
    document.getElementById("form-log-activity")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const dateVal = document.getElementById("act-input-date").value;
        const steps = parseInt(document.getElementById("act-input-steps").value, 10);
        const activeMins = parseInt(document.getElementById("act-input-active").value, 10);
        const cardioMins = parseInt(document.getElementById("act-input-cardio").value, 10) || 0;
        const calories = document.getElementById("act-input-calories").value;

        try {
            await Api.recordActivity({
                activity_date: dateVal,
                steps,
                active_minutes: activeMins,
                cardio_minutes: cardioMins,
                calories_burned: calories ? parseFloat(calories) : null,
                data_source: "manual",
            });
            closeModal("modal-activity");
            document.getElementById("form-log-activity").reset();
            showToast("Daily activity logged!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // Water quick add buttons (Dashboard & Hydration page)
    document.querySelectorAll(".btn-quick-water").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const ml = parseInt(e.currentTarget.dataset.amount, 10);
            await Api.logWater({ quantity_ml: ml });
            showToast(`+${ml}ml water logged!`);
            refreshActiveView();
        });
    });

    document.getElementById("form-custom-water-page")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = document.getElementById("input-custom-water-page-ml");
        const ml = parseInt(input.value, 10);
        await Api.logWater({ quantity_ml: ml });
        input.value = "";
        showToast(`+${ml}ml water logged!`);
        refreshActiveView();
    });

    // Sleep Page Form
    const sleepStartInput = document.getElementById("sleep-start-time-page");
    const sleepEndInput = document.getElementById("sleep-end-time-page");
    if (sleepStartInput && sleepEndInput) {
        const yesterdayEve = new Date();
        yesterdayEve.setDate(yesterdayEve.getDate() - 1);
        yesterdayEve.setHours(23, 0, 0, 0);
        sleepStartInput.value = yesterdayEve.toISOString().slice(0, 16);

        const todayMorn = new Date();
        todayMorn.setHours(7, 30, 0, 0);
        sleepEndInput.value = todayMorn.toISOString().slice(0, 16);
    }

    document.getElementById("form-record-sleep-page")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const start = document.getElementById("sleep-start-time-page").value;
        const end = document.getElementById("sleep-end-time-page").value;
        const rating = parseInt(document.getElementById("sleep-quality-page").value, 10);

        try {
            await Api.logSleep({
                sleep_start: new Date(start).toISOString(),
                sleep_end: new Date(end).toISOString(),
                quality_rating: rating,
            });
            showToast("Sleep session recorded!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // 14. AI Insights & CSV Exports
    document.getElementById("btn-generate-ai-insights")?.addEventListener("click", generateAIInsights);

    document.querySelectorAll(".btn-export-csv").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const type = e.currentTarget.dataset.type;
            try {
                showToast(`Preparing ${type} CSV export...`);
                await Api.exportCsv(type);
                showToast("CSV downloaded successfully!");
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    });

    // 15. User Profile Form Submission
    document.getElementById("form-user-profile")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const goal = document.getElementById("prof-fitness-goal").value;
        const units = document.getElementById("prof-preferred-units").value;
        const height = parseFloat(document.getElementById("prof-height").value) || null;
        const targetWeight = parseFloat(document.getElementById("prof-target-weight").value) || null;
        const steps = parseInt(document.getElementById("prof-daily-steps").value, 10);
        const water = parseInt(document.getElementById("prof-daily-water").value, 10);
        const sleep = parseFloat(document.getElementById("prof-daily-sleep").value);

        try {
            await Api.updateProfile({
                fitness_goal: goal,
                preferred_units: units,
                height_cm: height,
                target_weight: targetWeight,
                daily_step_target: steps,
                daily_water_target: water,
                daily_sleep_target: sleep,
            });
            showToast("Profile settings saved!");
            refreshActiveView();
        } catch (err) {
            showToast(err.message, "error");
        }
    });

    // 16. Exercise Catalog Search
    document.getElementById("exercise-search-input")?.addEventListener("input", (e) => {
        const q = e.target.value;
        const m = document.getElementById("exercise-muscle-filter").value;
        loadExerciseCatalog(q, m);
    });

    document.getElementById("exercise-muscle-filter")?.addEventListener("change", (e) => {
        const m = e.target.value;
        const q = document.getElementById("exercise-search-input").value;
        loadExerciseCatalog(q, m);
    });

    // 17. Workout type filters
    document.querySelectorAll(".filter-wtype-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".filter-wtype-btn").forEach(b => b.className = "btn btn-sm btn-secondary filter-wtype-btn");
            e.currentTarget.className = "btn btn-sm btn-primary filter-wtype-btn";
            State.workoutFilter = e.currentTarget.dataset.type;
            loadWorkouts();
        });
    });

    // 18. Initialize Auth Session
    const user = await Auth.init();
    if (!user) {
        // Open Auth modal if not logged in
        openModal("modal-auth");
    } else {
        updateUserUI();
        refreshActiveView();
    }

    // Load weather advisory in background
    loadWeatherAdvisory();
});

function updateUserUI() {
    if (!Auth.currentUser) return;
    const user = Auth.currentUser;
    const nameEl = document.getElementById("sidebar-user-name");
    const emailEl = document.getElementById("sidebar-user-email");
    const avatarEl = document.getElementById("user-avatar-initials");

    if (nameEl) nameEl.textContent = user.name;
    if (emailEl) emailEl.textContent = user.email;
    if (avatarEl) avatarEl.textContent = user.name.charAt(0).toUpperCase();
}
