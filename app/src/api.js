import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE, // set in app/.env.local
  timeout: 10000,
});

export const health = () => api.get("/health").then(r => r.data);

// UC-1: User Registration
export const register = (username, name, email, password) =>
  api.post("/users/register", { username, name, email, password }).then(r => r.data);

// UC-2: User Login
export const login = (username, password) =>
  api.post("/users/login", { username, password }).then(r => r.data);

// UC-3: View Profile
export const getProfile = (username) =>
  api.get(`/users/${encodeURIComponent(username)}/profile`).then(r => r.data);

// UC-4: Edit Profile
export const updateProfile = (username, data) =>
  api.put(`/users/${encodeURIComponent(username)}/profile`, data).then(r => r.data);

// UC-5: Follow User
export const follow = (me, other) =>
  api.post(`/users/${encodeURIComponent(me)}/follow/${encodeURIComponent(other)}`).then(r => r.data);

// UC-6: Unfollow User
export const unfollow = (me, other) =>
  api.delete(`/users/${encodeURIComponent(me)}/follow/${encodeURIComponent(other)}`).then(r => r.data);

// UC-7: View Connections
export const getConnections = (username) =>
  api.get(`/users/${encodeURIComponent(username)}/connections`).then(r => r.data);

// UC-8: Mutual Connections
export const getMutualConnections = (username, other) =>
  api.get(`/users/${encodeURIComponent(username)}/mutual?other=${encodeURIComponent(other)}`).then(r => r.data);

// UC-9: Recommendations
export const recommendations = (me) =>
  api.get(`/users/${encodeURIComponent(me)}/recommendations`).then(r => r.data);

// UC-10: Search Users
export const searchUsers = (query, limit = 20) =>
  api.get(`/users/search?query=${encodeURIComponent(query)}&limit=${limit}`).then(r => r.data);

// UC-11: Popular Users
export const getPopularUsers = (limit = 20) =>
  api.get(`/users/popular?limit=${limit}`).then(r => r.data);

// Feed
export const feed = (me) =>
  api.get(`/users/${encodeURIComponent(me)}/feed`).then(r => r.data);
