import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import SKUChatbot from "../components/SKUChatbot";
import SimulationPanel from "../components/SimulationPanel";
import { fetchSKUDetail } from "../services/api";

function DetailCard({ label, value, tone = "neutral" }) {
  const toneMap = {
    neutral: "theme-card-neutral",
    green: "theme-card-green",
    red: "theme-card-red",
    amber: "theme-card-amber",
    blue: "theme-card-blue",
  };

  return (
    <div className={`rounded-[1.1rem] border p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] ${toneMap[tone]}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

export default function SKUdetails() {
  const { skuId } = useParams();
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDetail();
  }, [skuId]);

  async function loadDetail() {
    setError("");
    try {
      const response = await fetchSKUDetail(skuId);
      setDetail(response);
    } catch (loadError) {
      setError(loadError.message);
    }
  }

  if (error) {
    return <div className="rounded-[1.5rem] border border-rose-200 bg-rose-50 p-6 text-rose-800">{error}</div>;
  }

  if (!detail) {
    return <div className="glass-panel rounded-[1.5rem] p-6">Loading SKU detail...</div>;
  }

  return (
    <div className="space-y-5">
      <section className="glass-panel rounded-[1.5rem] p-5 sm:p-6">
        <Link to="/skus" className="text-sm font-medium text-slate-700">
          Back to SKU queue
        </Link>

        <div className="mt-4 grid gap-5 xl:grid-cols-[minmax(0,1fr)_22rem]">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              SKU detail
            </p>
            <h2 className="section-title mt-2 text-3xl text-slate-950 sm:text-[2.6rem]">{detail.product_name}</h2>
            <p className="mt-2 text-sm text-slate-600">
              {detail.sku} | {detail.category} | {detail.pack_size}
            </p>
            <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-700">{detail.decision_explanation}</p>
          </div>

          <div className="theme-dark-panel rounded-[1.25rem] p-5 text-white">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">Decision snapshot</p>
            <div className="mt-4 grid gap-3">
              <BriefTile label="Recommendation" value={detail.recommendation} dark />
              <BriefTile label="Confidence" value={`${(detail.confidence * 100).toFixed(0)}%`} dark />
              <BriefTile label="Price gap vs market" value={`${detail.price_gap.toFixed(2)}%`} dark />
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <DetailCard label="Current price" value={`$${detail.current_price.toFixed(2)}`} tone="blue" />
        <DetailCard label="Suggested price" value={`$${detail.suggested_price.toFixed(2)}`} tone="green" />
        <DetailCard
          label="Margin"
          value={`${detail.margin.toFixed(2)}%`}
          tone={detail.margin < detail.margin_floor ? "red" : "neutral"}
        />
        <DetailCard label="Units sold last week" value={detail.units_sold_last_week} tone="amber" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <div className="space-y-5">
          <div className="glass-panel rounded-[1.5rem] p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Market context</p>
                <h3 className="mt-1 text-xl font-semibold text-slate-950">Competitor prices</h3>
              </div>
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {Object.entries(detail.all_competitor_prices).map(([name, value]) => (
                <DetailCard key={name} label={name} value={`$${value.toFixed(2)}`} />
              ))}
            </div>
          </div>

          <div className="glass-panel rounded-[1.5rem] p-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Decision drivers</p>
            <h3 className="mt-1 text-xl font-semibold text-slate-950">Recommendation breakdown</h3>

            <div className="mt-4 grid gap-3 md:grid-cols-3">
              <DetailCard label="Inventory" value={detail.inventory} />
              <DetailCard label="Confidence" value={`${(detail.confidence * 100).toFixed(0)}%`} tone="blue" />
              <DetailCard label="Price gap" value={`${detail.price_gap.toFixed(2)}%`} tone="amber" />
            </div>

            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <DetailCard
                label="Stock cover"
                value={detail.stock_cover != null ? detail.stock_cover.toFixed(2) : "N/A"}
              />
              <DetailCard label="Inventory interpretation" value={detail.inventory_interpretation || "N/A"} />
            </div>
          </div>

          <div className="glass-panel rounded-[1.5rem] p-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Modeled impact</p>
            <h3 className="mt-1 text-xl font-semibold text-slate-950">Suggested price outcome</h3>

            <div className="mt-4 grid gap-3 md:grid-cols-2 2xl:grid-cols-5">
              <DetailCard
                label="Expected volume change"
                value={`${detail.simulation_impact.expected_volume_change.toFixed(2)}%`}
                tone="amber"
              />
              <DetailCard
                label="Expected units sold"
                value={Math.ceil(detail.simulation_impact.expected_units_sold)}
              />
              <DetailCard
                label="Expected revenue impact"
                value={`$${detail.simulation_impact.expected_revenue_impact.toFixed(2)}`}
                tone="blue"
              />
              <DetailCard
                label="Expected margin impact"
                value={`$${detail.simulation_impact.expected_margin_impact.toFixed(2)}`}
                tone="green"
              />
              <DetailCard
                label="Projected margin"
                value={`${detail.simulation_impact.projected_margin_percent.toFixed(2)}%`}
              />
            </div>
          </div>

          <SKUChatbot
            skuId={detail.sku}
            productName={detail.product_name}
            onDecisionUpdated={loadDetail}
          />
        </div>

        <SimulationPanel
          skuId={detail.sku}
          suggestedPrice={detail.suggested_price}
          recommendation={detail.recommendation}
          decisionExplanation={detail.decision_explanation}
          confidence={detail.confidence}
          currentPrice={detail.current_price}
        />
      </section>
    </div>
  );
}

function BriefTile({ label, value, dark = false }) {
  return (
    <div className={`rounded-[1rem] border px-4 py-4 ${dark ? "border-white/10 bg-white/6" : "border-slate-200 bg-slate-50"}`}>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.16em] ${dark ? "text-slate-400" : "text-slate-500"}`}>
        {label}
      </p>
      <p className={`mt-1.5 text-lg font-semibold ${dark ? "text-white" : "text-slate-950"}`}>{value}</p>
    </div>
  );
}
