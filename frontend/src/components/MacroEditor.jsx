import React, { useState, useRef } from "react";

// Przykład propsów: initial: {protein, carbs, fat, calories, amount, description}
export default function MacroEditor({ initial, onSave, onCancel }) {
  const baseAmount = initial.amount || 100;
  const baseMacros = useRef({
    protein: initial.protein,
    carbs: initial.carbs,
    fat: initial.fat,
    calories: initial.calories,
    amount: baseAmount,
  });

  const [amount, setAmount] = useState(baseAmount);
  const [protein, setProtein] = useState(initial.protein);
  const [carbs, setCarbs] = useState(initial.carbs);
  const [fat, setFat] = useState(initial.fat);
  const [calories, setCalories] = useState(initial.calories);
  const [description, setDescription] = useState(initial.description || "");

  // Automatyczne przeliczanie przy zmianie gramatury
  const handleAmountChange = (e) => {
    const val = Number(e.target.value);
    setAmount(val);
    setProtein(Number(((baseMacros.current.protein / baseMacros.current.amount) * val).toFixed(2)));
    setCarbs(Number(((baseMacros.current.carbs / baseMacros.current.amount) * val).toFixed(2)));
    setFat(Number(((baseMacros.current.fat / baseMacros.current.amount) * val).toFixed(2)));
    setCalories(Number(((baseMacros.current.calories / baseMacros.current.amount) * val).toFixed(2)));
  };

  return (
    <div className="bg-gray-50 p-4 rounded mb-2 shadow">
      <div>
        <label>
          Weight [g]:{" "}
          <input
            type="number"
            min={1}
            step={1}
            value={amount}
            onChange={handleAmountChange}
            className="w-20 px-1 rounded"
          />
        </label>
      </div>
      <div className="flex gap-3 mt-3 flex-wrap">
        <label>
          Proteins:
          <input
            type="number"
            value={protein}
            onChange={(e) => setProtein(Number(e.target.value))}
            className="w-16 px-1 rounded ml-1"
          />g
        </label>
        <label>
          Carbs:
          <input
            type="number"
            value={carbs}
            onChange={(e) => setCarbs(Number(e.target.value))}
            className="w-16 px-1 rounded ml-1"
          />g
        </label>
        <label>
          Fat:
          <input
            type="number"
            value={fat}
            onChange={(e) => setFat(Number(e.target.value))}
            className="w-16 px-1 rounded ml-1"
          />g
        </label>
        <label>
          Kcal:
          <input
            type="number"
            value={calories}
            onChange={(e) => setCalories(Number(e.target.value))}
            className="w-20 px-1 rounded ml-1"
          />
        </label>
      </div>
      <div className="mt-3">
        <label>
          Description:&nbsp;
          <input
            type="text"
            value={description}
            onChange={e=>setDescription(e.target.value)}
            className="w-48 px-1 rounded"
          />
        </label>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          className="bg-blue-600 text-white rounded px-3 py-1"
          onClick={() =>
            onSave({ protein, carbs, fat, calories, amount, description })
          }
        >
          Save
        </button>
        <button
          className="bg-gray-400 text-white rounded px-3 py-1"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
