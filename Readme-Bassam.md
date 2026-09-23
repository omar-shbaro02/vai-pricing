
## 2026-09-23 ? VAI Frontend Color Palette Update.

### Scope and starting state

Approved palette: rose `#B7355F`, dark gray `#5B5B5B`, black `#000000`, white `#FFFFFF`.

Task-modified files (complete list): `frontend/src/styles.css` and `Readme-Bassam.md`.

Before editing, `git status --short` showed:

```text
 M package-lock.json
?? Readme-Bassam.md
```

The existing README was empty (0 bytes); this section was appended without deleting existing content. The root lockfile already had colleague changes and was left byte-for-byte unchanged. The CSS was initially clean. SHA-256 snapshots of all 332 tracked and non-ignored untracked files, the initial CSS and README bytes, and the initial Git status were saved outside the repository at `C:/Users/bassa/AppData/Local/Temp/vai-palette-m4k3fvig`. Ignored dependency, virtualenv, and local data files are outside that hash inventory; no commands intentionally edited those files. No dependencies were installed or updated.

### Inspection and implementation decisions

- Installed Tailwind is **4.2.1**, read from `frontend/node_modules/tailwindcss/package.json`; `frontend/package.json` requests `^4.1.12`. React/Vite versions were not used to infer Tailwind's version.
- `frontend/src/main.jsx:5` imports the only frontend stylesheet, `frontend/src/styles.css`. Its first line imports Tailwind. The installed Tailwind stylesheet orders `theme`, `base`, `components`, then `utilities`. Existing custom CSS follows the import and is unlayered, so normal custom declarations beat normal layered utility declarations. The PostCSS configuration uses `@tailwindcss/postcss`. The legacy JavaScript Tailwind configuration has an empty extended theme; no configuration or import order was changed.
- Updated existing root tokens; preserved their names. Replaced gradients, translucent surfaces, grid paint, glows, soft shadows and backdrop filters with opaque approved paint or `none`. Original dimensions, spacing, typography, positioning, breakpoints, border widths/styles and transition declarations remain unchanged.
- Read all frontend JSX components and routes (`/`, `/skus`, `/skus/:skuId`) and audited each color utility use. Replaced the old global `!important` utility overrides with explicit `.app-shell`-scoped selectors for the exact existing classes. Legacy colors in class-name selectors are identifiers, not new paint declarations. Contextual rules handle formerly dark panels, action roles, selected cards, inputs, disabled controls and chat messages.
- Primary actions and active navigation are rose/white and black/white on hover. Secondary actions are white/rose and rose/white on hover; an opaque inset rose line supplies their border without changing dimensions. Focus outlines are rose, including the visible labels of hidden filter checkboxes. Errors/warnings retain their explanatory text. Positive deltas retain signs and labels and use black; negative/error deltas use rose. Assistant chat text is black; user bubbles are rose/white. There are currently no sender-label elements; a narrowly scoped rule protects the existing supporting-text classes if used within a user bubble. Loading text uses the supporting gray role, and disabled controls use gray/white with full opacity and unchanged disabled attributes/cursors.
- Gauge strokes use their existing stable `stroke="url(#...-gauge)"` identifiers: action rate/margin use rose, over-market/KVI use black, tracks use gray. All metric labels, geometry, dash offsets, and movement transitions are preserved. Two explicitly targeted `!important` declarations are necessary to override existing inline paint: one removes only the four gauge filters, the other makes the two StatChip callout backgrounds white using their unique existing class combination. There are no blanket important rules or indiscriminate SVG fill/stroke overrides.

### Verification and actual results

- **PASS:** PostCSS parses the final CSS (161 declarations). Every literal paint color in declarations belongs to the four-color palette; no gradient or RGB/alpha paint declarations remain in this stylesheet. Old colors inside selector strings match restricted JSX identifiers only.
- **PASS:** Parsed before/after comparison finds identical original non-paint declarations and identical border widths/styles. This checks source layout preservation, not browser rendering.
- **PASS:** Existing Vite production build completed in memory with `build({root: 'frontend', build: {write: false}})`, producing three output objects; no generated build files were written. An initial source-check harness incorrectly classified `background-color` as non-paint, reported a mismatch, and was corrected before the successful final check; no layout changes were needed.
- **PASS:** `git diff --check` reports no whitespace errors.
- **PASS:** SHA-256 comparison after implementation finds only the permitted CSS and README changed from the starting snapshot. All 330 other inventoried files, including backend, JS/JSX, configuration, manifests, assets and the pre-modified root lockfile, are byte-identical. The initial README contents remain an exact prefix. No restricted source files were edited by this task.
- **PASS (calculated, not browser-measured):** white/rose contrast is **5.69:1**, white/gray is **6.79:1**, black/white is **21:1**. These exceed 4.5:1 for the intended text pairs. Chart series remain separately labeled; the blocked rail retains its original matching legend colors.
- **LIMITATION:** The Browser skill was read and its runtime initialized, but browser selection returned `No browser is available`; the prescribed discovery returned `[]`. Desktop/mobile screenshots, computed-style checks, keyboard interaction and rendered route/state checks could not be performed. No claims of visual or functional browser testing are made.
- No backend endpoints were called, no real-data mutations were performed, and backend functionality was not tested. Simulation, chat and agent-run actions were inspected in source only. No extra test files, dependency installs, migrations or configuration changes were made.
- Source inventory contains no standalone dialogs, notifications, dropdown components, canvas charts, axes or tooltips; no such UI was invented. Forms, dashboard cards, SKU cards/details, error/empty/loading states, simulation results and chat states were reviewed in existing source.

### Remaining unapproved colors and scope blockers

The only identified remaining rendered old palette is the **recommendation split rail and its legend dots** in `frontend/src/components/PortfolioCharts.jsx`:

