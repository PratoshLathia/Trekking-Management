export const API_BASE = "http://127.0.0.1:5000";

export async function apiFetch(path, options = {}) {
    const token = localStorage.getItem("token");

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    return fetch(`${API_BASE}${path}`, { ...options, headers });
}
