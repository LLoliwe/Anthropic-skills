import React, { useMemo, useState } from "react";
import { Button } from "@heroui/react";

/*
 * This is a fully synthetic component/information architecture acceptance test.
 * Neither status nor tool connectivity describes a live Pryntor venture.
 */
const surfaces = [
  { id: "core", category: "Systems", name: "Mission Control", short: "A command surface for clear, accountable action.", action: "Task and evidence navigation", stage: "Baseline blocked", visual: "glyph-core", code: "01", note: "Existing Lovable pilot has outstanding tests. This demo does not alter it.", tokens: ["Decisions", "Evidence", "Ownership"] },
  { id: "lvl7", category: "Learning", name: "LVL7 Learning", short: "Make difficult ideas tangible without losing depth.", action: "Learner & teacher interfaces", stage: "Educational review", visual: "glyph-learning", code: "02", note: "Any actual course, curriculum or marking feature requires subject review.", tokens: ["Comprehension", "Feedback", "Accessibility"] },
  { id: "travel", category: "Services", name: "Tirisano Travel", short: "Business travel, considered from first enquiry to support.", action: "Corporate portal concept", stage: "Architecture only", visual: "glyph-travel", code: "03", note: "No booking connection, traveller records or real provider integration.", tokens: ["Trust", "Clarity", "Support"] },
  { id: "studio", category: "Culture", name: "Pryntor Studios", short: "Original creative work, directed with human taste.", action: "Production workspace concept", stage: "Editorial direction", visual: "glyph-studio", code: "04", note: "No licensed external images or third-party creative are included.", tokens: ["Authorship", "Rights", "Craft"] },
  { id: "research", category: "Research", name: "Robotics Lab", short: "Engineering evidence before attractive demonstrations.", action: "Simulation evidence console", stage: "Research only", visual: "glyph-research", code: "05", note: "No physical safety or robotics-performance claims. Synthetic entries only.", tokens: ["Units", "Provenance", "Failure states"] }
];

const categories = ["All", "Systems", "Learning", "Services", "Culture", "Research"];

