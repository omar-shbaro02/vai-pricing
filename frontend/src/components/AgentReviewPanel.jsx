import { Link } from "react-router-dom";

function priorityTone(priority) {
  if (priority === "high") return "bg-white/12 text-[#ffd3e3] ring-1 ring-inset ring-[#ff7bac]/30";
  if (priority === "medium") return "bg-white/12 text-[#ffe0b5] ring-1 ring-inset ring-[#ff931e]/30";
  return "bg-white/12 text-[#d9f6c2] ring-1 ring-inset ring-[#7ac943]/30";
}

function recommendationTone(recommendation) {
  if (recommendation === "increase") return "text-[#a9e0ff]";
  if (recommendation === "decrease") return "text-[#ffd49d]";
  return "text-[#d8e5ef]";
}

function DarkStat({ label, value }) {
  return (
    <div className="theme-dark-soft rounded-[1rem] px-4 py-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-1.5 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}

export default function AgentReviewPanel({ review, selectedSku, onSelectSku, onRefresh, refreshing }) {
  if (!review) {
    return null;
  }

  const selected = review.selected_sku;

  return (
    <section className="theme-pdf-blue-panel rounded-[1.5rem] p-5 text-white sm:p-6">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(22rem,0.8fr)]">
        <div className="space-y-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-3xl">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-300">AI pricing copilot</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white">
                Priority actions across the current pricing queue.
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">{review.overview}</p>
            </div>

            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="inline-flex items-center justify-center rounded-full border border-white/12 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/16 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {refreshing ? "Refreshing..." : "Re-run pricing agent"}
            </button>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <DarkStat label="SKUs in view" value={review.totals.total} />
            <DarkStat label="Need increase" value={review.totals.increase} />
            <DarkStat label="Need decrease" value={review.totals.decrease} />
            <DarkStat label="Margin risks" value={review.totals.margin_violations} />
          </div>

          <div className="theme-dark-soft rounded-[1.25rem] p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">Priority list</p>
                <h3 className="mt-1 text-lg font-semibold text-white">SKUs that need action</h3>
              </div>
            </div>

            <div className="mt-4 grid gap-2.5">
              {review.focus_actions.map((item) => (
                <button
                  key={item.sku}
                  type="button"
                  onClick={() => onSelectSku(item.sku)}
                  className={`rounded-[1rem] border px-4 py-3.5 text-left transition ${
                    selectedSku === item.sku
                      ? "border-[#3fa9f5]/45 bg-[#3fa9f5]/16"
                      : "border-white/8 bg-black/10 hover:bg-white/8"
                  }`}
                >
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.15em] ${priorityTone(item.priority)}`}>
                          {item.priority}
                        </span>
                        <span className={`text-[11px] font-semibold uppercase tracking-[0.16em] ${recommendationTone(item.recommendation)}`}>
                          {item.recommendation}
                        </span>
                        <span className="text-[11px] uppercase tracking-[0.16em] text-slate-400">{item.sku}</span>
                      </div>
                      <h4 className="mt-2 truncate text-base font-semibold text-white">{item.product_name}</h4>
                      <p className="mt-1.5 text-sm leading-5 text-slate-300">{item.action}</p>
                    </div>

                    <div className="grid min-w-[10rem] gap-1 text-sm text-slate-300">
                      <div className="flex justify-between gap-4">
                        <span>Current</span>
                        <span>${item.current_price.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between gap-4">
                        <span>Suggested</span>
                        <span>${item.suggested_price.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between gap-4">
                        <span>Gap</span>
                        <span>{item.price_gap.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between gap-4">
                        <span>Confidence</span>
                        <span>{(item.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="theme-dark-soft rounded-[1.25rem] p-4">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">Selected SKU</p>
          {selected ? (
            <div className="mt-4 space-y-4">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-[11px] font-semibold uppercase tracking-[0.16em] ${recommendationTone(selected.recommendation)}`}>
                    {selected.recommendation}
                  </span>
                  <span className="text-[11px] uppercase tracking-[0.16em] text-slate-400">{selected.sku}</span>
                </div>
                <h3 className="mt-2 text-xl font-semibold text-white">{selected.product_name}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{selected.summary}</p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <DarkStat label="Current price" value={`$${selected.current_price.toFixed(2)}`} />
                <DarkStat label="Suggested price" value={`$${selected.suggested_price.toFixed(2)}`} />
                <DarkStat label="Margin" value={`${selected.margin.toFixed(2)}%`} />
                <DarkStat
                  label="Floor / confidence"
                  value={`${selected.margin_floor.toFixed(1)}% / ${(selected.confidence * 100).toFixed(0)}%`}
                />
              </div>

              <div className="theme-dark-soft rounded-[1rem] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                  Recommended next steps
                </p>
                <div className="mt-3 space-y-2">
                  {selected.next_steps.map((step) => (
                    <p key={step} className="rounded-[0.9rem] border border-white/8 bg-black/10 px-3 py-2.5 text-sm leading-5 text-slate-200">
                      {step}
                    </p>
                  ))}
                </div>
              </div>

              <Link
                to={`/skus/${selected.sku}`}
                className="theme-link-button inline-flex rounded-full px-4 py-2.5 text-sm font-semibold transition hover:bg-white"
              >
                Open full SKU detail
              </Link>
            </div>
          ) : (
            <div className="mt-4 rounded-[1rem] border border-dashed border-white/12 bg-white/5 p-5 text-sm leading-6 text-slate-300">
              Select a priority SKU to see its summary, next steps, and direct link into detailed analysis.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
