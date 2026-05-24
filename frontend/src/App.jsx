import { useState, useEffect, useCallback } from "react";
import { auth, apiAuth, apiCompanies, apiWorkers, apiDeadlines, apiDocuments, apiTraining, apiMedical, apiDPI, apiAttendance } from "./api.js";

const Icon = ({ d, size = 20, color = "currentColor", strokeWidth = 1.8 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);
const Icons = {
  dashboard:   "M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z M9 22V12h6v10",
  workers:     "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M9 11a4 4 0 100-8 4 4 0 000 8z M23 21v-2a4 4 0 00-3-3.87 M16 3.13a4 4 0 010 7.75",
  deadlines:   "M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01",
  documents:   "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8",
  dpi:         "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
  companies:   "M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z",
  medical:     "M22 12h-4l-3 9L9 3l-3 9H2",
  training:    "M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z",
  attendance:  "M12 2a10 10 0 100 20A10 10 0 0012 2z M12 6v6l4 2",
  bell:        "M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9 M13.73 21a2 2 0 01-3.46 0",
  search:      "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0",
  chevron:     "M9 18l6-6-6-6",
  plus:        "M12 5v14M5 12h14",
  alert:       "M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z M12 9v4 M12 17h.01",
  check:       "M20 6L9 17l-5-5",
  trend_up:    "M23 6l-9.5 9.5-5-5L1 18 M17 6h6v6",
  trend_down:  "M23 18l-9.5-9.5-5 5L1 6 M17 18h6v-6",
  logout:      "M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4 M16 17l5-5-5-5 M21 12H9",
};

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --c-bg:#0F0F13; --c-surface:#16161D; --c-surface2:#1E1E28; --c-border:#2A2A38;
    --c-text:#E8E8F0; --c-muted:#7070A0; --c-orange:#FF6B35; --c-orange2:#FF8C5A;
    --c-teal:#00D4AA; --c-purple:#8B5CF6; --c-yellow:#FFD166; --c-red:#FF4D6D;
    --c-green:#06D6A0; --c-blue:#4CC9F0; --font-head:'Syne',sans-serif;
    --font-body:'DM Sans',sans-serif; --radius:12px; --radius-lg:20px;
    --sidebar-w:240px; --transition:0.2s cubic-bezier(0.4,0,0.2,1);
  }
  body { background:var(--c-bg); color:var(--c-text); font-family:var(--font-body); font-size:14px; line-height:1.6; overflow-x:hidden; }
  ::-webkit-scrollbar { width:4px; } ::-webkit-scrollbar-track { background:var(--c-surface); } ::-webkit-scrollbar-thumb { background:var(--c-border); border-radius:2px; }
  .app { display:flex; height:100vh; overflow:hidden; }
  .sidebar { width:var(--sidebar-w); flex-shrink:0; background:var(--c-surface); border-right:1px solid var(--c-border); display:flex; flex-direction:column; overflow:hidden; position:relative; }
  .sidebar::before { content:''; position:absolute; top:-60px; left:-60px; width:200px; height:200px; border-radius:50%; background:radial-gradient(circle, rgba(255,107,53,0.12) 0%, transparent 70%); pointer-events:none; }
  .sidebar-logo { padding:24px 20px 20px; display:flex; align-items:center; gap:10px; border-bottom:1px solid var(--c-border); }
  .logo-icon { width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg, var(--c-orange), var(--c-purple)); display:flex; align-items:center; justify-content:center; font-family:var(--font-head); font-weight:800; font-size:16px; color:white; flex-shrink:0; }
  .logo-text { font-family:var(--font-head); font-weight:800; font-size:18px; }
  .logo-text span { color:var(--c-orange); }
  .logo-sub { font-size:10px; color:var(--c-muted); text-transform:uppercase; letter-spacing:1px; }
  .sidebar-nav { flex:1; padding:12px 10px; overflow-y:auto; }
  .nav-section { margin-bottom:6px; }
  .nav-label { font-size:10px; color:var(--c-muted); text-transform:uppercase; letter-spacing:1.5px; padding:8px 10px 4px; font-weight:600; }
  .nav-item { display:flex; align-items:center; gap:10px; padding:9px 12px; border-radius:var(--radius); cursor:pointer; transition:all var(--transition); color:var(--c-muted); font-weight:500; font-size:13.5px; position:relative; margin-bottom:2px; }
  .nav-item:hover { background:var(--c-surface2); color:var(--c-text); }
  .nav-item.active { background:linear-gradient(135deg, rgba(255,107,53,0.15), rgba(139,92,246,0.1)); color:var(--c-orange); border:1px solid rgba(255,107,53,0.2); }
  .nav-item.active::before { content:''; position:absolute; left:0; top:50%; transform:translateY(-50%); width:3px; height:60%; background:var(--c-orange); border-radius:0 3px 3px 0; }
  .nav-badge { margin-left:auto; background:var(--c-red); color:white; font-size:10px; font-weight:700; padding:1px 6px; border-radius:10px; }
  .sidebar-footer { padding:16px; border-top:1px solid var(--c-border); }
  .user-card { display:flex; align-items:center; gap:10px; padding:10px; background:var(--c-surface2); border-radius:var(--radius); cursor:pointer; transition:all var(--transition); }
  .user-avatar { width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg, var(--c-orange), var(--c-purple)); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; color:white; flex-shrink:0; }
  .user-name { font-weight:600; font-size:13px; } .user-role { font-size:11px; color:var(--c-muted); }
  .main { flex:1; display:flex; flex-direction:column; overflow:hidden; }
  .topbar { height:60px; background:var(--c-surface); border-bottom:1px solid var(--c-border); display:flex; align-items:center; padding:0 24px; gap:16px; flex-shrink:0; }
  .topbar-title { font-family:var(--font-head); font-size:20px; font-weight:700; flex:1; }
  .search-box { display:flex; align-items:center; gap:8px; background:var(--c-surface2); border:1px solid var(--c-border); border-radius:var(--radius); padding:7px 12px; width:220px; transition:all var(--transition); }
  .search-box:focus-within { border-color:var(--c-orange); width:260px; }
  .search-box input { background:none; border:none; outline:none; color:var(--c-text); font-size:13px; width:100%; font-family:var(--font-body); }
  .search-box input::placeholder { color:var(--c-muted); }
  .icon-btn { width:36px; height:36px; border-radius:var(--radius); background:var(--c-surface2); border:1px solid var(--c-border); display:flex; align-items:center; justify-content:center; cursor:pointer; transition:all var(--transition); position:relative; }
  .icon-btn:hover { background:var(--c-surface); border-color:var(--c-orange); color:var(--c-orange); }
  .notif-dot { position:absolute; top:6px; right:6px; width:7px; height:7px; background:var(--c-red); border-radius:50%; border:1px solid var(--c-surface); }
  .btn { display:flex; align-items:center; gap:6px; padding:8px 16px; border-radius:var(--radius); border:none; cursor:pointer; font-family:var(--font-body); font-size:13px; font-weight:600; transition:all var(--transition); }
  .btn-primary { background:linear-gradient(135deg, var(--c-orange), var(--c-orange2)); color:white; box-shadow:0 4px 14px rgba(255,107,53,0.35); }
  .btn-primary:hover { transform:translateY(-1px); box-shadow:0 6px 20px rgba(255,107,53,0.45); }
  .btn-ghost { background:var(--c-surface2); color:var(--c-muted); border:1px solid var(--c-border); }
  .btn-ghost:hover { color:var(--c-text); border-color:var(--c-text); }
  .content { flex:1; overflow-y:auto; padding:24px; }
  .card { background:var(--c-surface); border:1px solid var(--c-border); border-radius:var(--radius-lg); padding:20px; transition:all var(--transition); }
  .card:hover { border-color:rgba(255,107,53,0.25); }
  .card-title { font-family:var(--font-head); font-size:14px; font-weight:700; color:var(--c-muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:12px; }
  .kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }
  .kpi-card { background:var(--c-surface); border:1px solid var(--c-border); border-radius:var(--radius-lg); padding:20px; position:relative; overflow:hidden; transition:all var(--transition); }
  .kpi-card:hover { transform:translateY(-2px); box-shadow:0 8px 30px rgba(0,0,0,0.3); }
  .kpi-card::after { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:var(--accent); }
  .kpi-glow { position:absolute; top:-20px; right:-20px; width:80px; height:80px; border-radius:50%; opacity:0.15; background:var(--accent); filter:blur(20px); }
  .kpi-label { font-size:12px; color:var(--c-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px; }
  .kpi-value { font-family:var(--font-head); font-size:36px; font-weight:800; line-height:1; margin-bottom:8px; }
  .kpi-trend { display:flex; align-items:center; gap:4px; font-size:12px; font-weight:600; }
  .kpi-trend.up { color:var(--c-green); } .kpi-trend.down { color:var(--c-red); }
  .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px; }
  .grid-3 { display:grid; grid-template-columns:2fr 1fr; gap:16px; margin-bottom:24px; }
  .table-wrap { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; }
  th { text-align:left; padding:10px 14px; font-size:11px; font-weight:700; color:var(--c-muted); text-transform:uppercase; letter-spacing:1px; border-bottom:1px solid var(--c-border); }
  td { padding:12px 14px; border-bottom:1px solid rgba(42,42,56,0.5); font-size:13px; transition:background var(--transition); }
  tr:hover td { background:var(--c-surface2); } tr:last-child td { border-bottom:none; }
  .badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; }
  .badge-green  { background:rgba(6,214,160,0.12);  color:var(--c-green); }
  .badge-red    { background:rgba(255,77,109,0.12);  color:var(--c-red); }
  .badge-yellow { background:rgba(255,209,102,0.12); color:var(--c-yellow); }
  .badge-blue   { background:rgba(76,201,240,0.12);  color:var(--c-blue); }
  .badge-purple { background:rgba(139,92,246,0.12);  color:var(--c-purple); }
  .badge-orange { background:rgba(255,107,53,0.12);  color:var(--c-orange); }
  .avatar { width:32px; height:32px; border-radius:50%; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:12px; color:white; }
  .progress-bar { height:6px; background:var(--c-border); border-radius:3px; overflow:hidden; margin-top:6px; }
  .progress-fill { height:100%; border-radius:3px; transition:width 1s ease; }
  .alert-item { display:flex; align-items:flex-start; gap:12px; padding:12px; border-radius:var(--radius); margin-bottom:8px; border:1px solid var(--c-border); transition:all var(--transition); }
  .alert-item:hover { background:var(--c-surface2); }
  .alert-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; margin-top:5px; }
  .alert-text { font-size:13px; font-weight:500; } .alert-sub { font-size:11px; color:var(--c-muted); margin-top:2px; }
  .chart-bars { display:flex; align-items:flex-end; gap:8px; height:120px; padding:0 4px; }
  .chart-bar-wrap { flex:1; display:flex; flex-direction:column; align-items:center; gap:6px; }
  .chart-bar { width:100%; border-radius:4px 4px 0 0; transition:height 1s ease; min-height:4px; }
  .chart-months { display:flex; justify-content:space-between; padding:8px 4px 0; border-top:1px solid var(--c-border); margin-top:4px; }
  .chart-month-label { font-size:10px; color:var(--c-muted); flex:1; text-align:center; }
  .form-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .form-group { display:flex; flex-direction:column; gap:6px; }
  .form-group.full { grid-column:1/-1; }
  label { font-size:12px; font-weight:600; color:var(--c-muted); text-transform:uppercase; letter-spacing:0.8px; }
  input, select, textarea { background:var(--c-surface2); border:1px solid var(--c-border); border-radius:var(--radius); padding:10px 12px; color:var(--c-text); font-family:var(--font-body); font-size:13px; outline:none; width:100%; transition:all var(--transition); }
  input:focus, select:focus, textarea:focus { border-color:var(--c-orange); box-shadow:0 0 0 3px rgba(255,107,53,0.1); }
  select option { background:var(--c-surface2); }
  .modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.7); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:100; animation:fadeIn 0.2s ease; }
  .modal { background:var(--c-surface); border:1px solid var(--c-border); border-radius:var(--radius-lg); padding:28px; width:520px; max-width:90vw; animation:slideUp 0.25s ease; }
  .modal-title { font-family:var(--font-head); font-size:20px; font-weight:800; margin-bottom:20px; }
  .modal-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:24px; }
  .section-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
  .section-title { font-family:var(--font-head); font-size:24px; font-weight:800; }
  .section-sub { font-size:13px; color:var(--c-muted); margin-top:2px; }
  .timeline { position:relative; padding-left:20px; }
  .timeline::before { content:''; position:absolute; left:7px; top:8px; bottom:8px; width:2px; background:var(--c-border); }
  .timeline-item { position:relative; padding-bottom:16px; }
  .timeline-dot { position:absolute; left:-16px; top:4px; width:10px; height:10px; border-radius:50%; background:var(--c-orange); border:2px solid var(--c-surface); box-shadow:0 0 0 3px rgba(255,107,53,0.2); }
  .timeline-dot.green { background:var(--c-green); box-shadow:0 0 0 3px rgba(6,214,160,0.2); }
  .timeline-dot.red { background:var(--c-red); box-shadow:0 0 0 3px rgba(255,77,109,0.2); }
  .timeline-content { font-size:13px; font-weight:500; } .timeline-meta { font-size:11px; color:var(--c-muted); margin-top:2px; }
  .empty-state { text-align:center; padding:3rem 1rem; color:var(--c-muted); }
  .empty-state p { margin-top:0.5rem; font-size:13px; }
  @keyframes fadeIn { from{opacity:0} to{opacity:1} }
  @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
