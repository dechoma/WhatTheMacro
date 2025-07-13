// src/components/TargetForm.jsx
import React from "react";

export default function TargetForm({ target, onChange, onSave, saving, success }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 mb-4">
      <div className="font-semibold mb-2 text-center">My Targetse (edit):</div>
      <form
        className="flex flex-wrap gap-4 justify-center items-center"
        onSubmit={onSave}
        autoComplete="off"
      >
        <label>
          Proteins:
          <input
            type="number"
            name="protein"
            value={target.protein}
            onChange={onChange}
            className="ml-1 w-16 rounded px-1"
            min={0}
          />g
        </label>
        <label>
          Carbs:
          <input
            type="number"
            name="carbs"
            value={target.carbs}
            onChange={onChange}
            className="ml-1 w-16 rounded px-1"
            min={0}
          />g
        </label>
        <label>
          Fats:
          <input
            type="number"
            name="fat"
            value={target.fat}
            onChange={onChange}
            className="ml-1 w-16 rounded px-1"
            min={0}
          />g
        </label>
        <label>
          Kcal:
          <input
            type="number"
            name="calories"
            value={target.calories}
            onChange={onChange}
            className="ml-1 w-20 rounded px-1"
            min={0}
          />
        </label>
        <button
          type="submit"
          className="bg-blue-500 text-white rounded px-3 py-1 ml-4"
          disabled={saving}
        >
          {saving ? "Savinf..." : "Save new targets"}
        </button>
        {success && (
          <span className="ml-2 text-green-600 text-sm">Saved!</span>
        )}
      </form>
    </div>
  );
}
