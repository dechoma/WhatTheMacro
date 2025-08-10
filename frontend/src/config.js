// src/config.js
// Default: relative /api (works in Docker with Nginx proxy)
export const API_URL = import.meta.env.VITE_API_URL || "/api";
