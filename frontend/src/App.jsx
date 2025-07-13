import React, { useState, useEffect } from "react";
import TargetForm from "./components/TargetForm.jsx";
import MacroChart from "./components/MacroChart.jsx";
import IntakeList from "./components/IntakeList.jsx";
import MacroFromPhoto from "./components/MacroFromPhoto.jsx";
import TargetHistory from "./components/TargetHistory.jsx";
import { API_URL } from "./config";

export default function App() {
  const [date] = useState(() => new Date().toISOString().slice(0, 10));
  const [intake, setIntake] = useState({ sum: { protein: 0, carbs: 0, fat: 0, calories: 0 }, entries: [] });
  const [target, setTarget] = useState({ protein: 120, carbs: 195, fat: 60, calories: 1800 });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [historyKey, setHistoryKey] = useState(0);

  const refreshIntake = () => fetch(`${API_URL}/intake/${date}`).then(res => res.json()).then(setIntake);
  const refreshTarget = () => fetch(`${API_URL}/targets`).then(res => res.json()).then(setTarget);

  useEffect(() => {
    refreshIntake();
    refreshTarget();
  }, [date]);

  const handleTargetInput = e => setTarget({ ...target, [e.target.name]: Number(e.target.value) });

  const handleDeleteEntry = async (id) => {
  if (!window.confirm("Na pewno usunąć ten wpis?")) return;
  await fetch(`${API_URL}/intake/${id}`, { method: "DELETE" });
  refreshIntake();
  };

  const handleTargetSave = e => {
    e.preventDefault();
    setSaving(true);
    fetch(`${API_URL}/targets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(target),
    })
      .then(() => {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 1500);
        refreshTarget();
        setHistoryKey(x => x + 1);
      })
      .finally(() => setSaving(false));
  };

  return (
    <div className="max-w-lg mx-auto py-6 px-3">
      <h1 className="text-2xl font-bold mb-3 text-center">Makro Tracker</h1>

      <MacroChart intake={intake.sum} target={target} />
      <MacroFromPhoto date={date} onAdd={refreshIntake} />
<IntakeList entries={intake.entries} onDelete={handleDeleteEntry} />
      <TargetHistory key={historyKey} />
      <br/>
      <br/>
      <TargetForm
        target={target}
        onChange={handleTargetInput}
        onSave={handleTargetSave}
        saving={saving}
        success={success}
      />
    </div>
  );
}