| Exact source location | Remaining value | Consumer / why blocked |
| --- | --- | --- |
| `frontend/src/components/PortfolioCharts.jsx:154` | `linear-gradient(135deg, #00a99d 0%, #7ac943 100%)` | Increase rail segment and matching legend dot |
| `frontend/src/components/PortfolioCharts.jsx:161` | `linear-gradient(135deg, #ff931e 0%, #ff7bac 100%)` | Decrease rail segment and matching legend dot |
| `frontend/src/components/PortfolioCharts.jsx:168` | `linear-gradient(135deg, #bdccd4 0%, #89a4b6 100%)` | Hold rail segment and matching legend dot |

`SegmentRail` applies each value as inline `background` on line **84** (segment) and line **97** (legend dot). Those elements have no stable series-specific class, ID or data attribute; React keys are not DOM attributes. A shared CSS override would collapse the series distinction. Mapping via DOM position or serialized inline-style text would be fragile. Adding semantic selectors or changing the values requires prohibited JSX edits. These six elements therefore remain unchanged, preserving the original rail/legend correspondence and all labels.

Other old color literals remain in restricted JSX source but have CSS overrides: gauge props at lines 187?189, 210?212, 240?242 and 251?253; SVG track stroke at line 44; inline glow consumer at line 57; gradient stops at lines 35?36 (their gradients are no longer referenced by the styled gauge strokes); StatChip inline background at line 119 and accent values at lines 196 and 201. Those original literals were intentionally not deleted. Tailwind's installed defaults and generated in-memory utility definitions also retain old colors; dependencies/configuration/generated files are outside scope, and scoped CSS overrides the audited rendered utility uses.

The following inventory records every frontend JSX line containing an old explicit hex/RGB color, including arbitrary utility identifiers. Unless covered by the rail blocker above, these are preserved source values superseded by scoped CSS, not intentionally remaining rendered colors:

