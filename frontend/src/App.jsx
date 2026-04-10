import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import SKUdetails from "./pages/SKUdetails";

const navItems = [
  { to: "/", label: "Overview", end: true },
  { to: "/skus", label: "SKU Queue" },
];

export default function App() {
  return (
    <div className="app-shell min-h-screen text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[110rem] flex-col px-4 py-4 sm:px-6 lg:px-8">
        <header className="app-header">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-3">
                <span className="app-eyebrow">VAI Pricing Agent</span>
                <span className="text-[11px] font-medium uppercase tracking-[0.22em] text-slate-500">
                  Decision workspace
                </span>
              </div>
              <h1 className="section-title mt-3 text-3xl text-slate-950 sm:text-4xl">
                Pricing operations, portfolio review, and SKU decisions in one tighter workflow.
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
                Track the portfolio, review agent guidance, and move quickly from signal to SKU-level action.
              </p>
            </div>

            <div className="flex flex-col gap-3 xl:min-w-[31rem] xl:items-end">
              <nav className="flex flex-wrap gap-2">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) =>
                      isActive ? "nav-pill nav-pill-active" : "nav-pill"
                    }
                  >
                    {item.label}
                  </NavLink>
                ))}
              </nav>

              <div className="grid gap-2 sm:grid-cols-3 xl:min-w-[31rem]">
                <HeaderStat label="Mode" value="Portfolio + SKU" />
                <HeaderStat label="Focus" value="Review and execute" />
                <HeaderStat label="Users" value="Pricing teams" />
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/skus" element={<Dashboard tableOnly />} />
            <Route path="/skus/:skuId" element={<SKUdetails />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function HeaderStat({ label, value }) {
  return (
    <div className="theme-card-neutral rounded-xl border px-3 py-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-1.5 text-sm font-semibold text-slate-900">{value}</p>
    </div>
  );
}
