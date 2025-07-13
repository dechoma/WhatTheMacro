import React from "react";

export default function IntakeList({ entries, onDelete }) {
  return (
    <div>
      <h2 className="font-bold mb-2 text-lg">Today meals</h2>
      {entries.length === 0 && (
        <div className="text-gray-400">No logged Meals</div>
      )}
      {entries.map((entry) => (
        <div
          key={entry.id}
          className="flex items-center bg-white shadow p-2 mb-2 rounded"
        >
          <div className="flex-1">
            <div>
              <b>{entry.description || "Meal"}</b> — {entry.amount || 100}g
            </div>
            <div className="text-sm text-gray-700">
              B: {entry.protein}g | W: {entry.carbs}g | T: {entry.fat}g | Kcal: {entry.calories}
            </div>
          </div>
          <button
            className="ml-2 bg-red-600 text-white px-2 py-1 rounded"
            onClick={() => onDelete(entry.id)}
            title="Delete"
          >
            🗑️
          </button>
        </div>
      ))}
    </div>
  );
}
