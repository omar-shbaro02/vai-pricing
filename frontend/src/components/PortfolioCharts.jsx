function clampPercent(value) {
  return Math.max(0, Math.min(100, value));
}

function formatPercent(value) {
  return `${clampPercent(value).toFixed(1)}%`;
}

function formatCount(value) {
  return `${Math.round(value)}`;
}

function RadialGauge({
  value,
  size = 150,
  stroke = 14,
  label,
  subtitle,
  gradientId,
  gradientFrom,
  gradientTo,
  glow,
}) {
  const safeValue = clampPercent(value);
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (safeValue / 100) * circumference;

  return (
    <div className="flex flex-col items-center text-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90 overflow-visible">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={gradientFrom} />
              <stop offset="100%" stopColor={gradientTo} />
            </linearGradient>
          </defs>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(148, 163, 184, 0.18)"
            strokeWidth={stroke}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={`url(#${gradientId})`}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{
              filter: `drop-shadow(0 10px 18px ${glow})`,
              transition: "stroke-dashoffset 240ms ease",
            }}
          />
        </svg>

        <div className="absolute inset-[18%] flex items-center justify-center rounded-full border border-white/70 bg-white/72 shadow-[inset_0_1px_0_rgba(255,255,255,0.8),0_18px_36px_rgba(15,23,42,0.08)] backdrop-blur">
          <div>
            <div className="text-3xl font-semibold tracking-tight text-slate-950">{formatPercent(safeValue)}</div>
            <div className="mt-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">{label}</div>
          </div>
        </div>
      </div>

      {subtitle ? <p className="mt-3 max-w-[15rem] text-sm leading-6 text-slate-600">{subtitle}</p> : null}
    </div>
  );
}

