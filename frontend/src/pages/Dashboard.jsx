import { useEffect, useRef, useState } from "react";
import AgentReviewPanel from "../components/AgentReviewPanel";
import Filters from "../components/Filters";
import KPIcard from "../components/KPIcard";
import SKUtable from "../components/SKUtable";
import { fetchAgentReview, fetchDashboard, fetchSKUs, runAgent } from "../services/api";

const defaultFilters = {
  kvis_only: false,
  increases_only: false,
  decreases_only: false,
  margin_violations_only: false,
};

export default function Dashboard({ tableOnly = false }) {
  const [dashboard, setDashboard] = useState(null);
  const [rows, setRows] = useState([]);
  const [review, setReview] = useState(null);
  const [selectedSku, setSelectedSku] = useState("");
  const [filters, setFilters] = useState(defaultFilters);
  const [error, setError] = useState("");
  const [initialLoading, setInitialLoading] = useState(true);
  const [queueRefreshing, setQueueRefreshing] = useState(false);
  const [agentRunning, setAgentRunning] = useState(false);
  const hasLoadedRef = useRef(false);

  useEffect(() => {
    async function load() {
      const firstLoad = !hasLoadedRef.current;
      if (!firstLoad) {
        setQueueRefreshing(true);
      }
      setError("");
      try {
        const requests = tableOnly
          ? [fetchSKUs(filters), fetchAgentReview(filters)]
          : [fetchDashboard(), fetchSKUs(filters), fetchAgentReview(filters)];
        const responses = await Promise.all(requests);

        if (tableOnly) {
          const [skuRows, agentReview] = responses;
          setRows(skuRows);
          setReview(agentReview);
          setDashboard(null);
          setSelectedSku(agentReview.focus_actions[0]?.sku || "");
          return;
        }

        const [dashboardData, skuRows, agentReview] = responses;
        setDashboard(dashboardData);
        setRows(skuRows);
        setReview(agentReview);
        setSelectedSku(agentReview.focus_actions[0]?.sku || "");
      } catch (loadError) {
        setError(loadError.message);
      } finally {
        hasLoadedRef.current = true;
        setInitialLoading(false);
        setQueueRefreshing(false);
      }
    }

    load();
  }, [filters, tableOnly]);

  useEffect(() => {
    if (!review) {
      return;
    }

    if (!selectedSku) {
      setReview((current) => {
        if (!current || current.selected_sku == null) {
          return current;
        }
        return { ...current, selected_sku: null };
      });
      return;
    }

    async function loadSelectedReview() {
      try {
        const agentReview = await fetchAgentReview({ ...filters, skuId: selectedSku });
        setReview(agentReview);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadSelectedReview();
  }, [filters, review?.overview, selectedSku]);

  async function handleRunAgent() {
    setAgentRunning(true);
    setError("");
    try {
      await runAgent();
      const requests = tableOnly
        ? [fetchSKUs(filters), fetchAgentReview({ ...filters, skuId: selectedSku || undefined })]
        : [
            fetchDashboard(),
            fetchSKUs(filters),
            fetchAgentReview({ ...filters, skuId: selectedSku || undefined }),
          ];
      const responses = await Promise.all(requests);

      if (tableOnly) {
        const [skuRows, agentReview] = responses;
        setRows(skuRows);
        setReview(agentReview);
      } else {
        const [dashboardData, skuRows, agentReview] = responses;
        setDashboard(dashboardData);
        setRows(skuRows);
        setReview(agentReview);
      }
    } catch (runError) {
      setError(runError.message);
    } finally {
      setAgentRunning(false);
    }
  }

  function toggleFilter(key) {
    setFilters((current) => ({ ...current, [key]: !current[key] }));
  }

  if (initialLoading) {
    return <StatePanel tone="default">Loading pricing data...</StatePanel>;
  }

  if (error) {
    return <StatePanel tone="error">{error}</StatePanel>;
  }

  const overviewStats = dashboard
    ? [
        { label: "SKUs analyzed", value: dashboard.total_skus_analyzed, tone: "blue" },
        { label: "Actions recommended", value: dashboard.recommended_price_changes, tone: "neutral" },
        { label: "Overpriced vs market", value: `${dashboard.overpriced_percentage.toFixed(1)}%`, tone: "amber" },
        { label: "Average margin", value: `${dashboard.average_margin.toFixed(1)}%`, tone: "green" },
        { label: "KVI compliance", value: `${dashboard.kvi_compliance_score.toFixed(1)}%`, tone: "red" },
      ]
    : [];

  return (
    <div className="space-y-5">
      {!tableOnly && dashboard && (
        <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_23rem]">
          <div className="glass-panel rounded-[1.5rem] p-5 sm:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl">
                <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                  Portfolio overview
                </p>
                <h2 className="section-title mt-2 text-3xl text-slate-950 sm:text-[2.4rem]">
                  A clearer operating view of the pricing queue.
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
                  Review portfolio health, understand where pressure is building, and move directly into SKU-level action.
                </p>
              </div>

              <div className="theme-card-neutral rounded-[1.1rem] border px-4 py-3 text-sm text-slate-600">
                Updated from the latest dashboard and agent review responses.
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
              {overviewStats.map((item) => (
                <KPIcard key={item.label} label={item.label} value={item.value} tone={item.tone} />
              ))}
            </div>
          </div>

          <div className="theme-pdf-blue-panel rounded-[1.5rem] p-5 text-white">
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-300">Focus today</p>
            <div className="mt-3 space-y-3 text-sm leading-6 text-slate-300">
              <p>{review?.overview}</p>
              <p>{review?.portfolio_review}</p>
              <p className="font-medium text-white">{review?.execution_note}</p>
            </div>
          </div>
        </section>
      )}

      <AgentReviewPanel
        review={review}
        selectedSku={selectedSku}
        onSelectSku={setSelectedSku}
        onRefresh={handleRunAgent}
        refreshing={agentRunning}
      />

      <section className={`grid gap-5 ${!tableOnly && dashboard ? "xl:grid-cols-[minmax(0,1fr)_22rem]" : ""}`}>
        <div className="space-y-4">
          <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">SKU explorer</p>
              <h2 className="mt-1 text-2xl font-semibold text-slate-950">
                {tableOnly ? "Full pricing queue" : "Action-ready SKU analysis"}
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Filter the queue, compare recommendations, and open deeper SKU detail when you need it.
              </p>
            </div>
            {queueRefreshing && (
              <div className="text-sm font-medium text-slate-500">Updating queue...</div>
            )}
          </div>

          <Filters filters={filters} onChange={toggleFilter} />
          <SKUtable rows={rows} selectedSku={selectedSku} onSelectSku={setSelectedSku} />
        </div>

        {!tableOnly && dashboard && (
          <aside className="space-y-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Watchlist</p>
              <h2 className="mt-1 text-2xl font-semibold text-slate-950">Flagged SKUs</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                A narrow list of SKUs that deserve immediate attention.
              </p>
            </div>
            <SKUtable
              rows={dashboard.flagged_skus}
              compact
              selectedSku={selectedSku}
              onSelectSku={setSelectedSku}
            />
          </aside>
        )}
      </section>
    </div>
  );
}

function StatePanel({ children, tone = "default" }) {
  const className =
    tone === "error"
      ? "rounded-[1.5rem] border border-rose-200 bg-rose-50 p-6 text-rose-800"
      : "glass-panel rounded-[1.5rem] p-6 text-slate-700";

  return <div className={className}>{children}</div>;
}
