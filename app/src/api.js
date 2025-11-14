import { health, register, follow, unfollow, recommendations, feed } from "./api";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE, // set in app/.env.local
  timeout: 10000,
});

export const health = () => api.get("/health").then(r => r.data);

export const register = (username, name) =>
  api.post("/users/register", { username, name }).then(r => r.data);

export const follow = (me, other) =>
  api.post(`/users/${encodeURIComponent(me)}/follow/${encodeURIComponent(other)}`).then(r => r.data);

export const unfollow = (me, other) =>
  api.delete(`/users/${encodeURIComponent(me)}/follow/${encodeURIComponent(other)}`).then(r => r.data);

export const recommendations = (me) =>
  api.get(`/users/${encodeURIComponent(me)}/recommendations`).then(r => r.data);

export const feed = (me) =>
  api.get(`/users/${encodeURIComponent(me)}/feed`).then(r => r.data);