export default function App() {
  const [category, setCategory] = useState("All");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("core");
  const [saved, setSaved] = useState([]);
  const visible = useMemo(() => surfaces.filter(s =>
    (category === "All" || s.category === category) &&
    [s.name, s.category, s.action, s.short].join(" ").toLowerCase().includes(query.trim().toLowerCase())
  ), [category, query]);
  const active = surfaces.find(s => s.id === selected) ?? surfaces[0];

  function reset() { setCategory("All"); setQuery(""); setSelected("core"); }
  function toggleSaved() {
    setSaved(prev => prev.includes(active.id) ? prev.filter(x => x !== active.id) : [...prev, active.id]);
  }

  return (
    <div className="application-shell">
      <header className="topbar">
        <a className="wordmark" href="#main" aria-label="Pryntor interface lab home">
          <span className="wordmark-icon" aria-hidden="true">P<span>.</span></span>
          <span className="wordmark-text">PRYNTOR<span> / LAB</span></span>
        </a>
        <div className="topbar-right">
          <span className="live-dot" aria-hidden="true" />
          <span className="topbar-caption">INTERNAL / SYNTHETIC</span>
          <span className="topbar-version">R0.1</span>
        </div>
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="page-title">
          <div className="hero-copy">
            <div className="eyebrow"><span className="eyebrow-line"/> INTERFACE SYSTEMS / 2026</div>
            <h1 id="page-title">One foundation.<br/><em>Distinct identities.</em></h1>
            <p className="hero-description">A small, working interface laboratory for the free HeroUI component system. Each brand keeps its own voice; the engineering underneath stays considered.</p>
            <div className="hero-bottom">
              <div className="hero-stat"><strong>05</strong><span>Illustrative<br/>product surfaces</span></div>
              <div className="hero-stat"><strong>01</strong><span>Shared, free<br/>component foundation</span></div>
            </div>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="orbit orbit-a" /><div className="orbit orbit-b" />
            <div className="monolith">
              <div className="monolith-inner">
                <span className="mono-upper">FORM / FUNCTION</span>
                <div className="mono-sculpture"><span /><span /><span /></div>
                <span className="mono-bottom">PRYNTOR — ORIGINAL SYSTEMS</span>
              </div>
            </div>
            <div className="vertical-label">STRUCTURE · CONTRAST · CONTROL</div>
          </div>
        </section>

        <section className="workspace" aria-labelledby="workspace-title">
          <div className="section-heading">
            <div>
              <div className="section-kicker">01 / DISCOVER</div>
              <h2 id="workspace-title">Surfaces in focus<span className="count">{String(visible.length).padStart(2, "0")}</span></h2>
            </div>
            <p>Explore design patterns without touching actual product code or real customer information.</p>
          </div>

          <div className="filterbar">
            <div className="category-filters" role="group" aria-label="Filter by portfolio category">
              {categories.map(c => (
                <Button key={c} className={"filter-button" + (category === c ? " selected" : "")} variant="tertiary" aria-pressed={category === c} onPress={() => setCategory(c)}>{c}</Button>
              ))}
            </div>
            <label className="search-wrap">
              <span className="search-icon" aria-hidden="true">⌕</span>
              <span className="sr-only">Search product surfaces</span>
              <input aria-label="Search product surfaces" type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search surfaces" />
            </label>
          </div>

          <div className="layout-grid">
            <div className="surface-list" aria-label="Synthetic product concepts" aria-live="polite">
              {visible.length === 0 && <div className="no-results">
                <strong>No matching surfaces.</strong><p>Try a different term or return to all categories.</p>
                <Button className="reset-button" variant="secondary" onPress={reset}>Reset view</Button>
              </div>}
              {visible.map(surface => (
                <article data-testid="venture-card" key={surface.id} className={"surface-card " + (selected === surface.id ? "is-active" : "")}>
                  <div className="surface-card-head">
                    <span className="surface-index">{surface.code} / {surface.category.toUpperCase()}</span>
                    <span className={"identity-symbol " + surface.visual} aria-hidden="true"><i/><b/></span>
                  </div>
                  <h3>{surface.name}</h3>
                  <p>{surface.short}</p>
                  <div className="surface-card-foot">
                    <span>{surface.stage}</span>
                    <Button className="open-button" variant="secondary" aria-label={"Inspect " + surface.name} onPress={() => setSelected(surface.id)}>Explore <span aria-hidden="true">↗</span></Button>
                  </div>
                </article>
              ))}
            </div>
            <aside className="detail-panel" aria-labelledby="detail-title">
              <div className="detail-top"><span>02 / INSPECT</span><span className="detail-synthetic">DEMO DATA</span></div>
              <div className="detail-sigil"><span className={"identity-symbol " + active.visual} aria-hidden="true"><i/><b/></span></div>
              <p className="detail-label">{active.category.toUpperCase()} / {active.code}</p>
              <h2 id="detail-title">{active.name}</h2>
              <p className="detail-action">{active.action}</p>
              <div className="detail-divider"/>
              <h3>Design priorities</h3>
              <div className="token-list">{active.tokens.map((t,i) => <div className="token-row" key={t}><span>0{i+1}</span><span>{t}</span><span>↗</span></div>)}</div>
              <div className="detail-caution" role="note"><strong>Governance note</strong><p>{active.note}</p></div>
              <Button className="save-button" variant="primary" onPress={toggleSaved} aria-pressed={saved.includes(active.id)}>{saved.includes(active.id) ? "Saved to local selection ✓" : "Save this design direction ↗"}</Button>
              <p className="privacy">Selection lasts only in this page. No backend or analytics.</p>
            </aside>
          </div>
        </section>
      </main>

      <footer><span>© PRYNTOR / ORIGINAL CONCEPT</span><span>FREE HEROUI 3.2.6 · INTERNAL ACCEPTANCE PILOT</span><a href="#main">BACK TO TOP ↑</a></footer>
    </div>
  );
}
