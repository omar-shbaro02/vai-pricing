const filterConfig = [
  { key: "kvis_only", label: "KVIs only" },
  { key: "increases_only", label: "Increase actions" },
  { key: "decreases_only", label: "Decrease actions" },
  { key: "margin_violations_only", label: "Margin risks" },
];

export default function Filters({ filters, onChange }) {
  return (
    <div className="glass-panel rounded-[1.25rem] p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Filters</p>
          <h3 className="mt-1 text-base font-semibold text-slate-950">Refine the queue</h3>
        </div>

        <div className="flex flex-wrap gap-2.5">
          {filterConfig.map((filter) => (
            <label
              key={filter.key}
              className={`cursor-pointer rounded-full border px-3 py-2 text-sm font-medium transition ${
                filters[filter.key]
                  ? "border-transparent theme-button-primary"
                  : "border-slate-200 bg-white/80 text-slate-700 hover:bg-sky-50"
              }`}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={filters[filter.key]}
                onChange={() => onChange(filter.key)}
              />
              {filter.label}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
