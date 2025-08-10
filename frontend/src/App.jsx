import React, { useState, useEffect } from "react";
import TargetForm from "./components/TargetForm.jsx";
import MacroChart from "./components/MacroChart.jsx";
import IntakeList from "./components/IntakeList.jsx";
import MacroFromPhoto from "./components/MacroFromPhoto.jsx";
import TargetHistory from "./components/TargetHistory.jsx";
import { API_URL } from "./config";
import Auth from "./components/Auth.jsx";

export default function App() {
  const [date] = useState(() => new Date().toISOString().slice(0, 10));
  const [intake, setIntake] = useState({ sum: { protein: 0, carbs: 0, fat: 0, calories: 0 }, entries: [] });
  const [target, setTarget] = useState({ protein: 120, carbs: 195, fat: 60, calories: 1800 });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [historyKey, setHistoryKey] = useState(0);
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
  const refreshIntake = () => fetch(`${API_URL}/intake/${date}`, { headers: authHeaders }).then(res => res.json()).then(setIntake);
  const refreshTarget = () => fetch(`${API_URL}/targets`, { headers: authHeaders }).then(res => res.json()).then(setTarget);

  useEffect(() => {
    if (!token) return;
    refreshIntake();
    refreshTarget();
  }, [date, token]);

  const handleTargetInput = e => setTarget({ ...target, [e.target.name]: Number(e.target.value) });

  const handleDeleteEntry = async (id) => {
  if (!window.confirm("Na pewno usunąć ten wpis?")) return;
  await fetch(`${API_URL}/intake/${id}`, { method: "DELETE", headers: token ? { Authorization: `Bearer ${token}` } : {} });
  refreshIntake();
  };

  const handleTargetSave = e => {
    e.preventDefault();
    setSaving(true);
    fetch(`${API_URL}/targets`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(target),
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(() => {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 1500);
        refreshTarget();
        setHistoryKey(x => x + 1);
      })
      .catch(() => {
        setSuccess(false);
        alert("Authorization required. Please log in again.");
      })
      .finally(() => setSaving(false));
  };

  const handleAuthenticated = (newToken) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
  };

  return (
    <div className="max-w-lg mx-auto py-6 px-3">
      <h1 className="text-2xl font-bold mb-3 text-center">Makro Tracker</h1>
      <div className="flex justify-center mb-4">
        {token ? (
          <button onClick={handleLogout} className="text-sm text-red-700 underline">Logout</button>
        ) : null}
      </div>

      {!token ? (
        <Auth onAuthenticated={handleAuthenticated} />
      ) : null}

      {token ? (
        <>
          <MacroChart intake={intake.sum} target={target} />
          <MacroFromPhoto date={date} onAdd={refreshIntake} token={token} />
          <IntakeList entries={intake.entries} onDelete={handleDeleteEntry} />
          <TargetHistory key={historyKey} token={token} />
          <br/>
          <br/>
          <TargetForm
            target={target}
            onChange={handleTargetInput}
            onSave={handleTargetSave}
            saving={saving}
            success={success}
          />
        </>
      ) : null}
    </div>
  );
}
