import React, { useState } from 'react';

export default function MacroAdjust({ aiMacros, baseAmount, unit = "g", onConfirm }) {
  const [customAmount, setCustomAmount] = useState(baseAmount);
  const ratio = customAmount / baseAmount;
  const adjusted = {
    protein: +(aiMacros.protein * ratio).toFixed(1),
    carbs: +(aiMacros.carbs * ratio).toFixed(1),
    fat: +(aiMacros.fat * ratio).toFixed(1),
    calories: +(aiMacros.calories * ratio).toFixed(0)
  };

  return (
    <div className="bg-gray-100 p-4 rounded-xl shadow mb-4">
      <div className="mb-2 font-bold">Porcja bazowa: {baseAmount}{unit} (AI)</div>
      <div className="mb-3">
        <button
          className="bg-blue-500 text-white rounded px-4 py-1 mr-2"
          onClick={() => { onConfirm({ ...aiMacros, amount: baseAmount }); }}>
          Dodaj całość ({baseAmount}{unit})
        </button>
      </div>
      <div className="mb-2">Albo wpisz swoją ilość:</div>
      <input
        type="number"
        min={1}
        value={customAmount}
        onChange={e => setCustomAmount(Number(e.target.value))}
        className="w-24 rounded p-2 mr-2"
      />{unit}
      <button
        className="bg-green-500 text-white rounded px-4 py-1 ml-2"
        onClick={() => onConfirm({ ...adjusted, amount: customAmount })}>
        Dodaj tyle
      </button>
      <div className="font-semibold mt-3 mb-2">
        <div>Białko: {adjusted.protein}g</div>
        <div>Węgle: {adjusted.carbs}g</div>
        <div>Tłuszcz: {adjusted.fat}g</div>
        <div>Kcal: {adjusted.calories}</div>
      </div>
    </div>
  );
}