| File and line | Preserved source |
| --- | --- |
| `frontend/src/components/AgentReviewPanel.jsx:4` | `if (priority === "high") return "bg-white/12 text-[#ffd3e3] ring-1 ring-inset ring-[#ff7bac]/30";` |
| `frontend/src/components/AgentReviewPanel.jsx:5` | `if (priority === "medium") return "bg-white/12 text-[#ffe0b5] ring-1 ring-inset ring-[#ff931e]/30";` |
| `frontend/src/components/AgentReviewPanel.jsx:6` | `return "bg-white/12 text-[#d9f6c2] ring-1 ring-inset ring-[#7ac943]/30";` |
| `frontend/src/components/AgentReviewPanel.jsx:10` | `if (recommendation === "increase") return "text-[#a9e0ff]";` |
| `frontend/src/components/AgentReviewPanel.jsx:11` | `if (recommendation === "decrease") return "text-[#ffd49d]";` |
| `frontend/src/components/AgentReviewPanel.jsx:12` | `return "text-[#d8e5ef]";` |
| `frontend/src/components/AgentReviewPanel.jsx:76` | `? "border-[#3fa9f5]/45 bg-[#3fa9f5]/16"` |
| `frontend/src/components/KPIcard.jsx:11` | `<article className={`rounded-[1.1rem] border p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] ${toneMap[tone]}`}>` |
| `frontend/src/components/PortfolioCharts.jsx:44` | `stroke="rgba(148, 163, 184, 0.18)"` |
| `frontend/src/components/PortfolioCharts.jsx:64` | `<div className="absolute inset-[18%] flex items-center justify-center rounded-full border border-white/70 bg-white/72 shadow-[inset_0_1px_0_rgba(255,255,255,0.8),0_18px_36px_rgba(15,23,42,0.08)] backdrop-blur">` |
| `frontend/src/components/PortfolioCharts.jsx:80` | `<div className="overflow-hidden rounded-full border border-white/75 bg-white/70 p-1 shadow-[0_18px_34px_rgba(15,23,42,0.05)]">` |
| `frontend/src/components/PortfolioCharts.jsx:92` | `className="flex items-center justify-between rounded-[1.1rem] border border-white/75 bg-white/70 px-4 py-3 shadow-[0_12px_28px_rgba(15,23,42,0.05)]"` |
| `frontend/src/components/PortfolioCharts.jsx:115` | `className="rounded-[1.2rem] border border-white/75 px-4 py-4 shadow-[0_14px_26px_rgba(15,23,42,0.05)]"` |
| `frontend/src/components/PortfolioCharts.jsx:154` | `color: "linear-gradient(135deg, #00a99d 0%, #7ac943 100%)",` |
| `frontend/src/components/PortfolioCharts.jsx:161` | `color: "linear-gradient(135deg, #ff931e 0%, #ff7bac 100%)",` |
| `frontend/src/components/PortfolioCharts.jsx:168` | `color: "linear-gradient(135deg, #bdccd4 0%, #89a4b6 100%)",` |
| `frontend/src/components/PortfolioCharts.jsx:178` | `className="theme-card-blue relative overflow-hidden shadow-[0_20px_40px_rgba(15,23,42,0.06)]"` |
| `frontend/src/components/PortfolioCharts.jsx:187` | `gradientFrom="#0071bc"` |
| `frontend/src/components/PortfolioCharts.jsx:188` | `gradientTo="#00a99d"` |
| `frontend/src/components/PortfolioCharts.jsx:189` | `glow="rgba(0,113,188,0.24)"` |
| `frontend/src/components/PortfolioCharts.jsx:196` | `accent="linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,255,255,0.66))"` |
| `frontend/src/components/PortfolioCharts.jsx:201` | `accent="linear-gradient(180deg, rgba(255,147,30,0.14), rgba(255,255,255,0.78))"` |
| `frontend/src/components/PortfolioCharts.jsx:210` | `gradientFrom="#ff931e"` |
| `frontend/src/components/PortfolioCharts.jsx:211` | `gradientTo="#ff1d25"` |
| `frontend/src/components/PortfolioCharts.jsx:212` | `glow="rgba(255,123,172,0.24)"` |
| `frontend/src/components/PortfolioCharts.jsx:221` | `className="theme-card-neutral shadow-[0_20px_40px_rgba(15,23,42,0.06)]"` |
| `frontend/src/components/PortfolioCharts.jsx:230` | `className="theme-card-green shadow-[0_20px_40px_rgba(15,23,42,0.06)]"` |
| `frontend/src/components/PortfolioCharts.jsx:240` | `gradientFrom="#7ac943"` |
| `frontend/src/components/PortfolioCharts.jsx:241` | `gradientTo="#00a99d"` |
| `frontend/src/components/PortfolioCharts.jsx:242` | `glow="rgba(122,201,67,0.22)"` |
| `frontend/src/components/PortfolioCharts.jsx:251` | `gradientFrom="#ff7bac"` |
| `frontend/src/components/PortfolioCharts.jsx:252` | `gradientTo="#ff1d25"` |
| `frontend/src/components/PortfolioCharts.jsx:253` | `glow="rgba(255,29,37,0.18)"` |
| `frontend/src/components/PortfolioCharts.jsx:262` | `className="theme-card-amber shadow-[0_20px_40px_rgba(15,23,42,0.06)]"` |
| `frontend/src/components/PortfolioCharts.jsx:265` | `<div className="rounded-[1.35rem] border border-white/75 bg-white/72 p-5 shadow-[0_16px_30px_rgba(15,23,42,0.05)]">` |
| `frontend/src/components/PortfolioCharts.jsx:273` | `<div className="rounded-[1.35rem] border border-white/75 bg-white/72 p-5 shadow-[0_16px_30px_rgba(15,23,42,0.05)]">` |
| `frontend/src/components/SimulationPanel.jsx:5` | `if (recommendation === "increase") return "bg-[#3fa9f5]/14 text-[#0c6aa9] border-[#3fa9f5]/24";` |
| `frontend/src/components/SimulationPanel.jsx:6` | `if (recommendation === "decrease") return "bg-[#ff931e]/14 text-[#9c5a00] border-[#ff931e]/24";` |
| `frontend/src/components/SimulationPanel.jsx:7` | `return "bg-[#bdccd4]/20 text-[#456173] border-[#bdccd4]/32";` |
| `frontend/src/components/SKUChatbot.jsx:92` | `? "ml-auto max-w-[34rem] bg-[#16324f] text-white"` |
| `frontend/src/components/SKUChatbot.jsx:115` | `className="w-full rounded-[1rem] border border-slate-300 bg-white/85 px-4 py-3 text-sm outline-none transition focus:border-[#3fa9f5] focus:ring-4 focus:ring-[#3fa9f5]/15"` |
| `frontend/src/components/SKUtable.jsx:6` | `chip: "bg-[#ff7bac]/20 text-[#a9285d]",` |
| `frontend/src/components/SKUtable.jsx:13` | `chip: "bg-[#ff931e]/18 text-[#a85c00]",` |
| `frontend/src/components/SKUtable.jsx:20` | `chip: "bg-[#3fa9f5]/16 text-[#0d69a9]",` |
| `frontend/src/components/SKUtable.jsx:26` | `chip: "bg-[#bdccd4]/25 text-[#466072]",` |
| `frontend/src/components/SKUtable.jsx:43` | `className={`rounded-[1.2rem] border p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] transition ${` |
| `frontend/src/components/SKUtable.jsx:62` | `selected ? "bg-[#3fa9f5]/18 text-[#d7f1ff]" : "bg-[#3fa9f5]/12 text-[#0d69a9]"` |
| `frontend/src/pages/SKUdetails.jsx:17` | `<div className={`rounded-[1.1rem] border p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] ${toneMap[tone]}`}>` |

### Final CSS block index and reasons

The table identifies final line ranges for every changed or added block. The exact diff below supplies all previous/new declarations and documents every deletion, replacement and addition. Deleted global utility blocks have no final lines: they occupied original lines 219?323 and are replaced by the scoped blocks beginning at final line 208. Diff hunk headers give precise original/final coordinates, including comments and blank-line additions.

| Final lines in `frontend/src/styles.css` | Selector / block | Reason |
| --- | --- | --- |
| 3?24 | `:root` | Map existing brand/text/border/surface tokens to approved colors; disable soft shadow tokens. |
| 26?29 | `html` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 31?39 | `body` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 52?55 | `a` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 61?64 | `::selection` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 70?78 | `.app-shell::before` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 80?88 | `.app-header` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 90?95 | `.glass-panel` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 103?115 | `.app-eyebrow` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 117?126 | `.nav-pill` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 128?132 | `.nav-pill:hover` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 134?139 | `.nav-pill-active` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 141?144 | `.subtle-grid` | Remove tinted grid paint or apply readable chat role colors. |
| 146?150 | `.theme-dark-panel` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 152?156 | `.theme-pdf-blue-panel` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 158?161 | `.theme-dark-soft` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 163?167 | `.theme-button-primary` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 169?173 | `.theme-button-primary:hover` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 175?178 | `.theme-link-button` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 180?183 | `.theme-card-blue` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 185?188 | `.theme-card-green` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 190?193 | `.theme-card-amber` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 195?198 | `.theme-card-red` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 200?203 | `.theme-card-neutral` | Replace old palette/tint/gradient paint with approved flat surfaces, text or borders; remove soft effects where present. |
| 208?210 | `.app-shell [class~="backdrop-blur"]` | Remove audited soft shadows or blur/glow utility effects. |
| 212?214 | `.app-shell [class~="bg-[#16324f]"]` | Replace audited translucent/arbitrary backgrounds with white, except rose user chat bubbles. |
| 216?240 | `.app-shell [class~="bg-[#3fa9f5]/12"], .app-shell [class~="bg-[#3fa9f5]/14"], .app-shell [class~="bg-[#3fa9f5]/16"], .app-shell [class~="bg-[#3fa9f5]/18"], .app-shell [class~="bg-[#bdccd4]/20"], .app-shell [class~="bg-[#bdccd4]/25"], .app-shell [class~="bg-[#ff7bac]/20"], .app-shell [class~="bg-[#ff931e]/14"], .app-shell [class~="bg-[#ff931e]/18"], .app-shell [class~="bg-amber-50"], .app-shell [class~="bg-black/10"], .app-shell [class~="bg-rose-50"], .app-shell [class~="bg-slate-50"], .app-shell [class~="bg-white"], .app-shell [class~="bg-white/10"], .app-shell [class~="bg-white/12"], .app-shell [class~="bg-white/30"], .app-shell [class~="bg-white/5"], .app-shell [class~="bg-white/6"], .app-shell [class~="bg-white/70"], .app-shell [class~="bg-white/72"], .app-shell [class~="bg-white/80"], .app-shell [class~="bg-white/85"]` | Replace audited translucent/arbitrary backgrounds with white, except rose user chat bubbles. |
| 242?244 | `.app-shell [class~="blur-2xl"]` | Remove audited soft shadows or blur/glow utility effects. |
| 246?253 | `.app-shell [class~="border-[#3fa9f5]/24"], .app-shell [class~="border-[#3fa9f5]/45"], .app-shell [class~="border-[#bdccd4]/32"], .app-shell [class~="border-[#ff931e]/24"], .app-shell [class~="border-amber-200"], .app-shell [class~="border-rose-200"]` | Map audited borders/rings to gray or rose. |
| 255?264 | `.app-shell [class~="border-slate-200"], .app-shell [class~="border-slate-300"], .app-shell [class~="border-white/10"], .app-shell [class~="border-white/12"], .app-shell [class~="border-white/20"], .app-shell [class~="border-white/70"], .app-shell [class~="border-white/75"], .app-shell [class~="border-white/8"]` | Map audited borders/rings to gray or rose. |
| 266?270 | `.app-shell [class~="ring-[#7ac943]/30"], .app-shell [class~="ring-[#ff7bac]/30"], .app-shell [class~="ring-[#ff931e]/30"]` | Map audited borders/rings to gray or rose. |
| 272?280 | `.app-shell [class~="shadow-[0_12px_28px_rgba(15,23,42,0.05)]"], .app-shell [class~="shadow-[0_14px_26px_rgba(15,23,42,0.05)]"], .app-shell [class~="shadow-[0_16px_30px_rgba(15,23,42,0.05)]"], .app-shell [class~="shadow-[0_18px_34px_rgba(15,23,42,0.05)]"], .app-shell [class~="shadow-[0_20px_40px_rgba(15,23,42,0.06)]"], .app-shell [class~="shadow-[0_8px_20px_rgba(15,23,42,0.04)]"], .app-shell [class~="shadow-[inset_0_1px_0_rgba(255,255,255,0.8),0_18px_36px_rgba(15,23,42,0.08)]"]` | Remove audited soft shadows or blur/glow utility effects. |
| 282?297 | `.app-shell [class~="text-[#0c6aa9]"], .app-shell [class~="text-[#0d69a9]"], .app-shell [class~="text-[#9c5a00]"], .app-shell [class~="text-[#a85c00]"], .app-shell [class~="text-[#a9285d]"], .app-shell [class~="text-[#a9e0ff]"], .app-shell [class~="text-[#d7f1ff]"], .app-shell [class~="text-[#d9f6c2]"], .app-shell [class~="text-[#ffd3e3]"], .app-shell [class~="text-[#ffd49d]"], .app-shell [class~="text-[#ffe0b5]"], .app-shell [class~="text-amber-800"], .app-shell [class~="text-rose-700"], .app-shell [class~="text-rose-800"]` | Map audited text utilities to black values, gray supporting text or rose status/error text. |
| 299?309 | `.app-shell [class~="text-[#456173]"], .app-shell [class~="text-[#466072]"], .app-shell [class~="text-[#d8e5ef]"], .app-shell [class~="text-slate-200"], .app-shell [class~="text-slate-300"], .app-shell [class~="text-slate-400"], .app-shell [class~="text-slate-500"], .app-shell [class~="text-slate-600"], .app-shell [class~="text-slate-700"]` | Map audited text utilities to black values, gray supporting text or rose status/error text. |
| 311?315 | `.app-shell [class~="text-emerald-700"], .app-shell [class~="text-slate-900"], .app-shell [class~="text-slate-950"]` | Map audited text utilities to black values, gray supporting text or rose status/error text. |
| 318?321 | `.app-shell :is(.theme-dark-panel, .theme-pdf-blue-panel), .app-shell :is(.theme-dark-panel, .theme-pdf-blue-panel) .text-white:not(a):not(button)` | Restore black text on panels converted from dark to white. |
| 323?326 | `.app-shell article.theme-dark-panel, .app-shell button[class~="border-[#3fa9f5]/45"]` | Map audited borders/rings to gray or rose. |
| 329?336 | `.app-shell :is(button.theme-card-neutral, button.border-dashed, a.rounded-full, .theme-link-button), .app-shell label.cursor-pointer:not(.theme-button-primary), .app-shell button[class~="disabled:opacity-60"]` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 338?340 | `.app-shell a:not(.rounded-full):not(.nav-pill)` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 342?347 | `.app-shell :is(button.theme-card-neutral, button.border-dashed, a.rounded-full, .theme-link-button):hover, .app-shell label.cursor-pointer:not(.theme-button-primary):hover, .app-shell button[class~="disabled:opacity-60"]:hover` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 349?353 | `.app-shell .theme-button-primary, .app-shell .nav-pill-active` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 355?360 | `.app-shell .theme-button-primary:hover, .app-shell .nav-pill-active:hover` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 362?365 | `.app-shell article[class~="hover:border-sky-200"]:hover, .app-shell .theme-dark-soft button:hover` | Apply action/navigation/link, selected or hover colors while preserving dimensions and behavior. |
| 367?371 | `.app-shell :is(input, textarea, select)` | White control surfaces and black text with rose native accents. |
| 373?376 | `.app-shell :is(input, textarea)::placeholder` | Opaque gray placeholder text. |
| 378?381 | `.app-shell :is(input, textarea, select):focus` | Visible rose focus paint, including hidden-checkbox labels, without layout reflow. |
| 383?387 | `.app-shell :is(a, button, input, textarea, select):focus-visible, .app-shell label.cursor-pointer:has(input:focus-visible)` | Visible rose focus paint, including hidden-checkbox labels, without layout reflow. |
| 389?398 | `.app-shell button:disabled, .app-shell button:disabled:hover, .app-shell :is(input, textarea, select):disabled` | Opaque gray/white disabled treatment without changing disabled behavior. |
| 401?405 | `.app-shell .subtle-grid [class~="bg-[#16324f]"], .app-shell .subtle-grid [class~="bg-[#16324f]"] :is(.text-slate-500, .text-slate-700)` | Remove tinted grid paint or apply readable chat role colors. |
| 407?409 | `.app-shell .subtle-grid .whitespace-pre-wrap` | Remove tinted grid paint or apply readable chat role colors. |
| 412?415 | `.app-shell circle[stroke="url(#action-rate-gauge)"], .app-shell circle[stroke="url(#margin-gauge)"]` | Map identified gauge strokes/tracks or remove inline glow while preserving metric distinctions and geometry. |
| 417?420 | `.app-shell circle[stroke="url(#overpriced-gauge)"], .app-shell circle[stroke="url(#kvi-gauge)"]` | Map identified gauge strokes/tracks or remove inline glow while preserving metric distinctions and geometry. |
| 422?424 | `.app-shell svg:has(:is(#action-rate-gauge, #overpriced-gauge, #margin-gauge, #kvi-gauge)) circle[stroke="rgba(148, 163, 184, 0.18)"]` | Map identified gauge strokes/tracks or remove inline glow while preserving metric distinctions and geometry. |
| 427?429 | `.app-shell circle:is([stroke="url(#action-rate-gauge)"], [stroke="url(#overpriced-gauge)"], [stroke="url(#margin-gauge)"], [stroke="url(#kvi-gauge)"])` | Map identified gauge strokes/tracks or remove inline glow while preserving metric distinctions and geometry. |
| 432?434 | `.app-shell .theme-card-blue [class~="rounded-[1.2rem]"][class~="border-white/75"]` | Override only the two inline StatChip tinted backgrounds with opaque white. |

### Exact implementation diff

This diff is against the saved starting CSS, not against unrelated colleague changes.

```diff
--- frontend/src/styles.css (starting state)
+++ frontend/src/styles.css (final)
@@ -3,38 +3,35 @@
 :root {
   color-scheme: light;
   font-family: "Segoe UI Variable", "Trebuchet MS", "Segoe UI", sans-serif;
-  --brand-sky: #3fa9f5;
-  --brand-sky-deep: #0071bc;
-  --brand-mint: #00a99d;
-  --brand-leaf: #7ac943;
-  --brand-orange: #ff931e;
-  --brand-rose: #ff7bac;
-  --brand-red: #ff1d25;
-  --brand-mist: #bdccd4;
-  --ink-900: #16324f;
-  --ink-700: #2b4d6b;
-  --text-main: #17324d;
-  --text-muted: #557086;
-  --border-soft: rgba(22, 50, 79, 0.12);
-  --panel: rgba(255, 255, 255, 0.9);
-  --panel-strong: rgba(255, 255, 255, 0.96);
-  --panel-muted: rgba(189, 204, 212, 0.12);
-  --shadow-soft: 0 16px 36px rgba(22, 50, 79, 0.08);
-  --shadow-strong: 0 24px 48px rgba(22, 50, 79, 0.14);
+  --brand-sky: #B7355F;
+  --brand-sky-deep: #B7355F;
+  --brand-mint: #B7355F;
+  --brand-leaf: #B7355F;
+  --brand-orange: #B7355F;
+  --brand-rose: #B7355F;
+  --brand-red: #B7355F;
+  --brand-mist: #5B5B5B;
+  --ink-900: #000000;
+  --ink-700: #5B5B5B;
+  --text-main: #000000;
+  --text-muted: #5B5B5B;
+  --border-soft: #5B5B5B;
+  --panel: #FFFFFF;
+  --panel-strong: #FFFFFF;
+  --panel-muted: #FFFFFF;
+  --shadow-soft: none;
+  --shadow-strong: none;
 }
 
 html {
   min-height: 100%;
-  background:
-    radial-gradient(circle at top left, rgba(63, 169, 245, 0.2), transparent 32%),
-    radial-gradient(circle at top right, rgba(122, 201, 67, 0.16), transparent 30%),
-    linear-gradient(180deg, #f7fbff 0%, #eef5f8 48%, #f9f3ea 100%);
+  background: #FFFFFF;
 }
 
 body {
   margin: 0;
   min-width: 320px;
-  background: transparent;
+  background: #FFFFFF;
   color: var(--text-main);
   font-family: inherit;
   text-rendering: optimizeLegibility;
@@ -53,7 +50,7 @@
 }
 
 a {
-  color: inherit;
+  color: #B7355F;
   text-decoration: none;
 }
 
@@ -62,8 +59,8 @@
 }
 
 ::selection {
-  background: rgba(63, 169, 245, 0.24);
-  color: #0e2235;
+  background: #B7355F;
+  color: #FFFFFF;
 }
 
 .app-shell {
@@ -75,32 +72,26 @@
   position: fixed;
   inset: 0;
   pointer-events: none;
-  background:
-    radial-gradient(circle at 12% 18%, rgba(255, 147, 30, 0.08), transparent 18%),
-    radial-gradient(circle at 88% 14%, rgba(255, 123, 172, 0.08), transparent 18%),
-    linear-gradient(90deg, rgba(189, 204, 212, 0.08) 1px, transparent 1px),
-    linear-gradient(rgba(189, 204, 212, 0.08) 1px, transparent 1px);
+  background: none;
   background-size: auto, auto, 22px 22px, 22px 22px;
-  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.9), transparent 88%);
+  mask-image: none;
 }
 
 .app-header {
   margin-bottom: 1.5rem;
-  border: 1px solid rgba(63, 169, 245, 0.18);
+  border: 1px solid #5B5B5B;
   border-radius: 1.75rem;
-  background:
-    linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.84)),
-    linear-gradient(135deg, rgba(63, 169, 245, 0.08), rgba(122, 201, 67, 0.06));
-  box-shadow: var(--shadow-soft);
+  background: #FFFFFF;
+  box-shadow: none;
   padding: 1.35rem 1.6rem;
-  backdrop-filter: blur(18px);
+  backdrop-filter: none;
 }
 
 .glass-panel {
   border: 1px solid var(--border-soft);
   background: var(--panel);
-  box-shadow: var(--shadow-soft);
-  backdrop-filter: blur(14px);
+  box-shadow: none;
+  backdrop-filter: none;
 }
 
 .section-title {
@@ -113,211 +104,331 @@
   display: inline-flex;
   align-items: center;
   border-radius: 999px;
-  border: 1px solid rgba(63, 169, 245, 0.24);
-  background: linear-gradient(135deg, rgba(63, 169, 245, 0.14), rgba(122, 201, 67, 0.12));
+  border: 1px solid #B7355F;
+  background: #FFFFFF;
   padding: 0.42rem 0.8rem;
   font-size: 11px;
   font-weight: 800;
   letter-spacing: 0.22em;
   text-transform: uppercase;
-  color: var(--ink-900);
+  color: #B7355F;
 }
 
 .nav-pill {
   border-radius: 999px;
-  border: 1px solid rgba(22, 50, 79, 0.12);
-  background: rgba(255, 255, 255, 0.76);
+  border: 1px solid #B7355F;
+  background: #FFFFFF;
   padding: 0.68rem 1.05rem;
   font-size: 0.875rem;
   font-weight: 700;
-  color: var(--ink-700);
+  color: #B7355F;
   transition: 160ms ease;
 }
 
 .nav-pill:hover {
-  border-color: rgba(63, 169, 245, 0.28);
-  background: rgba(63, 169, 245, 0.08);
+  border-color: #B7355F;
+  background: #B7355F;
+  color: #FFFFFF;
 }
 
 .nav-pill-active {
-  background: linear-gradient(135deg, var(--brand-sky-deep), var(--brand-mint));
-  border-color: transparent;
-  color: #fff;
-  box-shadow: 0 16px 30px rgba(0, 113, 188, 0.24);
+  background: #B7355F;
+  border-color: #B7355F;
+  color: #FFFFFF;
+  box-shadow: none;
 }
 
 .subtle-grid {
-  background-image:
-    linear-gradient(rgba(189, 204, 212, 0.18) 1px, transparent 1px),
-    linear-gradient(90deg, rgba(189, 204, 212, 0.18) 1px, transparent 1px);
+  background-image: none;
   background-size: 18px 18px;
 }
 
 .theme-dark-panel {
-  border: 1px solid rgba(63, 169, 245, 0.12);
-  background:
-    radial-gradient(circle at top right, rgba(63, 169, 245, 0.14), transparent 28%),
-    radial-gradient(circle at bottom left, rgba(122, 201, 67, 0.12), transparent 24%),
-    linear-gradient(180deg, #17324d 0%, #10263a 100%);
-  box-shadow: var(--shadow-strong);
+  border: 1px solid #5B5B5B;
+  background: #FFFFFF;
+  box-shadow: none;
 }
 
 .theme-pdf-blue-panel {
-  border: 1px solid rgba(63, 169, 245, 0.22);
-  background:
-    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 24%),
-    radial-gradient(circle at bottom left, rgba(0, 169, 157, 0.14), transparent 22%),
-    linear-gradient(180deg, #3fa9f5 0%, #0071bc 100%);
-  box-shadow: 0 24px 48px rgba(0, 113, 188, 0.22);
+  border: 1px solid #5B5B5B;
+  background: #FFFFFF;
+  box-shadow: none;
 }
 
 .theme-dark-soft {
-  border: 1px solid rgba(255, 255, 255, 0.12);
-  background: rgba(255, 255, 255, 0.08);
+  border: 1px solid #5B5B5B;
+  background: #FFFFFF;
 }
 
 .theme-button-primary {
-  background: linear-gradient(135deg, var(--brand-sky-deep), var(--brand-mint));
-  color: white;
-  box-shadow: 0 14px 24px rgba(0, 113, 188, 0.2);
+  background: #B7355F;
+  color: #FFFFFF;
+  box-shadow: none;
 }
 
 .theme-button-primary:hover {
-  filter: brightness(1.04);
+  background: #000000;
+  color: #FFFFFF;
+  filter: none;
 }
 
 .theme-link-button {
-  background: rgba(255, 255, 255, 0.88);
-  color: var(--ink-900);
+  background: #FFFFFF;
+  color: #B7355F;
 }
 
 .theme-card-blue {
-  border-color: rgba(63, 169, 245, 0.24);
-  background: linear-gradient(180deg, rgba(63, 169, 245, 0.12), rgba(255, 255, 255, 0.94));
+  border-color: #5B5B5B;
+  background: #FFFFFF;
 }
 
 .theme-card-green {
-  border-color: rgba(122, 201, 67, 0.24);
-  background: linear-gradient(180deg, rgba(122, 201, 67, 0.12), rgba(255, 255, 255, 0.94));
+  border-color: #5B5B5B;
+  background: #FFFFFF;
 }
 
 .theme-card-amber {
-  border-color: rgba(255, 147, 30, 0.26);
-  background: linear-gradient(180deg, rgba(255, 147, 30, 0.12), rgba(255, 255, 255, 0.94));
+  border-color: #B7355F;
+  background: #FFFFFF;
 }
 
 .theme-card-red {
-  border-color: rgba(255, 29, 37, 0.18);
-  background: linear-gradient(180deg, rgba(255, 123, 172, 0.12), rgba(255, 255, 255, 0.94));
+  border-color: #B7355F;
+  background: #FFFFFF;
 }
 
 .theme-card-neutral {
-  border-color: rgba(189, 204, 212, 0.4);
-  background: linear-gradient(180deg, rgba(189, 204, 212, 0.14), rgba(255, 255, 255, 0.94));
-}
-
-.text-slate-950 {
-  color: var(--ink-900) !important;
-}
-
-.text-slate-900 {
-  color: #244563 !important;
-}
-
-.text-slate-800 {
-  color: #355674 !important;
-}
-
-.text-slate-700 {
-  color: #49667d !important;
-}
-
-.text-slate-600 {
-  color: var(--text-muted) !important;
-}
-
-.text-slate-500 {
-  color: #69859a !important;
-}
-
-.text-slate-400 {
-  color: #9bb2c0 !important;
-}
-
-.text-slate-300 {
-  color: #d0dde6 !important;
-}
-
-.bg-slate-50 {
-  background-color: rgba(189, 204, 212, 0.14) !important;
-}
-
-.bg-slate-100 {
-  background-color: rgba(189, 204, 212, 0.22) !important;
-}
-
-.bg-slate-950 {
-  background-color: #16324f !important;
-}
-
-.border-slate-200 {
-  border-color: rgba(22, 50, 79, 0.12) !important;
-}
-
-.border-slate-300 {
-  border-color: rgba(22, 50, 79, 0.18) !important;
-}
-
-.bg-cyan-50\/70,
-.bg-cyan-50 {
-  background-color: rgba(63, 169, 245, 0.12) !important;
-}
-
-.border-cyan-200 {
-  border-color: rgba(63, 169, 245, 0.24) !important;
-}
-
-.text-cyan-800,
-.text-cyan-900 {
-  color: #0d69a9 !important;
-}
-
-.bg-emerald-50\/70,
-.bg-emerald-50 {
-  background-color: rgba(122, 201, 67, 0.12) !important;
-}
-
-.border-emerald-200 {
-  border-color: rgba(122, 201, 67, 0.24) !important;
-}
-
-.text-emerald-700 {
-  color: #4d8921 !important;
-}
-
-.bg-amber-50\/70,
-.bg-amber-50 {
-  background-color: rgba(255, 147, 30, 0.12) !important;
-}
-
-.border-amber-200 {
-  border-color: rgba(255, 147, 30, 0.24) !important;
-}
-
-.text-amber-800,
-.text-amber-900 {
-  color: #a45f05 !important;
-}
-
-.bg-rose-50 {
-  background-color: rgba(255, 123, 172, 0.12) !important;
-}
-
-.border-rose-200 {
-  border-color: rgba(255, 123, 172, 0.24) !important;
-}
-
-.text-rose-700,
-.text-rose-800 {
-  color: #b83a73 !important;
-}
+  border-color: #5B5B5B;
+  background: #FFFFFF;
+}
+
+/* Audited utility uses across all frontend components; unlayered rules
+   override Tailwind utilities without global utility changes or !important. */
+
+.app-shell [class~="backdrop-blur"] {
+  backdrop-filter: none;
+}
+
+.app-shell [class~="bg-[#16324f]"] {
+  background: #B7355F;
+}
+
+.app-shell [class~="bg-[#3fa9f5]/12"],
+.app-shell [class~="bg-[#3fa9f5]/14"],
+.app-shell [class~="bg-[#3fa9f5]/16"],
+.app-shell [class~="bg-[#3fa9f5]/18"],
+.app-shell [class~="bg-[#bdccd4]/20"],
+.app-shell [class~="bg-[#bdccd4]/25"],
+.app-shell [class~="bg-[#ff7bac]/20"],
+.app-shell [class~="bg-[#ff931e]/14"],
+.app-shell [class~="bg-[#ff931e]/18"],
+.app-shell [class~="bg-amber-50"],
+.app-shell [class~="bg-black/10"],
+.app-shell [class~="bg-rose-50"],
+.app-shell [class~="bg-slate-50"],
+.app-shell [class~="bg-white"],
+.app-shell [class~="bg-white/10"],
+.app-shell [class~="bg-white/12"],
+.app-shell [class~="bg-white/30"],
+.app-shell [class~="bg-white/5"],
+.app-shell [class~="bg-white/6"],
+.app-shell [class~="bg-white/70"],
+.app-shell [class~="bg-white/72"],
+.app-shell [class~="bg-white/80"],
+.app-shell [class~="bg-white/85"] {
+  background: #FFFFFF;
+}
+
+.app-shell [class~="blur-2xl"] {
+  filter: none;
+}
+
+.app-shell [class~="border-[#3fa9f5]/24"],
+.app-shell [class~="border-[#3fa9f5]/45"],
+.app-shell [class~="border-[#bdccd4]/32"],
+.app-shell [class~="border-[#ff931e]/24"],
+.app-shell [class~="border-amber-200"],
+.app-shell [class~="border-rose-200"] {
+  border-color: #B7355F;
+}
+
+.app-shell [class~="border-slate-200"],
+.app-shell [class~="border-slate-300"],
+.app-shell [class~="border-white/10"],
+.app-shell [class~="border-white/12"],
+.app-shell [class~="border-white/20"],
+.app-shell [class~="border-white/70"],
+.app-shell [class~="border-white/75"],
+.app-shell [class~="border-white/8"] {
+  border-color: #5B5B5B;
+}
+
+.app-shell [class~="ring-[#7ac943]/30"],
+.app-shell [class~="ring-[#ff7bac]/30"],
+.app-shell [class~="ring-[#ff931e]/30"] {
+  --tw-ring-color: #B7355F;
+}
+
+.app-shell [class~="shadow-[0_12px_28px_rgba(15,23,42,0.05)]"],
+.app-shell [class~="shadow-[0_14px_26px_rgba(15,23,42,0.05)]"],
+.app-shell [class~="shadow-[0_16px_30px_rgba(15,23,42,0.05)]"],
+.app-shell [class~="shadow-[0_18px_34px_rgba(15,23,42,0.05)]"],
+.app-shell [class~="shadow-[0_20px_40px_rgba(15,23,42,0.06)]"],
+.app-shell [class~="shadow-[0_8px_20px_rgba(15,23,42,0.04)]"],
+.app-shell [class~="shadow-[inset_0_1px_0_rgba(255,255,255,0.8),0_18px_36px_rgba(15,23,42,0.08)]"] {
+  box-shadow: none;
+}
+
+.app-shell [class~="text-[#0c6aa9]"],
+.app-shell [class~="text-[#0d69a9]"],
+.app-shell [class~="text-[#9c5a00]"],
+.app-shell [class~="text-[#a85c00]"],
+.app-shell [class~="text-[#a9285d]"],
+.app-shell [class~="text-[#a9e0ff]"],
+.app-shell [class~="text-[#d7f1ff]"],
+.app-shell [class~="text-[#d9f6c2]"],
+.app-shell [class~="text-[#ffd3e3]"],
+.app-shell [class~="text-[#ffd49d]"],
+.app-shell [class~="text-[#ffe0b5]"],
+.app-shell [class~="text-amber-800"],
+.app-shell [class~="text-rose-700"],
+.app-shell [class~="text-rose-800"] {
+  color: #B7355F;
+}
+
+.app-shell [class~="text-[#456173]"],
+.app-shell [class~="text-[#466072]"],
+.app-shell [class~="text-[#d8e5ef]"],
+.app-shell [class~="text-slate-200"],
+.app-shell [class~="text-slate-300"],
+.app-shell [class~="text-slate-400"],
+.app-shell [class~="text-slate-500"],
+.app-shell [class~="text-slate-600"],
+.app-shell [class~="text-slate-700"] {
+  color: #5B5B5B;
+}
+
+.app-shell [class~="text-emerald-700"],
+.app-shell [class~="text-slate-900"],
+.app-shell [class~="text-slate-950"] {
+  color: #000000;
+}
+
+/* White surfaces replace formerly dark panels; retain contextual text roles. */
+.app-shell :is(.theme-dark-panel, .theme-pdf-blue-panel),
+.app-shell :is(.theme-dark-panel, .theme-pdf-blue-panel) .text-white:not(a):not(button) {
+  color: #000000;
+}
+
+.app-shell article.theme-dark-panel,
+.app-shell button[class~="border-[#3fa9f5]/45"] {
+  border-color: #B7355F;
+}
+
+/* Action roles take precedence over the audited surface/text utilities. */
+.app-shell :is(button.theme-card-neutral, button.border-dashed, a.rounded-full, .theme-link-button),
+.app-shell label.cursor-pointer:not(.theme-button-primary),
+.app-shell button[class~="disabled:opacity-60"] {
+  background: #FFFFFF;
+  color: #B7355F;
+  border-color: #B7355F;
+  box-shadow: inset 0 0 0 1px #B7355F;
+}
+
+.app-shell a:not(.rounded-full):not(.nav-pill) {
+  color: #B7355F;
+}
+
+.app-shell :is(button.theme-card-neutral, button.border-dashed, a.rounded-full, .theme-link-button):hover,
+.app-shell label.cursor-pointer:not(.theme-button-primary):hover,
+.app-shell button[class~="disabled:opacity-60"]:hover {
+  background: #B7355F;
+  color: #FFFFFF;
+}
+
+.app-shell .theme-button-primary,
+.app-shell .nav-pill-active {
+  background: #B7355F;
+  color: #FFFFFF;
+}
+
+.app-shell .theme-button-primary:hover,
+.app-shell .nav-pill-active:hover {
+  background: #000000;
+  color: #FFFFFF;
+  filter: none;
+}
+
+.app-shell article[class~="hover:border-sky-200"]:hover,
+.app-shell .theme-dark-soft button:hover {
+  border-color: #B7355F;
+}
+
+.app-shell :is(input, textarea, select) {
+  background: #FFFFFF;
+  color: #000000;
+  accent-color: #B7355F;
+}
+
+.app-shell :is(input, textarea)::placeholder {
+  color: #5B5B5B;
+  opacity: 1;
+}
+
+.app-shell :is(input, textarea, select):focus {
+  border-color: #B7355F;
+  --tw-ring-color: #B7355F;
+}
+
+.app-shell :is(a, button, input, textarea, select):focus-visible,
+.app-shell label.cursor-pointer:has(input:focus-visible) {
+  outline: 2px solid #B7355F;
+  outline-offset: 2px;
+}
+
+.app-shell button:disabled,
+.app-shell button:disabled:hover,
+.app-shell :is(input, textarea, select):disabled {
+  background: #5B5B5B;
+  color: #FFFFFF;
+  border-color: #5B5B5B;
+  opacity: 1;
+  box-shadow: none;
+  filter: none;
+}
+
+/* Chat roles: the existing bubble classes are unique to SKUChatbot. */
+.app-shell .subtle-grid [class~="bg-[#16324f]"],
+.app-shell .subtle-grid [class~="bg-[#16324f]"] :is(.text-slate-500, .text-slate-700) {
+  background: #B7355F;
+  color: #FFFFFF;
+}
+
+.app-shell .subtle-grid .whitespace-pre-wrap {
+  color: #000000;
+}
+
+/* Stable gauge IDs preserve separately labeled metrics; no blanket SVG rules. */
+.app-shell circle[stroke="url(#action-rate-gauge)"],
+.app-shell circle[stroke="url(#margin-gauge)"] {
+  stroke: #B7355F;
+}
+
+.app-shell circle[stroke="url(#overpriced-gauge)"],
+.app-shell circle[stroke="url(#kvi-gauge)"] {
+  stroke: #000000;
+}
+
+.app-shell svg:has(:is(#action-rate-gauge, #overpriced-gauge, #margin-gauge, #kvi-gauge)) circle[stroke="rgba(148, 163, 184, 0.18)"] {
+  stroke: #5B5B5B;
+}
+
+/* Only these four inline glow declarations require a targeted priority override. */
+.app-shell circle:is([stroke="url(#action-rate-gauge)"], [stroke="url(#overpriced-gauge)"], [stroke="url(#margin-gauge)"], [stroke="url(#kvi-gauge)"]) {
+  filter: none !important;
+}
+
+/* Both StatChip callouts share this unique, existing class combination. */
+.app-shell .theme-card-blue [class~="rounded-[1.2rem]"][class~="border-white/75"] {
+  background: #FFFFFF !important;
+}
```
