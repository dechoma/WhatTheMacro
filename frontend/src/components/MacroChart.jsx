const COLORS = {
  "Proteins": "#0088FE",
  "Carbs": "#FFBB28",
  "Fats": "#FF5252",
};

export default function MacroChart({ intake, target }) {
  const data = [
    { name: "Proteins", value: intake.protein, max: target.protein, color: COLORS["Proteins"] },
    { name: "Carbs", value: intake.carbs, max: target.carbs, color: COLORS["Carbs"] },
    { name: "Fats", value: intake.fat, max: target.fat, color: COLORS["Fats"] },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl p-5 mb-6">
      <h2 className="text-lg font-bold text-center mb-3">Daily macro</h2>
      {data.map((item) => {
        const percent = Math.min(item.value / item.max * 100, 100);
        return (
          <div key={item.name} className="mb-3 flex flex-col items-center">
            <div className="flex justify-between w-[70%] mb-1">
              <span style={{ color: item.color, fontWeight: 600 }}>{item.name}</span>
              <span className="text-xs">{item.value || 0} / {item.max}g</span>
            </div>
            <div style={{
              background: "#e5e7eb",
              borderRadius: 16,
              height: 16,
              width: "70%",
              overflow: "hidden",
            }}>
              <div style={{
                width: percent + "%",
                background: item.color,
                height: "100%",
                transition: "width 0.5s",
              }} />
            </div>
          </div>
        );
      })}
      <div className="text-center mt-2 text-sm">
        Left: {Math.max(target.protein - (intake.protein || 0), 0)}g protein,&nbsp;
        {Math.max(target.carbs - (intake.carbs || 0), 0)}g carb,&nbsp;
        {Math.max(target.fat - (intake.fat || 0), 0)}g fat
      </div>
    </div>
  );
}
