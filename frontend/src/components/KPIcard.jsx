export default function KPIcard({ label, value, tone = "neutral" }) {
  const toneMap = {
    neutral: "theme-card-neutral",
    blue: "theme-card-blue",
    green: "theme-card-green",
    amber: "theme-card-amber",
    red: "theme-card-red",
  };

  return (
    <article className={`rounded-[1.1rem] border p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] ${toneMap[tone]}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
    </article>
  );
}