function SegmentRail({ segments }) {
  return (
    <div className="space-y-4">
      <div className="overflow-hidden rounded-full border border-white/75 bg-white/70 p-1 shadow-[0_18px_34px_rgba(15,23,42,0.05)]">
        <div className="flex h-5 overflow-hidden rounded-full">
          {segments.map((segment) => (
            <div key={segment.label} style={{ width: `${segment.percent}%`, background: segment.color }} />
          ))}
        </div>
      </div>

      <div className="grid gap-3">
        {segments.map((segment) => (
          <div
            key={segment.label}
            className="flex items-center justify-between rounded-[1.1rem] border border-white/75 bg-white/70 px-4 py-3 shadow-[0_12px_28px_rgba(15,23,42,0.05)]"
          >
            <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ background: segment.color }} aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-slate-950">{segment.label}</p>
                <p className="text-xs text-slate-500">{segment.caption}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-semibold tracking-tight text-slate-950">{segment.value}</p>
              <p className="text-xs text-slate-500">{formatPercent(segment.percent)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatChip({ label, value, accent }) {
  return (
    <div
      className="rounded-[1.2rem] border border-white/75 px-4 py-4 shadow-[0_14px_26px_rgba(15,23,42,0.05)]"
      style={{ background: accent }}
    >
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
    </div>
  );
}

function ChartCard({ eyebrow, title, description, className = "", children }) {
  return (
    <article className={`rounded-[1.5rem] border p-5 sm:p-6 ${className}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">{eyebrow}</p>
      <h3 className="mt-2 text-xl font-semibold text-slate-950">{title}</h3>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">{description}</p>
      <div className="mt-5">{children}</div>
    </article>
  );
}

export default function PortfolioCharts({ dashboard, review }) {
  const totals = review?.totals ?? {};
  const total = totals.total ?? dashboard.total_skus_analyzed;
  const actions = dashboard.recommended_price_changes;
  const increaseCount = totals.increase ?? 0;
  const decreaseCount = totals.decrease ?? Math.max(actions - increaseCount, 0);
  const holdCount = totals.hold ?? Math.max(total - actions, 0);
  const flaggedCount = dashboard.flagged_skus.length;
  const actionRate = total > 0 ? (actions / total) * 100 : 0;
  const overpriced = dashboard.overpriced_percentage;
  const averageMargin = dashboard.average_margin;
  const kviCompliance = dashboard.kvi_compliance_score;

  const segments = [
    {
      label: "Increase",
      value: formatCount(increaseCount),
      percent: total > 0 ? (increaseCount / total) * 100 : 0,
      caption: "recover margin selectively",
      color: "linear-gradient(135deg, #00a99d 0%, #7ac943 100%)",
    },
    {
      label: "Decrease",
      value: formatCount(decreaseCount),
      percent: total > 0 ? (decreaseCount / total) * 100 : 0,
      caption: "close market gaps",
      color: "linear-gradient(135deg, #ff931e 0%, #ff7bac 100%)",
    },
    {
      label: "Hold",
      value: formatCount(holdCount),
      percent: total > 0 ? (holdCount / total) * 100 : 0,
      caption: "leave stable pricing in place",
      color: "linear-gradient(135deg, #bdccd4 0%, #89a4b6 100%)",
    },
  ];

  return (
    <div className="grid gap-4 xl:grid-cols-[1.35fr_0.95fr]">
      <ChartCard
        eyebrow="Portfolio pulse"
        title="A cleaner read on pricing pressure"
        description="Two radial gauges make the top-line story easier to scan: how much of the assortment needs action, and how much is still above the market."
        className="theme-card-blue relative overflow-hidden shadow-[0_20px_40px_rgba(15,23,42,0.06)]"
      >
        <div className="pointer-events-none absolute right-[-2.5rem] top-[-2rem] h-32 w-32 rounded-full bg-white/30 blur-2xl" />
        <div className="grid gap-5 lg:grid-cols-[1fr_auto_1fr] lg:items-center">
          <RadialGauge
            value={actionRate}
            label="Action rate"
            subtitle={`${actions} of ${total} SKUs currently need a change recommendation.`}
            gradientId="action-rate-gauge"
            gradientFrom="#0071bc"
            gradientTo="#00a99d"
            glow="rgba(0,113,188,0.24)"
          />

          <div className="mx-auto grid w-full max-w-[13rem] gap-3">
            <StatChip
              label="SKUs analyzed"
              value={formatCount(total)}
              accent="linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,255,255,0.66))"
            />
            <StatChip
              label="Flagged now"
              value={formatCount(flaggedCount)}
              accent="linear-gradient(180deg, rgba(255,147,30,0.14), rgba(255,255,255,0.78))"
            />
          </div>

          <RadialGauge
            value={overpriced}
            label="Over market"
            subtitle="This is the share of SKUs currently sitting above the market reference."
            gradientId="overpriced-gauge"
            gradientFrom="#ff931e"
            gradientTo="#ff1d25"
            glow="rgba(255,123,172,0.24)"
          />
        </div>
      </ChartCard>

      <ChartCard
        eyebrow="Recommendation split"
        title="What kind of action is being recommended"
        description="A segmented rail gives users a quick feel for whether the queue is mostly corrective, margin-led, or steady."
        className="theme-card-neutral shadow-[0_20px_40px_rgba(15,23,42,0.06)]"
      >
        <SegmentRail segments={segments} />
      </ChartCard>

      <ChartCard
        eyebrow="Health signals"
        title="Margin and KVI discipline"
        description="These two gauges work well side by side because they answer different questions: profitability and price trust."
        className="theme-card-green shadow-[0_20px_40px_rgba(15,23,42,0.06)]"
      >
        <div className="grid gap-6 sm:grid-cols-2">
          <RadialGauge
            value={averageMargin}
            size={138}
            stroke={12}
            label="Average margin"
            subtitle="Healthy margin headroom across the current portfolio."
            gradientId="margin-gauge"
            gradientFrom="#7ac943"
            gradientTo="#00a99d"
            glow="rgba(122,201,67,0.22)"
          />
          <RadialGauge
            value={kviCompliance}
            size={138}
            stroke={12}
            label="KVI compliance"
            subtitle="How tightly key value items are staying near market."
            gradientId="kvi-gauge"
            gradientFrom="#ff7bac"
            gradientTo="#ff1d25"
            glow="rgba(255,29,37,0.18)"
          />
        </div>
      </ChartCard>

      <ChartCard
        eyebrow="Watchlist focus"
        title="Immediate review load"
        description="A compact callout keeps the urgent queue visible without repeating the old KPI card treatment."
        className="theme-card-amber shadow-[0_20px_40px_rgba(15,23,42,0.06)]"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-[1.35rem] border border-white/75 bg-white/72 p-5 shadow-[0_16px_30px_rgba(15,23,42,0.05)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Recommended changes</p>
            <p className="mt-3 text-5xl font-semibold tracking-tight text-slate-950">{formatCount(actions)}</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              SKUs are currently queued for intervention across the portfolio.
            </p>
          </div>

          <div className="rounded-[1.35rem] border border-white/75 bg-white/72 p-5 shadow-[0_16px_30px_rgba(15,23,42,0.05)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Sidebar watchlist</p>
            <p className="mt-3 text-5xl font-semibold tracking-tight text-slate-950">{formatCount(flaggedCount)}</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              priority SKUs are surfaced for immediate review and handoff.
            </p>
          </div>
        </div>
      </ChartCard>
    </div>
  );
}
