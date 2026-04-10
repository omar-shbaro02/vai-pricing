import { useEffect, useState } from "react";
import { runSimulation } from "../services/api";

function recommendationTone(recommendation) {
  if (recommendation === "increase") return "bg-[#3fa9f5]/14 text-[#0c6aa9] border-[#3fa9f5]/24";
  if (recommendation === "decrease") return "bg-[#ff931e]/14 text-[#9c5a00] border-[#ff931e]/24";
  return "bg-[#bdccd4]/20 text-[#456173] border-[#bdccd4]/32";
}

export default function SimulationPanel({
  skuId,
  suggestedPrice,
  recommendation,
  decisionExplanation,
  confidence,
  currentPrice,
}) {
  const [proposedPrice, setProposedPrice] = useState(suggestedPrice ?? 0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setProposedPrice(suggestedPrice ?? 0);
  }, [suggestedPrice]);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await runSimulation({
        sku: skuId,
        proposed_price: Number(proposedPrice),
      });
      setResult(response);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  }

  const hasResult = result != null;

  return (
    <div className="space-y-4">
      <section className="theme-dark-panel rounded-[1.5rem] p-5 text-white">
        <div className="flex flex-wrap items-center gap-3">
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-300">Agent rationale</p>
          <span className={`rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${recommendationTone(recommendation)}`}>
            {recommendation}
          </span>
        </div>

        <p className="mt-4 text-sm leading-6 text-slate-300">{decisionExplanation}</p>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <Metric label="Current" value={`$${currentPrice?.toFixed(2) ?? "0.00"}`} dark />
          <Metric label="Suggested" value={`$${suggestedPrice?.toFixed(2) ?? "0.00"}`} dark />
          <Metric label="Confidence" value={`${((confidence ?? 0) * 100).toFixed(0)}%`} dark />
        </div>
      </section>

      <section className="glass-panel rounded-[1.5rem] p-5">
        <div className="mb-4">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Simulation</p>
          <h3 className="mt-1 text-xl font-semibold text-slate-950">Test a new price</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Try an alternative price and compare the projected demand, revenue, margin dollars, and margin rate.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-700">
            Proposed price
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={proposedPrice}
              onChange={(event) => setProposedPrice(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-950 focus:ring-4 focus:ring-slate-200"
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            className="theme-button-primary w-full rounded-full px-5 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-400 disabled:shadow-none"
          >
            {loading ? "Running..." : "Run simulation"}
          </button>
        </form>

        {error && <p className="mt-4 text-sm text-rose-700">{error}</p>}

        {hasResult && (
          <div className="mt-5 space-y-4">
            <div className="space-y-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Simulation output
                </p>
                <h4 className="mt-1 text-lg font-semibold text-slate-950">
                  Projected outcome at ${result.proposed_price.toFixed(2)}
                </h4>
              </div>
              <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-600">
                Current ${result.current_price.toFixed(2)}
              </span>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <Metric label="Volume change" value={`${result.expected_volume_change.toFixed(2)}%`} tone="amber" />
              <Metric label="Expected units sold" value={Math.ceil(result.expected_units_sold)} tone="neutral" />
              <Metric label="Revenue impact" value={`$${result.expected_revenue_impact.toFixed(2)}`} tone="blue" />
              <Metric label="Margin impact" value={`$${result.expected_margin_impact.toFixed(2)}`} tone="green" />
              <Metric label="Projected margin" value={`${result.projected_margin_percent.toFixed(2)}%`} tone="neutral" />
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function Metric({ label, value, dark = false, tone = "neutral" }) {
  const toneMap = {
    neutral: "theme-card-neutral",
    green: "theme-card-green",
    amber: "theme-card-amber",
    blue: "theme-card-blue",
  };

  return (
    <div className={`min-w-0 rounded-[1rem] border p-4 ${dark ? "border-white/10 bg-white/6" : toneMap[tone]}`}>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.16em] ${dark ? "text-slate-400" : "text-slate-500"}`}>{label}</p>
      <p className={`mt-1.5 break-words text-lg font-semibold ${dark ? "text-white" : "text-slate-950"}`}>{value}</p>
    </div>
  );
}
