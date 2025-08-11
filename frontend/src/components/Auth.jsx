import React, { useState } from "react";
import { API_URL } from "../config";

export default function Auth({ onAuthenticated }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [adminPassword, setAdminPassword] = useState(import.meta.env.VITE_ADMIN_PASSWORD || "");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError("");
    setLoading(true);
    try {
      const body = new URLSearchParams();
      body.append("username", email);
      body.append("password", password);
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!res.ok) throw new Error("Login failed");
      const data = await res.json();
      onAuthenticated(data.access_token);
    } catch (e) {
      setError("Invalid email or password.");
    }
    setLoading(false);
  };

  const handleSignup = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Admin-Password": adminPassword },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error("Signup failed");
      const data = await res.json();
      onAuthenticated(data.access_token);
    } catch (e) {
      setError("Could not sign up. Check admin password and email.");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-sm mx-auto bg-white rounded-xl shadow p-4 mt-6">
      <h2 className="text-xl font-semibold mb-3 text-center">Sign in</h2>
      <div className="flex flex-col gap-2">
        <input
          type="email"
          placeholder="Email"
          className="border rounded px-2 py-1"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="border rounded px-2 py-1"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          placeholder="Admin password (required to sign up)"
          className="border rounded px-2 py-1"
          value={adminPassword}
          onChange={(e) => setAdminPassword(e.target.value)}
        />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <div className="flex gap-2 mt-2">
          <button
            className="flex-1 bg-blue-600 text-white rounded px-3 py-1"
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? "..." : "Login"}
          </button>
          <button
            className="flex-1 bg-gray-700 text-white rounded px-3 py-1"
            onClick={handleSignup}
            disabled={loading}
          >
            {loading ? "..." : "Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
}


