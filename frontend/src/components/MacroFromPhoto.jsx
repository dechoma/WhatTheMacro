import React, { useState } from "react";
import { API_URL } from "../config";
import MacroEditor from "./MacroEditor";

export default function MacroFromPhoto({ date, onAdd }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [macroResult, setMacroResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showEditor, setShowEditor] = useState(false);

  const handleImageChange = (e) => {
    setError("");
    setMacroResult(null);
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError("");
    setMacroResult(null);
    const formData = new FormData();
    formData.append("image", selectedFile);
    try {
      const res = await fetch(`${API_URL}/estimate-macro`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to analyze image");
      const macro = await res.json();
      if (macro.barcode && (macro.protein == null)) {
        setError("Barcode detected, but no macros found.");
      } else {
        setMacroResult(macro);
        setShowEditor(true);
      }
    } catch (err) {
      setError("Could not analyze the image.");
    }
    setLoading(false);
  };

  const handleSaveMacro = async (macroData) => {
    // Dodajemy wpis do bazy
    const formData = new FormData();
    formData.append("date", date);
    formData.append("protein", macroData.protein);
    formData.append("carbs", macroData.carbs);
    formData.append("fat", macroData.fat);
    formData.append("calories", macroData.calories);
    formData.append("description", macroData.description || "");
    formData.append("amount", macroData.amount);

    try {
      await fetch(`${API_URL}/intake`, {
        method: "POST",
        body: formData,
      });
      setMacroResult(null);
      setSelectedFile(null);
      setShowEditor(false);
      onAdd && onAdd();
    } catch {
      setError("Failed to add to intake.");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow p-4 mb-4 text-center">
      <div className="mb-2 font-semibold">Add meal via photo</div>
      <input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        className="mb-2"
      />
      <button
        className="bg-green-600 text-white rounded px-3 py-1 ml-2"
        disabled={!selectedFile || loading}
        onClick={handleAnalyze}
      >
        {loading ? "Analyzing..." : "Analyze Photo"}
      </button>
      {error && <div className="text-red-600 mt-2">{error}</div>}
      {showEditor && macroResult && (
        <MacroEditor
          initial={{
            protein: macroResult.protein,
            carbs: macroResult.carbs,
            fat: macroResult.fat,
            calories: macroResult.calories,
            amount: 100, // lub macroResult.base_amount jeśli masz
            description: macroResult.description
          }}
          onSave={handleSaveMacro}
          onCancel={() => setShowEditor(false)}
        />
      )}
    </div>
  );
}
