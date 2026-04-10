import { Link } from "react-router-dom";

function recommendationTone(value, violation) {
  if (violation) {
    return {
      chip: "bg-[#ff7bac]/20 text-[#a9285d]",
      surface: "theme-card-red",
    };
  }

  if (value === "decrease") {
    return {
      chip: "bg-[#ff931e]/18 text-[#a85c00]",
      surface: "theme-card-amber",
    };
  }

  if (value === "increase") {
    return {
      chip: "bg-[#3fa9f5]/16 text-[#0d69a9]",
      surface: "theme-card-blue",
    };
  }

  return {
    chip: "bg-[#bdccd4]/25 text-[#466072]",
    surface: "theme-card-neutral",
  };
}

function Delta({ value, positiveIsGood = false }) {
  const positive = value >= 0;
  const tone = positive === positiveIsGood ? "text-emerald-700" : "text-rose-700";
  const sign = positive ? "+" : "";
  return <span className={tone}>{`${sign}${value.toFixed(2)}%`}</span>;
}

function SKUCard({ row, compact, selected, onSelectSku }) {
  const tone = recommendationTone(row.recommendation, row.margin_violation);

  return (
    <article
      className={`rounded-[1.2rem] border p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] transition ${
        selected
          ? "theme-dark-panel text-white"
          : `${tone.surface} hover:border-sky-200`
      }`}
    >
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.15em] ${
                selected ? "bg-white/10 text-white" : tone.chip
              }`}
            >
              {row.margin_violation ? "margin risk" : row.recommendation}
            </span>
            {row.kvi_flag && (
              <span
                className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.15em] ${
                  selected ? "bg-[#3fa9f5]/18 text-[#d7f1ff]" : "bg-[#3fa9f5]/12 text-[#0d69a9]"
                }`}
              >
                KVI
              </span>
            )}
            <span className={`text-[11px] uppercase tracking-[0.18em] ${selected ? "text-slate-300" : "text-slate-500"}`}>
              {row.sku}
            </span>
          </div>

          <h3 className={`mt-3 text-lg font-semibold ${selected ? "text-white" : "text-slate-950"}`}>
            {row.product_name}
          </h3>
          <p className={`mt-2 max-w-3xl text-sm leading-6 ${selected ? "text-slate-300" : "text-slate-600"}`}>
            {row.ai_explainer}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => onSelectSku?.(row.sku)}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
              selected ? "theme-link-button text-slate-950 hover:bg-white" : "theme-button-primary hover:brightness-105"
            }`}
          >
            {selected ? "Selected" : "Review SKU"}
          </button>
          <Link
            to={`/skus/${row.sku}`}
            className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
              selected ? "border-white/20 text-white hover:bg-white/10" : "border-slate-300 text-slate-700 hover:bg-sky-50"
            }`}
          >
            Open detail
          </Link>
        </div>
      </div>

      <div className={`mt-4 grid gap-2.5 ${compact ? "sm:grid-cols-2 xl:grid-cols-2" : "sm:grid-cols-2 xl:grid-cols-6"}`}>
        <Metric label="Current" value={`$${row.tawfeer_price.toFixed(2)}`} selected={selected} />
        <Metric label="Suggested" value={`$${row.suggested_price.toFixed(2)}`} selected={selected} />
        <Metric label="Gap" value={<Delta value={row.price_gap} positiveIsGood={false} />} selected={selected} />
        <Metric label="Margin" value={`${row.margin.toFixed(2)}%`} selected={selected} />
        <Metric label="Confidence" value={`${(row.confidence * 100).toFixed(0)}%`} selected={selected} />
        {!compact && <Metric label="Reference" value={`$${row.reference_price.toFixed(2)}`} selected={selected} />}
      </div>
    </article>
  );
}

function Metric({ label, value, selected }) {
  return (
    <div className={`rounded-[0.95rem] border px-3 py-3 ${selected ? "border-white/10 bg-white/6" : "border-slate-200 bg-white/70"}`}>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.16em] ${selected ? "text-slate-400" : "text-slate-500"}`}>
        {label}
      </p>
      <div className={`mt-1.5 text-base font-semibold ${selected ? "text-white" : "text-slate-950"}`}>{value}</div>
    </div>
  );
}

export default function SKUtable({ rows, compact = false, selectedSku, onSelectSku }) {
  return (
    <div className="space-y-3">
      {rows.map((row) => (
        <SKUCard
          key={row.sku}
          row={row}
          compact={compact}
          selected={selectedSku === row.sku}
          onSelectSku={onSelectSku}
        />
      ))}

      {!rows.length && (
        <div className={`glass-panel rounded-[1.25rem] border-dashed text-center text-slate-500 ${compact ? "px-4 py-6" : "px-6 py-12"}`}>
          No SKUs match the current filters.
        </div>
      )}
    </div>
  );
}
