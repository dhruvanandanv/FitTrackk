/**
 * FitTrack API Client
 * Dynamic base URL support and standard authenticated fetch wrapper.
 */

const getApiBaseUrl = () => {
    // Check if injected by environment or configured
    if (window.FITTRACK_API_URL) {
        return window.FITTRACK_API_URL.replace(/\/$/, "");
    }
    // If running in development or served from backend
    if (window.location.origin && window.location.origin.startsWith("http")) {
        return `${window.location.origin}/api/v1`;
    }
    return "http://localhost:8000/api/v1";
};

export const API_BASE = getApiBaseUrl();

export const Storage = {
    TOKEN_KEY: "fittrack_auth_token",
    USER_KEY: "fittrack_auth_user",

    getToken() {
        return localStorage.getItem(this.TOKEN_KEY) || sessionStorage.getItem(this.TOKEN_KEY);
    },

    setToken(token, remember = true) {
        if (remember) {
            localStorage.setItem(this.TOKEN_KEY, token);
        } else {
            sessionStorage.setItem(this.TOKEN_KEY, token);
        }
    },

    getUser() {
        const u = localStorage.getItem(this.USER_KEY) || sessionStorage.getItem(this.USER_KEY);
        try {
            return u ? JSON.parse(u) : null;
        } catch {
            return null;
        }
    },

    setUser(user, remember = true) {
        const str = JSON.stringify(user);
        if (remember) {
            localStorage.setItem(this.USER_KEY, str);
        } else {
            sessionStorage.setItem(this.USER_KEY, str);
        }
    },

    clear() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        sessionStorage.removeItem(this.TOKEN_KEY);
        sessionStorage.removeItem(this.USER_KEY);
    }
};

export async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    const token = Storage.getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
    };

    if (config.body && typeof config.body === "object" && !(config.body instanceof FormData)) {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);

        if (response.status === 401) {
            // Token expired or unauthorized
            Storage.clear();
            window.dispatchEvent(new CustomEvent("fittrack:unauthorized"));
            throw new Error("Session expired. Please log in again.");
        }

        if (response.status === 204) {
            return null;
        }

        // Handle CSV blob responses
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("text/csv")) {
            return await response.blob();
        }

        const data = await response.json();

        if (!response.ok) {
            const errorMsg = data.detail || (data.message ? data.message : `Request failed with status ${response.status}`);
            throw new Error(typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg));
        }

        return data;
    } catch (err) {
        console.error(`API Error [${endpoint}]:`, err);
        throw err;
    }
}

export const Api = {
    // Auth
    register: (payload) => apiRequest("/auth/register", { method: "POST", body: payload }),
    login: (payload) => apiRequest("/auth/login", { method: "POST", body: payload }),
    logout: () => apiRequest("/auth/logout", { method: "POST" }),
    getMe: () => apiRequest("/auth/me", { method: "GET" }),

    // Profile
    getProfile: () => apiRequest("/profile", { method: "GET" }),
    updateProfile: (payload) => apiRequest("/profile", { method: "PATCH", body: payload }),

    // Dashboard
    getDashboard: (dateStr) => apiRequest(`/dashboard${dateStr ? `?date=${dateStr}` : ""}`, { method: "GET" }),

    // Weight
    createWeight: (payload) => apiRequest("/weight", { method: "POST", body: payload }),
    getWeights: (params = "") => apiRequest(`/weight${params ? `?${params}` : ""}`, { method: "GET" }),
    updateWeight: (id, payload) => apiRequest(`/weight/${id}`, { method: "PATCH", body: payload }),
    deleteWeight: (id) => apiRequest(`/weight/${id}`, { method: "DELETE" }),

    // Activity
    recordActivity: (payload) => apiRequest("/activity", { method: "POST", body: payload }),
    getActivities: (params = "") => apiRequest(`/activity${params ? `?${params}` : ""}`, { method: "GET" }),

    // Workouts
    createWorkout: (payload) => apiRequest("/workouts", { method: "POST", body: payload }),
    getWorkouts: (params = "") => apiRequest(`/workouts${params ? `?${params}` : ""}`, { method: "GET" }),
    getWorkout: (id) => apiRequest(`/workouts/${id}`, { method: "GET" }),
    updateWorkout: (id, payload) => apiRequest(`/workouts/${id}`, { method: "PATCH", body: payload }),
    deleteWorkout: (id) => apiRequest(`/workouts/${id}`, { method: "DELETE" }),

    // Water
    logWater: (payload) => apiRequest("/water", { method: "POST", body: payload }),
    getWater: (dateStr) => apiRequest(`/water${dateStr ? `?date=${dateStr}` : ""}`, { method: "GET" }),
    deleteWater: (id) => apiRequest(`/water/${id}`, { method: "DELETE" }),

    // Sleep
    logSleep: (payload) => apiRequest("/sleep", { method: "POST", body: payload }),
    getSleep: (limit = 30) => apiRequest(`/sleep?limit=${limit}`, { method: "GET" }),
    deleteSleep: (id) => apiRequest(`/sleep/${id}`, { method: "DELETE" }),

    // Food & Nutrition
    logFood: (payload) => apiRequest("/food", { method: "POST", body: payload }),
    getFood: (dateStr) => apiRequest(`/food${dateStr ? `?date=${dateStr}` : ""}`, { method: "GET" }),
    deleteFood: (id) => apiRequest(`/food/${id}`, { method: "DELETE" }),
    searchFood: (query) => apiRequest(`/food/search?q=${encodeURIComponent(query)}`, { method: "GET" }),

    // Analytics & Exports
    getWeeklyAnalytics: (dateStr) => apiRequest(`/analytics/weekly${dateStr ? `?date=${dateStr}` : ""}`, { method: "GET" }),
    getMonthlyAnalytics: (dateStr) => apiRequest(`/analytics/monthly${dateStr ? `?date=${dateStr}` : ""}`, { method: "GET" }),
    getWeightAnalytics: () => apiRequest("/analytics/weight", { method: "GET" }),
    getWorkoutAnalytics: () => apiRequest("/analytics/workouts", { method: "GET" }),
    exportCsv: async (dataType = "all") => {
        const blob = await apiRequest(`/analytics/export?data_type=${dataType}`, { method: "GET" });
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `fittrack_${dataType}_export.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);
    },

    // Integrations
    getExerciseCatalog: (query, muscle) => {
        let q = [];
        if (query) q.push(`q=${encodeURIComponent(query)}`);
        if (muscle) q.push(`muscle_group=${encodeURIComponent(muscle)}`);
        return apiRequest(`/integrations/exercises${q.length ? `?${q.join("&")}` : ""}`, { method: "GET" });
    },
    getWeatherSuggestion: (lat, lon) => apiRequest(`/integrations/weather?lat=${lat}&lon=${lon}`, { method: "GET" }),
    getWeeklyInsights: (dateStr) => apiRequest(`/insights/weekly${dateStr ? `?date=${dateStr}` : ""}`, { method: "POST" }),
};