`;

const avatarColor = (name) => {
  const colors = ["#FF6B35","#8B5CF6","#00D4AA","#4CC9F0","#FFD166","#FF4D6D"];
  let h = 0; for (const c of (name||"?")) h = c.charCodeAt(0) + ((h<<5)-h);
  return colors[Math.abs(h) % colors.length];
};
const initials = (name) => (name||"?").split(" ").map(w=>w[0]).join("").slice(0,2).toUpperCase();
const statoBadge = (s) => {
  const map = {
    ATTIVO:"green", ACTIVE:"green", AVAILABLE:"green", SUPERATO:"green", IDONEO:"green", COMPLETED:"green",
    INATTIVO:"red", EXPIRED:"red", DISPOSED:"red", NON_IDONEO:"red", ALERT:"red", SOSPESA:"red", ABSENT:"red", NON_SUPERATO:"red",
    PENDING:"yellow", MAINTENANCE:"yellow", LATE:"yellow", IDONEO_LIMITAZIONI:"yellow", SCHEDULED:"yellow",
    ASSIGNED:"blue", ATTIVA:"blue", PRESENT:"blue",
    LOW:"blue", MEDIUM:"yellow", HIGH:"orange", OBBLIGATORIO:"orange",
  };
  return map[s] || "blue";
};
const Badge = ({ text }) => <span className={`badge badge-${statoBadge(text)}`}>{text}</span>;
const KPICard = ({ label, value, trend, trendLabel, accent }) => (
  <div className="kpi-card" style={{"--accent": accent}}>
    <div className="kpi-glow" />
    <div className="kpi-label">{label}</div>
    <div className="kpi-value" style={{color: accent}}>{value}</div>
    {trend !== undefined && (
      <div className={`kpi-trend ${trend >= 0 ? "up" : "down"}`}>
        <Icon d={trend >= 0 ? Icons.trend_up : Icons.trend_down} size={14} color="currentColor" />
        {Math.abs(trend)}% {trendLabel}
      </div>
    )}
  </div>
);
const MiniBar = ({ val, max, color }) => (
  <div className="progress-bar">
    <div className="progress-fill" style={{width:`${max>0?(val/max)*100:0}%`, background:color}} />
  </div>
);
const EmptyState = ({ message = "Nessun dato disponibile.", action }) => (
  <div className="empty-state">
    <Icon d={Icons.alert} size={32} color="var(--c-muted)" />
    <p>{message}</p>
    {action}
  </div>
);

function DashboardView({ workers, deadlines, companies, documents, dpiItems }) {
  const alertCount = deadlines.filter(d => {
    const s = d.stato || d.status || "";
    return s === "ALERT" || s === "EXPIRED";
  }).length;
  const activeWorkers = workers.filter(w => (w.stato || w.status) === "ACTIVE").length;
  const dpiAssigned = dpiItems.filter(d => d.stato === "ASSIGNED").length;
  const dpiMaint   = dpiItems.filter(d => d.stato === "MAINTENANCE").length;
  const urgentDeadlines = deadlines.filter(d => {
    const s = d.stato || d.status || "";
    return s === "ALERT" || s === "EXPIRED";
  }).slice(0, 5);
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Dashboard</div><div className="section-sub">Panoramica sicurezza</div></div>
      </div>
      <div className="kpi-grid">
        <KPICard label="Lavoratori Attivi"    value={activeWorkers}    accent="var(--c-teal)" />
        <KPICard label="Scadenze Critiche"    value={alertCount}       accent="var(--c-red)" />
        <KPICard label="Aziende Gestite"      value={companies.length} accent="var(--c-purple)" />
        <KPICard label="Documenti Archiviati" value={documents.length} accent="var(--c-yellow)" />
      </div>
      <div className="grid-3">
        <div className="card">
          <div className="card-title">Stato DPI</div>
          {dpiItems.length === 0 ? <EmptyState message="Nessun DPI registrato." /> : (
            <div style={{display:"flex",flexDirection:"column",gap:"10px",marginTop:"4px"}}>
              {[
                {label:"Assegnati",  val:dpiAssigned,                          max:dpiItems.length, color:"var(--c-blue)"},
                {label:"Disponibili",val:dpiItems.length-dpiAssigned-dpiMaint, max:dpiItems.length, color:"var(--c-green)"},
                {label:"Manutenzione",val:dpiMaint,                            max:dpiItems.length, color:"var(--c-yellow)"},
              ].map((r,i)=>(
                <div key={i}>
                  <div style={{display:"flex",justifyContent:"space-between",marginBottom:"4px"}}>
                    <span style={{fontSize:"12px",color:"var(--c-muted)"}}>{r.label}</span>
                    <span style={{fontSize:"12px",fontWeight:"700"}}>{r.val}</span>
                  </div>
                  <MiniBar val={r.val} max={r.max} color={r.color} />
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="card">
          <div className="card-title">Sommario</div>
          <div style={{display:"flex",flexDirection:"column",gap:"8px",marginTop:"4px"}}>
            {[
              {label:"Lavoratori totali",     val:workers.length},
              {label:"Aziende attive",        val:companies.filter(c=>c.is_active!==false).length},
              {label:"DPI totali",            val:dpiItems.length},
              {label:"Scadenze pending",      val:deadlines.filter(d=>(d.stato||"PENDING")==="PENDING").length},
            ].map((r,i)=>(
              <div key={i} style={{display:"flex",justifyContent:"space-between",padding:"8px",background:"var(--c-surface2)",borderRadius:"8px"}}>
                <span style={{fontSize:"12px",color:"var(--c-muted)"}}>{r.label}</span>
                <span style={{fontSize:"14px",fontWeight:"700",color:"var(--c-text)"}}>{r.val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="card">
        <div className="card-title">⚠ Scadenze Urgenti</div>
        {urgentDeadlines.length === 0
          ? <EmptyState message="Nessuna scadenza urgente." />
          : urgentDeadlines.map(d=>(
            <div key={d.id} className="alert-item">
              <div className="alert-dot" style={{background:(d.stato||d.status)==="EXPIRED"?"var(--c-red)":"var(--c-yellow)"}} />
              <div>
                <div className="alert-text">{d.titolo || d.descrizione}</div>
                <div className="alert-sub">{d.data_scadenza || d.data} · <Badge text={d.stato||d.status}/></div>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}

function WorkersView({ workers, onAdd }) {
  const [search, setSearch] = useState("");
  const fullName = (w) => `${w.cognome || ""} ${w.nome || ""}`.trim() || w.nome || "";
  const filtered = workers.filter(w => {
    const s = search.toLowerCase();
    return fullName(w).toLowerCase().includes(s)
      || (w.mansione||"").toLowerCase().includes(s)
      || (w.codice_fiscale||"").toLowerCase().includes(s);
  });
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Lavoratori</div><div className="section-sub">{workers.length} lavoratori registrati</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuovo</button>
      </div>
      <div className="card">
        <div style={{marginBottom:"16px"}}>
          <div className="search-box" style={{width:"100%"}}>
            <Icon d={Icons.search} size={15} color="var(--c-muted)"/>
            <input placeholder="Cerca per nome, mansione, CF..." value={search} onChange={e=>setSearch(e.target.value)}/>
          </div>
        </div>
        {filtered.length === 0
          ? <EmptyState message={workers.length===0 ? "Nessun lavoratore. Clicca \"Nuovo\" per aggiungerne uno." : "Nessun risultato per la ricerca."} />
          : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lavoratore</th><th>Mansione</th><th>C.F.</th><th>Contratto</th><th>Stato</th><th>Assunzione</th></tr></thead>
              <tbody>
                {filtered.map(w=>(
                  <tr key={w.id}>
                    <td><div style={{display:"flex",alignItems:"center",gap:"10px"}}><div className="avatar" style={{background:avatarColor(fullName(w))}}>{initials(fullName(w))}</div><span style={{fontWeight:600}}>{fullName(w)}</span></div></td>
                    <td style={{color:"var(--c-muted)"}}>{w.mansione}</td>
                    <td style={{fontFamily:"monospace",fontSize:"0.8rem"}}>{w.codice_fiscale}</td>
                    <td><Badge text={w.tipo_contratto||"FULL_TIME"}/></td>
                    <td><Badge text={w.stato||"ACTIVE"}/></td>
                    <td style={{color:"var(--c-muted)"}}>{w.data_assunzione}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function DeadlinesView({ deadlines, onAdd }) {
  const [filter, setFilter] = useState("ALL");
  const filters = ["ALL","ALERT","PENDING","EXPIRED","COMPLETED"];
  const filtered = filter==="ALL" ? deadlines : deadlines.filter(d=>(d.stato||d.status||"PENDING")===filter);
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Scadenze</div><div className="section-sub">Monitoraggio D.Lgs. 81/08</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuova</button>
      </div>
      <div style={{display:"flex",gap:"8px",marginBottom:"16px",flexWrap:"wrap"}}>
        {filters.map(f=>(
          <button key={f} onClick={()=>setFilter(f)} className="btn" style={{background:filter===f?"var(--c-orange)":"var(--c-surface2)",color:filter===f?"white":"var(--c-muted)",border:`1px solid ${filter===f?"var(--c-orange)":"var(--c-border)"}`,padding:"6px 14px",fontSize:"12px"}}>{f}</button>
        ))}
      </div>
      <div className="card">
        {filtered.length === 0
          ? <EmptyState message="Nessuna scadenza in questa categoria." />
          : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Tipo</th><th>Titolo</th><th>Data Scadenza</th><th>Priorità</th><th>Stato</th></tr></thead>
              <tbody>
                {filtered.map(d=>(
                  <tr key={d.id}>
                    <td><span style={{fontSize:"11px",color:"var(--c-muted)",fontWeight:700}}>{d.tipo}</span></td>
                    <td style={{fontWeight:600}}>{d.titolo || d.descrizione}</td>
                    <td style={{color:new Date(d.data_scadenza||d.data)<new Date()?"var(--c-red)":"var(--c-text)"}}>{d.data_scadenza || d.data}</td>
                    <td><Badge text={d.priorita}/></td>
                    <td><Badge text={d.stato||d.status}/></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function DocumentsView({ documents, onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Documenti</div><div className="section-sub">{documents.length} documenti archiviati</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Carica</button>
      </div>
      <div className="card">
        {documents.length === 0
          ? <EmptyState message="Nessun documento archiviato." />
          : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Titolo</th><th>Categoria</th><th>Data</th><th>Versione</th><th>Stato</th></tr></thead>
              <tbody>
                {documents.map(d=>(
                  <tr key={d.id}>
                    <td><div style={{display:"flex",alignItems:"center",gap:"8px"}}><Icon d={Icons.documents} size={15} color="var(--c-muted)"/><span style={{fontWeight:600}}>{d.titolo}</span></div></td>
                    <td><Badge text={d.categoria}/></td>
                    <td>{d.data_caricamento || d.created_at?.split("T")[0]}</td>
                    <td style={{color:"var(--c-muted)"}}>v{d.versione||1}</td>
                    <td><Badge text={d.stato||"ACTIVE"}/></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function DPIView({ dpiItems, onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">DPI</div><div className="section-sub">Dispositivi di Protezione Individuale</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuovo DPI</button>
      </div>
      <div className="kpi-grid" style={{gridTemplateColumns:"repeat(3,1fr)"}}>
        {[
          {label:"Totale DPI",    val:dpiItems.length,                                color:"var(--c-blue)"},
          {label:"Assegnati",     val:dpiItems.filter(d=>d.stato==="ASSIGNED").length, color:"var(--c-orange)"},
          {label:"Manutenzione",  val:dpiItems.filter(d=>d.stato==="MAINTENANCE").length, color:"var(--c-yellow)"},
        ].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color}}>{k.val}</div></div>
        ))}
      </div>
      <div className="card">
        {dpiItems.length === 0
          ? <EmptyState message="Nessun DPI registrato." />
          : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Codice</th><th>Nome</th><th>Categoria</th><th>Stato</th><th>Scadenza</th></tr></thead>
              <tbody>
                {dpiItems.map(d=>(
                  <tr key={d.id}>
                    <td style={{fontFamily:"monospace",color:"var(--c-orange)",fontSize:"12px"}}>{d.codice}</td>
                    <td style={{fontWeight:600}}>{d.nome}</td>
                    <td><span style={{fontSize:"11px",color:"var(--c-muted)"}}>{d.categoria}</span></td>
                    <td><Badge text={d.stato}/></td>
                    <td style={{color:d.data_scadenza&&new Date(d.data_scadenza)<new Date()?"var(--c-red)":"var(--c-text)"}}>{d.data_scadenza||"—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function CompaniesView({ companies, onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Aziende</div><div className="section-sub">{companies.length} aziende clienti</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuova Azienda</button>
      </div>
      {companies.length === 0
        ? <div className="card"><EmptyState message="Nessuna azienda. Clicca \"Nuova Azienda\" per aggiungerne una." /></div>
        : (
        <div style={{display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:"16px"}}>
          {companies.map(c=>(
            <div key={c.id} className="card" style={{cursor:"pointer"}}>
              <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",marginBottom:"14px"}}>
                <div style={{display:"flex",alignItems:"center",gap:"12px"}}>
                  <div className="avatar" style={{width:44,height:44,fontSize:16,background:avatarColor(c.ragione_sociale||""),borderRadius:"12px"}}>{initials(c.ragione_sociale||"?")}</div>
                  <div><div style={{fontFamily:"var(--font-head)",fontWeight:800,fontSize:"16px"}}>{c.ragione_sociale}</div><div style={{fontSize:"12px",color:"var(--c-muted)"}}>{c.codice_ateco||"—"}</div></div>
                </div>
                <Badge text={c.is_active!==false?"ACTIVE":"INACTIVE"}/>
              </div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"10px"}}>
                <div style={{background:"var(--c-surface2)",borderRadius:"8px",padding:"10px"}}><div style={{fontSize:"11px",color:"var(--c-muted)",marginBottom:"4px"}}>P.IVA</div><div style={{fontFamily:"monospace",fontSize:"12px",color:"var(--c-muted)"}}>{c.partita_iva}</div></div>
                <div style={{background:"var(--c-surface2)",borderRadius:"8px",padding:"10px"}}><div style={{fontSize:"11px",color:"var(--c-muted)",marginBottom:"4px"}}>Email</div><div style={{fontSize:"12px",color:"var(--c-muted)",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{c.email||"—"}</div></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MedicalView({ visits, protocols, onAdd }) {
  const [tab, setTab] = useState("visite");
  const idonei    = visits.filter(v=>v.esito==="IDONEO").length;
  const limitati  = visits.filter(v=>v.esito==="IDONEO_LIMITAZIONI").length;
  const scheduled = visits.filter(v=>v.stato==="SCHEDULED").length;
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Medicina del Lavoro</div><div className="section-sub">Protocolli sanitari e visite mediche D.Lgs.81/08</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuova Visita</button>
      </div>
      <div className="kpi-grid">
        {[
          {label:"Visite Totali",     val:visits.length, color:"var(--c-blue)"},
          {label:"Idonei",            val:idonei,         color:"var(--c-green)"},
          {label:"Con Limitazioni",   val:limitati,       color:"var(--c-yellow)"},
          {label:"Da Effettuare",     val:scheduled,      color:"var(--c-orange)"},
        ].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color,fontSize:"32px"}}>{k.val}</div></div>
        ))}
      </div>
      <div style={{display:"flex",gap:"8px",marginBottom:"16px"}}>
        {["visite","protocolli"].map(t=>(
          <button key={t} className="btn" onClick={()=>setTab(t)} style={{background:tab===t?"var(--c-orange)":"var(--c-surface2)",color:tab===t?"white":"var(--c-muted)",border:`1px solid ${tab===t?"var(--c-orange)":"var(--c-border)"}`}}>{t==="visite"?"Visite Mediche":"Protocolli Sanitari"}</button>
        ))}
      </div>
      {tab==="visite" && (
        <div className="card">
          {visits.length === 0
            ? <EmptyState message="Nessuna visita medica registrata." />
            : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Lavoratore</th><th>Tipo</th><th>Medico</th><th>Data</th><th>Prossima</th><th>Esito</th><th>Stato</th></tr></thead>
                <tbody>
                  {visits.map(v=>(
                    <tr key={v.id}>
                      <td><span style={{fontFamily:"monospace",fontSize:"11px",color:"var(--c-muted)"}}>#{v.worker_id}</span></td>
                      <td><span style={{fontSize:"11px",color:"var(--c-muted)",fontWeight:700}}>{v.tipo}</span></td>
                      <td style={{color:"var(--c-muted)"}}>{v.medico||"—"}</td>
                      <td>{v.data_visita}</td>
                      <td style={{color:v.data_prossima_visita&&new Date(v.data_prossima_visita)<new Date()?"var(--c-red)":"var(--c-text)"}}>{v.data_prossima_visita||"—"}</td>
                      <td>{v.esito?<Badge text={v.esito}/>:<span style={{color:"var(--c-muted)"}}>—</span>}</td>
                      <td><Badge text={v.stato}/></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      {tab==="protocolli" && (
        protocols.length === 0
          ? <div className="card"><EmptyState message="Nessun protocollo sanitario definito." /></div>
          : (
          <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:"16px"}}>
            {protocols.map(p=>(
              <div key={p.id} className="card">
                <div style={{display:"flex",alignItems:"center",gap:"10px",marginBottom:"14px"}}>
                  <div style={{width:40,height:40,borderRadius:"10px",background:"linear-gradient(135deg,var(--c-teal),var(--c-blue))",display:"flex",alignItems:"center",justifyContent:"center"}}><Icon d={Icons.medical} size={18} color="white"/></div>
                  <div><div style={{fontWeight:700,fontSize:"14px"}}>Azienda #{p.company_id}</div><div style={{fontSize:"11px",color:"var(--c-muted)"}}>Approv. {p.data_approvazione||"—"}</div></div>
                </div>
                <div style={{fontSize:"13px",fontWeight:600,marginBottom:"6px"}}>{p.titolo}</div>
                <div style={{fontSize:"12px",color:"var(--c-muted)"}}>{p.medico_competente||"—"}</div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}

function TrainingView({ courses, onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Formazione</div><div className="section-sub">Gestione corsi, edizioni e attestati</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuovo Corso</button>
      </div>
      <div className="kpi-grid" style={{gridTemplateColumns:"repeat(2,1fr)"}}>
        {[
          {label:"Corsi Attivi",  val:courses.length, color:"var(--c-purple)"},
          {label:"Obbligatori",   val:courses.filter(c=>c.tipo==="OBBLIGATORIO").length, color:"var(--c-orange)"},
        ].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color,fontSize:"32px"}}>{k.val}</div></div>
        ))}
      </div>
      {courses.length === 0
        ? <div className="card"><EmptyState message="Nessun corso nel catalogo." /></div>
        : (
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"16px"}}>
          {courses.map(c=>(
            <div key={c.id} className="card" style={{cursor:"pointer"}}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:"12px"}}>
                <div style={{fontFamily:"monospace",fontSize:"11px",color:"var(--c-orange)",fontWeight:700}}>{c.codice}</div>
                <Badge text={c.tipo}/>
              </div>
              <div style={{fontFamily:"var(--font-head)",fontWeight:800,fontSize:"15px",marginBottom:"8px"}}>{c.titolo}</div>
              <div style={{display:"flex",gap:"16px",fontSize:"12px",color:"var(--c-muted)"}}>
                <span>⏱ {c.durata_ore}h</span>
                {c.provider && <span>🏫 {c.provider}</span>}
                <span>📅 validità {c.validita_anni||3} anni</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AttendanceView({ records, onAdd }) {
  const presenti = records.filter(r=>r.stato==="PRESENT").length;
  const assenti  = records.filter(r=>r.stato==="ABSENT").length;
  const ritardi  = records.filter(r=>r.stato==="LATE").length;
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Presenze</div><div className="section-sub">Registro presenze giornaliero</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Timbratura Manuale</button>
      </div>
      <div className="kpi-grid">
        {[
          {label:"Presenti",  val:presenti, color:"var(--c-green)"},
          {label:"Assenti",   val:assenti,  color:"var(--c-red)"},
          {label:"Ritardi",   val:ritardi,  color:"var(--c-yellow)"},
          {label:"Totale",    val:records.length, color:"var(--c-blue)"},
        ].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color,fontSize:"32px"}}>{k.val}</div></div>
        ))}
      </div>
      <div className="card">
        {records.length === 0
          ? <EmptyState message="Nessun record presenze." />
          : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lavoratore</th><th>Data</th><th>Stato</th><th>Entrata</th><th>Uscita</th><th>Ore Lav.</th><th>Approvato</th></tr></thead>
              <tbody>
                {records.map(r=>(
                  <tr key={r.id}>
                    <td style={{fontFamily:"monospace",fontSize:"11px",color:"var(--c-muted)"}}>#{r.worker_id}</td>
                    <td style={{color:"var(--c-muted)"}}>{r.data}</td>
                    <td><Badge text={r.stato}/></td>
                    <td style={{fontFamily:"monospace",color:"var(--c-teal)",fontWeight:700}}>{r.ora_entrata||"—"}</td>
                    <td style={{fontFamily:"monospace",color:"var(--c-orange)",fontWeight:700}}>{r.ora_uscita||"—"}</td>
                    <td style={{fontWeight:700}}>{r.ore_lavorate?`${r.ore_lavorate}h`:"—"}</td>
                    <td>{r.approvato?<span style={{color:"var(--c-green)",fontWeight:700}}>✓</span>:<span style={{color:"var(--c-muted)"}}>Pending</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function AddModal({ view, onClose, onSaved, data }) {
  const titles = { workers:"Nuovo Lavoratore", deadlines:"Nuova Scadenza", documents:"Carica Documento", dpi:"Nuovo DPI", companies:"Nuova Azienda", medical:"Nuova Visita", training:"Nuovo Corso", attendance:"Timbratura Manuale" };
  const [form, setForm] = useState({});
  const [file, setFile] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const set = (k,v) => setForm(f=>({...f,[k]:v}));

  const handleSave = async () => {
    setSaving(true); setError(null);
    try {
      if (view==="workers") {
        if (!form.nome || !form.cognome || !form.codice_fiscale || !form.data_nascita || !form.mansione || !form.data_assunzione) { setError("Compila tutti i campi obbligatori (*)"); setSaving(false); return; }
        if (form.codice_fiscale.length !== 16) { setError("Il Codice Fiscale deve essere di 16 caratteri"); setSaving(false); return; }
        await apiWorkers.create({ nome:form.nome, cognome:form.cognome, mansione:form.mansione, codice_fiscale:form.codice_fiscale, data_nascita:form.data_nascita, luogo_nascita:form.luogo_nascita||null, data_assunzione:form.data_assunzione, tipo_contratto:form.tipo_contratto||"FULL_TIME", company_id:parseInt(form.company_id)||1, email:form.email||null, telefono:form.telefono||null, is_rspp:form.is_rspp||false, is_rls:form.is_rls||false, is_medico_competente:false });
      } else if (view==="companies") {
        if (!form.ragione_sociale) { setError("Inserisci la ragione sociale"); setSaving(false); return; }
        const piva = (form.partita_iva||"").replace(/\D/g,"");
        if (piva.length !== 11) { setError("La P.IVA deve essere di esattamente 11 cifre"); setSaving(false); return; }
        const cf = (form.codice_fiscale||"").toUpperCase().replace(/[^A-Z0-9]/g,"");
        if (cf.length !== 11 && cf.length !== 16) { setError("Il Codice Fiscale deve essere 11 cifre (aziende) o 16 caratteri (persone fisiche)"); setSaving(false); return; }
        await apiCompanies.create({ ragione_sociale:form.ragione_sociale, partita_iva:piva, codice_fiscale:cf.length===11?cf.padEnd(16,"0"):cf, email:form.email||null, telefono:form.telefono||null, codice_ateco:form.codice_ateco||null });
      } else if (view==="deadlines") {
        await apiDeadlines.create({ titolo:form.titolo||"Nuova scadenza", tipo:form.tipo||"ALTRO", priorita:form.priorita||"MEDIUM", data_scadenza:form.data_scadenza||new Date().toISOString().split("T")[0], company_id:parseInt(form.company_id)||1, worker_id:form.worker_id?parseInt(form.worker_id):null, giorni_preavviso:parseInt(form.giorni_preavviso)||30 });
      } else if (view==="dpi") {
        await apiDPI.createItem({ codice:form.codice||"DPI-NEW", nome:form.nome, categoria:form.categoria||"ALTRO", marca:form.marca, data_acquisto:form.data_acquisto, data_scadenza:form.data_scadenza, costo:parseFloat(form.costo)||0, company_id:parseInt(form.company_id)||1 });
      } else if (view==="medical") {
        await apiMedical.createVisit({ worker_id:parseInt(form.worker_id)||1, company_id:parseInt(form.company_id)||1, tipo:form.tipo||"PERIODICA", data_visita:form.data_visita||new Date().toISOString().split("T")[0], medico:form.medico, struttura:form.struttura, data_prossima_visita:form.data_prossima_visita, note:form.note });
      } else if (view==="training") {
        await apiTraining.createCourse({ codice:form.codice||"FOR-NEW", titolo:form.titolo, tipo:form.tipo||"OBBLIGATORIO", durata_ore:parseFloat(form.durata_ore)||8, validita_anni:parseInt(form.validita_anni)||3, provider:form.provider, company_id:parseInt(form.company_id)||1 });
      } else if (view==="attendance") {
        await apiAttendance.createTimbratura({ worker_id:parseInt(form.worker_id)||1, company_id:parseInt(form.company_id)||1, tipo:form.tipo||"ENTRATA", metodo:form.metodo||"MANUALE", timestamp:form.timestamp||new Date().toISOString(), note:form.note });
      } else if (view==="documents") {
        if (!file) { setError("Seleziona un file da caricare"); setSaving(false); return; }
        const fd = new FormData();
        fd.append("file", file);
        fd.append("titolo", form.titolo||file.name);
        fd.append("categoria", form.categoria||"ALTRO");
        fd.append("company_id", form.company_id||"1");
        if (form.worker_id) fd.append("worker_id", form.worker_id);
        const token = auth.getToken();
        const res = await fetch("/api/v1/documents/upload", { method:"POST", headers:{ Authorization:`Bearer ${token}` }, body:fd });
        if (!res.ok) { const e = await res.json().catch(()=>({detail:"Errore upload"})); throw new Error(e.detail); }
      }
      onSaved();
      onClose();
    } catch(e) { setError(e.message); }
    finally { setSaving(false); }
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e=>e.stopPropagation()}>
        <div className="modal-title">{titles[view]||"Nuovo"}</div>
        {view==="workers" && (
          <div className="form-grid">
            <div className="form-group"><label>Nome *</label><input placeholder="Mario" value={form.nome||""} onChange={e=>set("nome",e.target.value)}/></div>
            <div className="form-group"><label>Cognome *</label><input placeholder="Rossi" value={form.cognome||""} onChange={e=>set("cognome",e.target.value)}/></div>
            <div className="form-group"><label>Codice Fiscale *</label><input placeholder="RSSMRA80A01H501Z" maxLength={16} value={form.codice_fiscale||""} onChange={e=>set("codice_fiscale",e.target.value.toUpperCase())}/></div>
            <div className="form-group"><label>Data Nascita *</label><input type="date" value={form.data_nascita||""} onChange={e=>set("data_nascita",e.target.value)}/></div>
            <div className="form-group"><label>Luogo Nascita</label><input placeholder="Roma" value={form.luogo_nascita||""} onChange={e=>set("luogo_nascita",e.target.value)}/></div>
            <div className="form-group"><label>Mansione *</label><input placeholder="Operaio" value={form.mansione||""} onChange={e=>set("mansione",e.target.value)}/></div>
            <div className="form-group"><label>Azienda *</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Contratto</label><select value={form.tipo_contratto||"FULL_TIME"} onChange={e=>set("tipo_contratto",e.target.value)}><option value="FULL_TIME">Tempo Pieno</option><option value="PART_TIME">Part Time</option><option value="TEMPORARY">Temporaneo</option><option value="APPRENTICE">Apprendistato</option><option value="PROJECT">Progetto</option></select></div>
            <div className="form-group"><label>Data Assunzione *</label><input type="date" value={form.data_assunzione||""} onChange={e=>set("data_assunzione",e.target.value)}/></div>
            <div className="form-group"><label>Email</label><input type="email" placeholder="mario.rossi@email.it" value={form.email||""} onChange={e=>set("email",e.target.value)}/></div>
            <div className="form-group"><label>Telefono</label><input placeholder="+39 333 1234567" value={form.telefono||""} onChange={e=>set("telefono",e.target.value)}/></div>
            <div className="form-group"><label>RSPP</label><select value={form.is_rspp||"false"} onChange={e=>set("is_rspp",e.target.value==="true")}><option value="false">No</option><option value="true">Sì</option></select></div>
            <div className="form-group"><label>RLS</label><select value={form.is_rls||"false"} onChange={e=>set("is_rls",e.target.value==="true")}><option value="false">No</option><option value="true">Sì</option></select></div>
          </div>
        )}
        {view==="deadlines" && (
          <div className="form-grid">
            <div className="form-group full"><label>Titolo *</label><input placeholder="Descrizione scadenza..." value={form.titolo||""} onChange={e=>set("titolo",e.target.value)}/></div>
            <div className="form-group"><label>Tipo</label><select value={form.tipo||"ALTRO"} onChange={e=>set("tipo",e.target.value)}><option value="FORMAZIONE">Formazione</option><option value="VISITA_MEDICA">Visita Medica</option><option value="MANUTENZIONE_ATTREZZATURA">Manutenzione</option><option value="RINNOVO_DOCUMENTO">Rinnovo Documento</option><option value="SOSTITUZIONE_DPI">Sostituzione DPI</option><option value="ALTRO">Altro</option></select></div>
            <div className="form-group"><label>Priorità</label><select value={form.priorita||"MEDIUM"} onChange={e=>set("priorita",e.target.value)}><option value="LOW">Bassa</option><option value="MEDIUM">Media</option><option value="HIGH">Alta</option></select></div>
            <div className="form-group"><label>Azienda</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Lavoratore</label><select value={form.worker_id||""} onChange={e=>set("worker_id",e.target.value)}><option value="">— Tutti —</option>{data.workers.map(w=><option key={w.id} value={w.id}>{w.cognome} {w.nome}</option>)}</select></div>
            <div className="form-group"><label>Data Scadenza *</label><input type="date" value={form.data_scadenza||""} onChange={e=>set("data_scadenza",e.target.value)}/></div>
            <div className="form-group"><label>Giorni Preavviso</label><input type="number" min={1} value={form.giorni_preavviso||30} onChange={e=>set("giorni_preavviso",e.target.value)}/></div>
          </div>
        )}
        {view==="documents" && (
          <div className="form-grid">
            <div className="form-group full"><label>File *</label><input type="file" onChange={e=>setFile(e.target.files[0])} style={{background:"#0f1117",border:"1px solid #2a2d3e",borderRadius:"8px",padding:"0.5rem",color:"#fff",width:"100%",boxSizing:"border-box"}}/></div>
            <div className="form-group full"><label>Titolo</label><input placeholder="Titolo documento (opzionale)" value={form.titolo||""} onChange={e=>set("titolo",e.target.value)}/></div>
            <div className="form-group"><label>Categoria</label><select value={form.categoria||"ALTRO"} onChange={e=>set("categoria",e.target.value)}><option value="SICUREZZA">Sicurezza</option><option value="FORMAZIONE">Formazione</option><option value="MEDICINA">Medicina</option><option value="CONTRATTO">Contratto</option><option value="DPI">DPI</option><option value="ALTRO">Altro</option></select></div>
            <div className="form-group"><label>Azienda</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Lavoratore</label><select value={form.worker_id||""} onChange={e=>set("worker_id",e.target.value)}><option value="">— Nessuno —</option>{data.workers.map(w=><option key={w.id} value={w.id}>{w.cognome} {w.nome}</option>)}</select></div>
          </div>
        )}
        {view==="dpi" && (
          <div className="form-grid">
            <div className="form-group"><label>Codice *</label><input placeholder="DPI-006" value={form.codice||""} onChange={e=>set("codice",e.target.value)}/></div>
            <div className="form-group"><label>Nome *</label><input placeholder="Nome dispositivo" value={form.nome||""} onChange={e=>set("nome",e.target.value)}/></div>
            <div className="form-group"><label>Categoria</label><select value={form.categoria||"ALTRO"} onChange={e=>set("categoria",e.target.value)}><option value="TESTA">Testa</option><option value="OCCHI_VISO">Occhi/Viso</option><option value="UDITO">Udito</option><option value="VIE_RESPIRATORIE">Vie Respiratorie</option><option value="MANI_BRACCIA">Mani/Braccia</option><option value="PIEDI_GAMBE">Piedi/Gambe</option><option value="CORPO">Corpo</option><option value="ANTICADUTA">Anticaduta</option><option value="ALTRO">Altro</option></select></div>
            <div className="form-group"><label>Azienda</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Marca</label><input placeholder="3M, Honeywell..." value={form.marca||""} onChange={e=>set("marca",e.target.value)}/></div>
            <div className="form-group"><label>Costo (€)</label><input type="number" min={0} value={form.costo||""} onChange={e=>set("costo",e.target.value)}/></div>
            <div className="form-group"><label>Data Acquisto</label><input type="date" value={form.data_acquisto||""} onChange={e=>set("data_acquisto",e.target.value)}/></div>
            <div className="form-group"><label>Data Scadenza</label><input type="date" value={form.data_scadenza||""} onChange={e=>set("data_scadenza",e.target.value)}/></div>
          </div>
        )}
        {view==="companies" && (
          <div className="form-grid">
            <div className="form-group full"><label>Ragione Sociale *</label><input placeholder="Nome Azienda SRL" value={form.ragione_sociale||""} onChange={e=>set("ragione_sociale",e.target.value)}/></div>
            <div className="form-group"><label>P.IVA * (11 cifre)</label><input placeholder="01234567890" maxLength={11} value={form.partita_iva||""} onChange={e=>set("partita_iva",e.target.value.replace(/\D/g,""))}/></div>
            <div className="form-group"><label>Codice Fiscale * (11 o 16 car.)</label><input placeholder="01234567890 oppure RSSMRA80A01H501Z" maxLength={16} value={form.codice_fiscale||""} onChange={e=>set("codice_fiscale",e.target.value.toUpperCase().replace(/[^A-Z0-9]/g,""))}/></div>
            <div className="form-group"><label>Email</label><input type="email" placeholder="info@azienda.it" value={form.email||""} onChange={e=>set("email",e.target.value)}/></div>
            <div className="form-group"><label>Telefono</label><input placeholder="+39 02 1234567" value={form.telefono||""} onChange={e=>set("telefono",e.target.value)}/></div>
            <div className="form-group"><label>Codice ATECO</label><input placeholder="41.20.00" value={form.codice_ateco||""} onChange={e=>set("codice_ateco",e.target.value)}/></div>
          </div>
        )}
        {view==="medical" && (
          <div className="form-grid">
            <div className="form-group"><label>Lavoratore *</label><select value={form.worker_id||""} onChange={e=>set("worker_id",e.target.value)}><option value="">— Seleziona —</option>{data.workers.map(w=><option key={w.id} value={w.id}>{w.cognome} {w.nome}</option>)}</select></div>
            <div className="form-group"><label>Azienda</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Tipo Visita</label><select value={form.tipo||"PERIODICA"} onChange={e=>set("tipo",e.target.value)}><option value="PREVENTIVA">Preventiva</option><option value="PERIODICA">Periodica</option><option value="REINTEGRO">Reintegro</option><option value="CAMBIO_MANSIONE">Cambio Mansione</option><option value="CESSAZIONE">Cessazione</option><option value="STRAORDINARIA">Straordinaria</option></select></div>
            <div className="form-group"><label>Data Visita *</label><input type="date" value={form.data_visita||""} onChange={e=>set("data_visita",e.target.value)}/></div>
            <div className="form-group"><label>Medico</label><input placeholder="Dr. Bianchi" value={form.medico||""} onChange={e=>set("medico",e.target.value)}/></div>
            <div className="form-group"><label>Struttura</label><input placeholder="Nome clinica/studio" value={form.struttura||""} onChange={e=>set("struttura",e.target.value)}/></div>
            <div className="form-group"><label>Prossima Visita</label><input type="date" value={form.data_prossima_visita||""} onChange={e=>set("data_prossima_visita",e.target.value)}/></div>
            <div className="form-group full"><label>Note</label><textarea rows={2} placeholder="Note aggiuntive..." value={form.note||""} onChange={e=>set("note",e.target.value)}/></div>
          </div>
        )}
        {view==="training" && (
          <div className="form-grid">
            <div className="form-group"><label>Codice *</label><input placeholder="FOR-006" value={form.codice||""} onChange={e=>set("codice",e.target.value)}/></div>
            <div className="form-group"><label>Titolo *</label><input placeholder="Nome corso" value={form.titolo||""} onChange={e=>set("titolo",e.target.value)}/></div>
            <div className="form-group"><label>Tipo</label><select value={form.tipo||"OBBLIGATORIO"} onChange={e=>set("tipo",e.target.value)}><option value="OBBLIGATORIO">Obbligatorio</option><option value="FACOLTATIVO">Facoltativo</option><option value="AGGIORNAMENTO">Aggiornamento</option></select></div>
            <div className="form-group"><label>Azienda</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Durata (ore)</label><input type="number" min={1} value={form.durata_ore||8} onChange={e=>set("durata_ore",e.target.value)}/></div>
            <div className="form-group"><label>Validità (anni)</label><input type="number" min={1} value={form.validita_anni||3} onChange={e=>set("validita_anni",e.target.value)}/></div>
            <div className="form-group full"><label>Provider</label><input placeholder="Ente erogatore" value={form.provider||""} onChange={e=>set("provider",e.target.value)}/></div>
          </div>
        )}
        {view==="attendance" && (
          <div className="form-grid">
            <div className="form-group"><label>Lavoratore *</label><select value={form.worker_id||""} onChange={e=>set("worker_id",e.target.value)}><option value="">— Seleziona —</option>{data.workers.map(w=><option key={w.id} value={w.id}>{w.cognome} {w.nome}</option>)}</select></div>
            <div className="form-group"><label>Azienda</label><select value={form.company_id||""} onChange={e=>set("company_id",e.target.value)}><option value="">— Seleziona —</option>{data.companies.map(c=><option key={c.id} value={c.id}>{c.ragione_sociale}</option>)}</select></div>
            <div className="form-group"><label>Tipo</label><select value={form.tipo||"ENTRATA"} onChange={e=>set("tipo",e.target.value)}><option value="ENTRATA">Entrata</option><option value="USCITA">Uscita</option><option value="PAUSA_INIZIO">Pausa Inizio</option><option value="PAUSA_FINE">Pausa Fine</option></select></div>
            <div className="form-group"><label>Metodo</label><select value={form.metodo||"MANUALE"} onChange={e=>set("metodo",e.target.value)}><option value="MANUALE">Manuale</option><option value="GPS">GPS</option><option value="NFC">NFC</option><option value="QR_CODE">QR Code</option></select></div>
            <div className="form-group"><label>Data e Ora *</label><input type="datetime-local" value={form.timestamp||""} onChange={e=>set("timestamp",new Date(e.target.value).toISOString())}/></div>
            <div className="form-group full"><label>Note</label><input placeholder="Motivazione timbratura manuale..." value={form.note||""} onChange={e=>set("note",e.target.value)}/></div>
          </div>
        )}
        {error && <div style={{color:"#ff4d4f",fontSize:"0.8rem",marginBottom:"0.5rem",padding:"0.5rem",background:"#ff4d4f11",borderRadius:"6px"}}>{error}</div>}
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Annulla</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}><Icon d={Icons.check} size={14} color="white"/>{saving?"Salvataggio...":"Salva"}</button>
        </div>
      </div>
    </div>
  );
}

// ─── Login Screen ────────────────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState(null);
  const [loading, setLoading]   = useState(false);
  const handleSubmit = async () => {
    if (!email || !password) { setError("Inserisci email e password"); return; }
    setLoading(true); setError(null);
    try {
      const res = await apiAuth.login(email, password);
      auth.setToken(res.access_token);
      onLogin();
    } catch(e) { setError(e.message); }
    finally { setLoading(false); }
  };
  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"#0f1117"}}>
      <div style={{background:"#1a1d27",padding:"2.5rem",borderRadius:"16px",width:"360px",border:"1px solid #2a2d3e"}}>
        <div style={{textAlign:"center",marginBottom:"2rem"}}>
          <div style={{fontSize:"2rem",fontWeight:"800",color:"#fff"}}>Engi<span style={{color:"#FF6B35"}}>Pro</span></div>
          <div style={{color:"#888",fontSize:"0.85rem",marginTop:"0.25rem"}}>Safety Platform</div>
        </div>
        {error && <div style={{background:"#ff4d4f22",border:"1px solid #ff4d4f",color:"#ff4d4f",padding:"0.75rem",borderRadius:"8px",marginBottom:"1rem",fontSize:"0.85rem"}}>{error}</div>}
        <div style={{marginBottom:"1rem"}}>
          <label style={{color:"#aaa",fontSize:"0.8rem",display:"block",marginBottom:"0.4rem"}}>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="admin@engipro.it" style={{width:"100%",background:"#0f1117",border:"1px solid #2a2d3e",borderRadius:"8px",padding:"0.65rem",color:"#fff",fontSize:"0.9rem",boxSizing:"border-box"}} />
        </div>
        <div style={{marginBottom:"1.5rem"}}>
          <label style={{color:"#aaa",fontSize:"0.8rem",display:"block",marginBottom:"0.4rem"}}>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} onKeyDown={e=>e.key==="Enter"&&handleSubmit()} placeholder="••••••••" style={{width:"100%",background:"#0f1117",border:"1px solid #2a2d3e",borderRadius:"8px",padding:"0.65rem",color:"#fff",fontSize:"0.9rem",boxSizing:"border-box"}} />
        </div>
        <button onClick={handleSubmit} disabled={loading} style={{width:"100%",background:"#FF6B35",color:"#fff",border:"none",borderRadius:"8px",padding:"0.75rem",fontSize:"0.95rem",fontWeight:"600",cursor:"pointer"}}>
          {loading ? "Accesso..." : "Accedi"}
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [loggedIn, setLoggedIn]     = useState(auth.isLoggedIn());
  const [currentUser, setCurrentUser] = useState(null);
  const [activeView, setActiveView] = useState("dashboard");
  const [showModal, setShowModal]   = useState(false);
  const [apiData, setApiData]       = useState({
    workers:[], companies:[], deadlines:[], documents:[],
    dpiItems:[], protocols:[], visits:[], courses:[], records:[],
  });
  const [loading, setLoading] = useState(false);
  const [refreshTick, setRefreshTick] = useState(0);
  const refresh = () => setRefreshTick(t => t+1);

  const loadData = useCallback(async () => {
    if (!auth.isLoggedIn()) return;
    setLoading(true);
    try {
      const norm = (r) => {
        if (!r || r.status === 'rejected') return [];
        const v = r.value;
        if (!v) return [];
        if (Array.isArray(v)) return v;
        if (v.items) return v.items;
        return [];
      };
      const [workers, companies, deadlines, documents, dpiItems, protocols, visits, courses, records] = await Promise.allSettled([
        apiWorkers.list(),
        apiCompanies.list(),
        apiDeadlines.list(),
        apiDocuments.list(),
        apiDPI.items(),
        apiMedical.protocols(),
        apiMedical.visits(),
        apiTraining.courses(),
        apiAttendance.records(),
      ]);
      setApiData({
        workers:    norm(workers),
        companies:  norm(companies),
        deadlines:  norm(deadlines),
        documents:  norm(documents),
        dpiItems:   norm(dpiItems),
        protocols:  norm(protocols),
        visits:     norm(visits),
        courses:    norm(courses),
        records:    norm(records),
      });

      // load current user info
      try {
        const me = await apiAuth.me();
        setCurrentUser(me);
      } catch(_) {}
    } catch(e) { console.error('Load error:', e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (loggedIn) loadData(); }, [loggedIn, loadData, refreshTick]);

  if (!loggedIn) return <LoginScreen onLogin={() => { setLoggedIn(true); }} />;

  const alertCount = apiData.deadlines.filter(d => {
    const s = d.stato || d.status || "";
    return s === "ALERT" || s === "EXPIRED";
  }).length;

  const navItems = [
    { id:"dashboard",  label:"Dashboard",  icon:Icons.dashboard,  section:"PRINCIPALE" },
    { id:"companies",  label:"Aziende",    icon:Icons.companies,  section:"GESTIONE" },
    { id:"workers",    label:"Lavoratori", icon:Icons.workers,    section:"GESTIONE" },
    { id:"deadlines",  label:"Scadenze",   icon:Icons.deadlines,  section:"GESTIONE", badge:alertCount },
    { id:"documents",  label:"Documenti",  icon:Icons.documents,  section:"GESTIONE" },
    { id:"dpi",        label:"DPI",        icon:Icons.dpi,        section:"GESTIONE" },
    { id:"medical",    label:"Medicina",   icon:Icons.medical,    section:"MODULI" },
    { id:"training",   label:"Formazione", icon:Icons.training,   section:"MODULI" },
    { id:"attendance", label:"Presenze",   icon:Icons.attendance, section:"MODULI" },
  ];
  const sections = [...new Set(navItems.map(n=>n.section))];
  const viewTitles = { dashboard:"Dashboard", companies:"Aziende", workers:"Lavoratori", deadlines:"Scadenze", documents:"Documenti", dpi:"DPI", medical:"Medicina del Lavoro", training:"Formazione", attendance:"Presenze" };

  const userInitials = currentUser?.full_name
    ? currentUser.full_name.split(" ").map(w=>w[0]).join("").slice(0,2).toUpperCase()
    : "–";
  const userName = currentUser?.full_name || currentUser?.email || "Utente";
  const userRole = currentUser?.role || "–";

  return (
    <>
      <style>{css}</style>
      <div className="app">
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-icon">E</div>
            <div><div className="logo-text">Engi<span>Pro</span></div><div className="logo-sub">Safety Platform</div></div>
          </div>
          <nav className="sidebar-nav">
            {sections.map(section=>(
              <div key={section} className="nav-section">
                <div className="nav-label">{section}</div>
                {navItems.filter(n=>n.section===section).map(item=>(
                  <div key={item.id} className={`nav-item ${activeView===item.id?"active":""}`} onClick={()=>setActiveView(item.id)}>
                    <Icon d={item.icon} size={16} color="currentColor"/>
                    {item.label}
                    {item.badge>0 && <span className="nav-badge">{item.badge}</span>}
                  </div>
                ))}
              </div>
            ))}
          </nav>
          <div className="sidebar-footer">
            <div className="user-card" onClick={() => { auth.setToken(null); setLoggedIn(false); }}>
              <div className="user-avatar">{userInitials}</div>
              <div>
                <div className="user-name">{userName}</div>
                <div className="user-role">{userRole} · <span style={{color:"var(--c-red)",fontSize:"10px"}}>Logout</span></div>
              </div>
            </div>
          </div>
        </aside>
        <main className="main">
          <header className="topbar">
            <div className="topbar-title">{viewTitles[activeView]}</div>
            {loading && <span style={{fontSize:"12px",color:"var(--c-muted)"}}>Caricamento...</span>}
            <div className="icon-btn" style={{position:"relative"}}><Icon d={Icons.bell} size={17} color="var(--c-muted)"/>{alertCount>0&&<span className="notif-dot"/>}</div>
          </header>
          <div className="content">
            {activeView==="dashboard"  && <DashboardView workers={apiData.workers} deadlines={apiData.deadlines} companies={apiData.companies} documents={apiData.documents} dpiItems={apiData.dpiItems}/>}
            {activeView==="workers"    && <WorkersView    workers={apiData.workers}    onAdd={()=>setShowModal(true)}/>}
            {activeView==="deadlines"  && <DeadlinesView  deadlines={apiData.deadlines} onAdd={()=>setShowModal(true)}/>}
            {activeView==="documents"  && <DocumentsView  documents={apiData.documents} onAdd={()=>setShowModal(true)}/>}
            {activeView==="dpi"        && <DPIView        dpiItems={apiData.dpiItems}  onAdd={()=>setShowModal(true)}/>}
            {activeView==="companies"  && <CompaniesView  companies={apiData.companies} onAdd={()=>setShowModal(true)}/>}
            {activeView==="medical"    && <MedicalView    visits={apiData.visits} protocols={apiData.protocols} onAdd={()=>setShowModal(true)}/>}
            {activeView==="training"   && <TrainingView   courses={apiData.courses}    onAdd={()=>setShowModal(true)}/>}
            {activeView==="attendance" && <AttendanceView records={apiData.records}    onAdd={()=>setShowModal(true)}/>}
          </div>
        </main>
      </div>
      {showModal && <AddModal view={activeView} onClose={()=>setShowModal(false)} onSaved={refresh} data={apiData}/>}
    </>
  );
}
