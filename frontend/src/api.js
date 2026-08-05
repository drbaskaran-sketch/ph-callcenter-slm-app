// Central fetch wrapper — attaches the JWT bearer token issued by
// POST /api/v1/auth/login to every request, and forces a re-login if the
// backend ever responds 401 (expired/invalid token).
const API_BASE = '/api/v1';
const TOKEN_KEY = 'ph_auth_token';
const USER_KEY = 'ph_auth_user';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// Notify the app to drop back to the login screen (e.g. after a 401).
function forceLogout() {
  clearSession();
  window.dispatchEvent(new Event('ph-auth-expired'));
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || 'Login failed');
  }
  const data = await res.json();
  setSession(data.access_token, data.user);
  return data.user;
}

// Drop-in replacement for fetch() against our API — same signature, plus
// auto-auth and auto-logout-on-401. Callers still pass paths like
// `${API_BASE}/branches`, so this mirrors that by accepting a full path.
export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(path, { ...options, headers });
  if (res.status === 401) {
    forceLogout();
  }
  return res;
}

export { API_BASE };
