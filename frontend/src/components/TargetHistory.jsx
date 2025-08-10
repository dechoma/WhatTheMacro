import React, { useEffect, useState } from "react";
import { API_URL } from "../config";

export default function TargetHistory({ token }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/targets/history`, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      .then(res => res.json())
      .then(setHistory);
  }, [token]);

  if (!history.length) return null;

  return (
    <div className="bg-white rounded-xl shadow p-4 mt-4">
      <h3 className="font-semibold mb-2 text-center">Target history</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="pr-2">Date</th>
              <th className="pr-2">Proteins</th>
              <th className="pr-2">Carbs</th>
              <th className="pr-2">Fats</th>
              <th className="pr-2">Kcal</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, idx) => (
              <tr key={entry.ts + idx} className="border-b last:border-b-0">
                <td className="pr-2 whitespace-nowrap">{new Date(entry.ts).toLocaleString()}</td>
                <td className="pr-2">{entry.protein}g</td>
                <td className="pr-2">{entry.carbs}g</td>
                <td className="pr-2">{entry.fat}g</td>
                <td className="pr-2">{entry.calories}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
