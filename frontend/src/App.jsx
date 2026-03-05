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
  @keyframes fadeIn { from{opacity:0} to{opacity:1} }
  @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
`;

const WORKERS = [
  { id:1, nome:"Marco Rossi",    ruolo:"Operaio",        azienda:"Edil SRL",     stato:"ATTIVO",   dpi:"Completo", scadenza_vm:"2026-08-15" },
  { id:2, nome:"Laura Bianchi",  ruolo:"Tecnico",        azienda:"SafeTech SPA", stato:"ATTIVO",   dpi:"Completo", scadenza_vm:"2026-03-20" },
  { id:3, nome:"Giuseppe Verdi", ruolo:"Elettricista",   azienda:"Edil SRL",     stato:"ATTIVO",   dpi:"Mancante", scadenza_vm:"2025-12-01" },
  { id:4, nome:"Anna Ferrari",   ruolo:"Amministrativa", azienda:"SafeTech SPA", stato:"INATTIVO", dpi:"Completo", scadenza_vm:"2027-01-10" },
  { id:5, nome:"Luca Marino",    ruolo:"Gruista",        azienda:"Costruzioni+", stato:"ATTIVO",   dpi:"Completo", scadenza_vm:"2026-06-30" },
];
const DEADLINES = [
  { id:1, tipo:"FORMAZIONE",  descrizione:"Corso Primo Soccorso",  lavoratore:"Marco Rossi",    data:"2026-03-10", priorita:"HIGH",   stato:"ALERT" },
  { id:2, tipo:"VISITA_MEDICA", descrizione:"Visita Periodica",    lavoratore:"Laura Bianchi",  data:"2026-03-20", priorita:"HIGH",   stato:"ALERT" },
  { id:3, tipo:"MANUTENZIONE",  descrizione:"Manutenzione Carrello",lavoratore:"—",             data:"2026-04-05", priorita:"MEDIUM", stato:"PENDING" },
  { id:4, tipo:"FORMAZIONE",  descrizione:"Aggiorn. Sicurezza",    lavoratore:"Giuseppe Verdi", data:"2026-04-15", priorita:"MEDIUM", stato:"PENDING" },
  { id:5, tipo:"VISITA_MEDICA", descrizione:"Visita Preventiva",   lavoratore:"Luca Marino",    data:"2026-06-30", priorita:"LOW",    stato:"PENDING" },
  { id:6, tipo:"FORMAZIONE",  descrizione:"Corso Antincendio",     lavoratore:"Anna Ferrari",   data:"2025-12-01", priorita:"HIGH",   stato:"EXPIRED" },
];
const COMPANIES = [
  { id:1, nome:"Edil SRL",     settore:"Edilizia",   lavoratori:24, stato:"ATTIVA",  piva:"01234567890" },
  { id:2, nome:"SafeTech SPA", settore:"Tecnologia", lavoratori:18, stato:"ATTIVA",  piva:"09876543210" },
  { id:3, nome:"Costruzioni+", settore:"Edilizia",   lavoratori:31, stato:"ATTIVA",  piva:"11223344556" },
  { id:4, nome:"LogiMove SRL", settore:"Logistica",  lavoratori:12, stato:"SOSPESA", piva:"66778899001" },
];
const DOCUMENTS = [
  { id:1, titolo:"DVR Edil SRL 2026",        categoria:"SICUREZZA",  azienda:"Edil SRL",      data:"2026-01-15", stato:"ACTIVE",  versione:3 },
  { id:2, titolo:"Attestato Primo Soccorso", categoria:"FORMAZIONE", azienda:"SafeTech SPA",  data:"2026-02-01", stato:"ACTIVE",  versione:1 },
  { id:3, titolo:"Contratto Collettivo",     categoria:"CONTRATTO",  azienda:"Costruzioni+",  data:"2025-10-10", stato:"EXPIRED", versione:2 },
  { id:4, titolo:"Scheda DPI Casco",         categoria:"DPI",        azienda:"Edil SRL",      data:"2026-03-01", stato:"ACTIVE",  versione:1 },
];
const DPI_ITEMS = [
  { id:1, codice:"DPI-001", nome:"Casco Protettivo 3M H700", categoria:"TESTA",       stato:"ASSIGNED",    lavoratore:"Marco Rossi",    scadenza:"2028-01-01" },
  { id:2, codice:"DPI-002", nome:"Otoprotettori Peltor",     categoria:"UDITO",       stato:"AVAILABLE",   lavoratore:"—",              scadenza:"2027-06-01" },
  { id:3, codice:"DPI-003", nome:"Guanti Antitaglio Lvl.5",  categoria:"MANI_BRACCIA",stato:"ASSIGNED",    lavoratore:"Giuseppe Verdi", scadenza:"2026-09-01" },
  { id:4, codice:"DPI-004", nome:"Scarpe Antinfort. S3",     categoria:"PIEDI_GAMBE", stato:"MAINTENANCE", lavoratore:"—",              scadenza:"2027-01-01" },
  { id:5, codice:"DPI-005", nome:"Imbracatura Anticaduta",   categoria:"ANTICADUTA",  stato:"ASSIGNED",    lavoratore:"Luca Marino",    scadenza:"2026-12-01" },
];
const MEDICAL_VISITS = [
  { id:1, lavoratore:"Marco Rossi",    tipo:"PERIODICA",       esito:"IDONEO",             data:"2026-01-15", prossima:"2027-01-15", medico:"Dr. Bianchi", stato:"COMPLETED" },
  { id:2, lavoratore:"Laura Bianchi",  tipo:"PERIODICA",       esito:null,                 data:"2026-03-20", prossima:null,         medico:"Dr. Bianchi", stato:"SCHEDULED" },
  { id:3, lavoratore:"Giuseppe Verdi", tipo:"PREVENTIVA",      esito:"IDONEO_LIMITAZIONI", data:"2025-11-10", prossima:"2026-05-10", medico:"Dr. Rossi",   stato:"COMPLETED" },
  { id:4, lavoratore:"Luca Marino",    tipo:"CAMBIO_MANSIONE", esito:"IDONEO",             data:"2026-02-05", prossima:"2027-02-05", medico:"Dr. Bianchi", stato:"COMPLETED" },
  { id:5, lavoratore:"Anna Ferrari",   tipo:"CESSAZIONE",      esito:"IDONEO",             data:"2026-01-31", prossima:null,         medico:"Dr. Verdi",   stato:"COMPLETED" },
];
const PROTOCOLS = [
  { id:1, azienda:"Edil SRL",     titolo:"Protocollo Sanitario 2026", medico:"Dr. Bianchi", approvazione:"2026-01-10" },
  { id:2, azienda:"SafeTech SPA", titolo:"Protocollo Sanitario 2026", medico:"Dr. Rossi",   approvazione:"2026-01-15" },
  { id:3, azienda:"Costruzioni+", titolo:"Protocollo Sanitario 2026", medico:"Dr. Verdi",   approvazione:"2026-02-01" },
];
const COURSES = [
  { id:1, codice:"FOR-001", titolo:"Corso Primo Soccorso",      durata:16, tipo:"OBBLIGATORIO", provider:"Croce Rossa",  edizioni:3 },
  { id:2, codice:"FOR-002", titolo:"Antincendio Rischio Medio", durata:8,  tipo:"OBBLIGATORIO", provider:"Vigili Fuoco", edizioni:2 },
  { id:3, codice:"FOR-003", titolo:"Sicurezza sul Lavoro Base", durata:8,  tipo:"OBBLIGATORIO", provider:"Interno",      edizioni:5 },
  { id:4, codice:"FOR-004", titolo:"Uso Carrelli Elevatori",    durata:12, tipo:"OBBLIGATORIO", provider:"INAIL",        edizioni:1 },
  { id:5, codice:"FOR-005", titolo:"Lavori in Quota",           durata:8,  tipo:"OBBLIGATORIO", provider:"Interno",      edizioni:2 },
];
const PARTICIPATIONS = [
  { id:1, lavoratore:"Marco Rossi",    corso:"Corso Primo Soccorso",      data:"2025-09-10", esito:"SUPERATO",     scadenza:"2028-09-10" },
  { id:2, lavoratore:"Laura Bianchi",  corso:"Antincendio Rischio Medio", data:"2025-10-05", esito:"SUPERATO",     scadenza:"2028-10-05" },
  { id:3, lavoratore:"Giuseppe Verdi", corso:"Sicurezza sul Lavoro Base", data:"2025-11-20", esito:"NON_SUPERATO", scadenza:null },
  { id:4, lavoratore:"Luca Marino",    corso:"Uso Carrelli Elevatori",    data:"2026-01-15", esito:"SUPERATO",     scadenza:"2031-01-15" },
  { id:5, lavoratore:"Anna Ferrari",   corso:"Sicurezza sul Lavoro Base", data:"2025-11-20", esito:"SUPERATO",     scadenza:"2028-11-20" },
];
const TIMBRATURE = [
  { id:1, lavoratore:"Marco Rossi",    tipo:"ENTRATA", timestamp:"2026-03-04 07:58", metodo:"GPS",    lat:"45.4654", lng:"9.1859", valida:true },
  { id:2, lavoratore:"Marco Rossi",    tipo:"USCITA",  timestamp:"2026-03-04 17:05", metodo:"GPS",    lat:"45.4654", lng:"9.1859", valida:true },
  { id:3, lavoratore:"Laura Bianchi",  tipo:"ENTRATA", timestamp:"2026-03-04 08:45", metodo:"NFC",    lat:null,      lng:null,     valida:true },
  { id:4, lavoratore:"Giuseppe Verdi", tipo:"ENTRATA", timestamp:"2026-03-04 09:15", metodo:"MANUALE",lat:null,      lng:null,     valida:true },
  { id:5, lavoratore:"Luca Marino",    tipo:"ENTRATA", timestamp:"2026-03-04 07:30", metodo:"GPS",    lat:"45.4721", lng:"9.1934", valida:true },
  { id:6, lavoratore:"Luca Marino",    tipo:"USCITA",  timestamp:"2026-03-04 18:30", metodo:"GPS",    lat:"45.4721", lng:"9.1934", valida:true },
];
const ATTENDANCE_RECORDS = [
  { id:1, lavoratore:"Marco Rossi",    data:"2026-03-04", stato:"PRESENT", entrata:"07:58", uscita:"17:05", ore:9.1,  straord:1.1, approvato:true },
  { id:2, lavoratore:"Laura Bianchi",  data:"2026-03-04", stato:"PRESENT", entrata:"08:45", uscita:"—",     ore:null, straord:0,   approvato:false },
  { id:3, lavoratore:"Giuseppe Verdi", data:"2026-03-04", stato:"LATE",    entrata:"09:15", uscita:"—",     ore:null, straord:0,   approvato:false },
  { id:4, lavoratore:"Luca Marino",    data:"2026-03-04", stato:"PRESENT", entrata:"07:30", uscita:"18:30", ore:11.0, straord:3.0, approvato:true },
  { id:5, lavoratore:"Anna Ferrari",   data:"2026-03-04", stato:"ABSENT",  entrata:"—",     uscita:"—",     ore:0,    straord:0,   approvato:false },
];

const avatarColor = (name) => {
  const colors = ["#FF6B35","#8B5CF6","#00D4AA","#4CC9F0","#FFD166","#FF4D6D"];
  let h = 0; for (const c of name) h = c.charCodeAt(0) + ((h<<5)-h);
  return colors[Math.abs(h) % colors.length];
};
const initials = (name) => name.split(" ").map(w=>w[0]).join("").slice(0,2).toUpperCase();
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
    <div className="progress-fill" style={{width:`${(val/max)*100}%`, background:color}} />
  </div>
);

function DashboardView() {
  const alertCount = DEADLINES.filter(d=>d.stato==="ALERT"||d.stato==="EXPIRED").length;
  const activeWorkers = WORKERS.filter(w=>w.stato==="ATTIVO").length;
  const chartData = [
    {m:"Gen",val:65},{m:"Feb",val:78},{m:"Mar",val:52},{m:"Apr",val:90},
    {m:"Mag",val:85},{m:"Giu",val:73},{m:"Lug",val:88},{m:"Ago",val:61},
  ];
  const maxVal = Math.max(...chartData.map(d=>d.val));
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Dashboard</div><div className="section-sub">Panoramica sicurezza — Marzo 2026</div></div>
        <button className="btn btn-primary"><Icon d={Icons.plus} size={15} color="white"/> Nuova Scadenza</button>
      </div>
      <div className="kpi-grid">
        <KPICard label="Lavoratori Attivi"    value={activeWorkers}      trend={12}  trendLabel="vs mese"     accent="var(--c-teal)" />
        <KPICard label="Scadenze Critiche"    value={alertCount}         trend={-8}  trendLabel="vs mese"     accent="var(--c-red)" />
        <KPICard label="Aziende Gestite"      value={COMPANIES.length}   trend={25}  trendLabel="trimestre"   accent="var(--c-purple)" />
        <KPICard label="Documenti Archiviati" value={48}                 trend={5}   trendLabel="vs mese"     accent="var(--c-yellow)" />
      </div>
      <div className="grid-3">
        <div className="card">
          <div className="card-title">Conformità Mensile</div>
          <div className="chart-bars">
            {chartData.map((d,i)=>(
              <div key={i} className="chart-bar-wrap">
                <div className="chart-bar" style={{height:`${(d.val/maxVal)*100}%`, background: d.val>80?"linear-gradient(180deg,var(--c-teal),rgba(0,212,170,0.3))":d.val>65?"linear-gradient(180deg,var(--c-orange),rgba(255,107,53,0.3))":"linear-gradient(180deg,var(--c-red),rgba(255,77,109,0.3))"}} />
              </div>
            ))}
          </div>
          <div className="chart-months">{chartData.map((d,i)=><span key={i} className="chart-month-label">{d.m}</span>)}</div>
        </div>
        <div className="card">
          <div className="card-title">Stato DPI</div>
          <div style={{display:"flex",flexDirection:"column",gap:"10px",marginTop:"4px"}}>
            {[{label:"Assegnati",val:3,max:5,color:"var(--c-blue)"},{label:"Disponibili",val:1,max:5,color:"var(--c-green)"},{label:"Manutenzione",val:1,max:5,color:"var(--c-yellow)"}].map((r,i)=>(
              <div key={i}>
                <div style={{display:"flex",justifyContent:"space-between",marginBottom:"4px"}}>
                  <span style={{fontSize:"12px",color:"var(--c-muted)"}}>{r.label}</span>
                  <span style={{fontSize:"12px",fontWeight:"700"}}>{r.val}</span>
                </div>
                <MiniBar val={r.val} max={r.max} color={r.color} />
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">⚠ Scadenze Urgenti</div>
          {DEADLINES.filter(d=>d.stato==="ALERT"||d.stato==="EXPIRED").map(d=>(
            <div key={d.id} className="alert-item">
              <div className="alert-dot" style={{background:d.stato==="EXPIRED"?"var(--c-red)":"var(--c-yellow)"}} />
              <div><div className="alert-text">{d.descrizione}</div><div className="alert-sub">{d.lavoratore} · {d.data} · <Badge text={d.stato}/></div></div>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="card-title">Attività Recenti</div>
          <div className="timeline">
            {[
              {text:"DVR Edil SRL aggiornato",meta:"2h fa",color:""},
              {text:"Visita medica completata — M. Rossi",meta:"Ieri",color:"green"},
              {text:"DPI mancante segnalato — G. Verdi",meta:"2 gg fa",color:"red"},
              {text:"Corso Antincendio scaduto",meta:"3 gg fa",color:"red"},
              {text:"Nuovo lavoratore registrato",meta:"4 gg fa",color:"green"},
            ].map((item,i)=>(
              <div key={i} className="timeline-item">
                <div className={`timeline-dot ${item.color}`} />
                <div className="timeline-content">{item.text}</div>
                <div className="timeline-meta">{item.meta}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function WorkersView({ onAdd }) {
  const [search, setSearch] = useState("");
  const filtered = WORKERS.filter(w=>w.nome.toLowerCase().includes(search.toLowerCase())||w.azienda.toLowerCase().includes(search.toLowerCase()));
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Lavoratori</div><div className="section-sub">{WORKERS.length} lavoratori registrati</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuovo</button>
      </div>
      <div className="card">
        <div style={{marginBottom:"16px"}}>
          <div className="search-box" style={{width:"100%"}}>
            <Icon d={Icons.search} size={15} color="var(--c-muted)"/>
            <input placeholder="Cerca lavoratore o azienda..." value={search} onChange={e=>setSearch(e.target.value)}/>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Lavoratore</th><th>Ruolo</th><th>Azienda</th><th>Stato</th><th>DPI</th><th>Scad. VM</th></tr></thead>
            <tbody>
              {filtered.map(w=>(
                <tr key={w.id}>
                  <td><div style={{display:"flex",alignItems:"center",gap:"10px"}}><div className="avatar" style={{background:avatarColor(w.nome)}}>{initials(w.nome)}</div><span style={{fontWeight:600}}>{w.nome}</span></div></td>
                  <td style={{color:"var(--c-muted)"}}>{w.ruolo}</td>
                  <td>{w.azienda}</td>
                  <td><Badge text={w.stato}/></td>
                  <td><Badge text={w.dpi==="Completo"?"ACTIVE":"ALERT"}/></td>
                  <td style={{color:new Date(w.scadenza_vm)<new Date()?"var(--c-red)":"var(--c-text)"}}>{w.scadenza_vm}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DeadlinesView({ onAdd }) {
  const [filter, setFilter] = useState("ALL");
  const filters = ["ALL","ALERT","PENDING","EXPIRED","COMPLETED"];
  const filtered = filter==="ALL" ? DEADLINES : DEADLINES.filter(d=>d.stato===filter);
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
        <div className="table-wrap">
          <table>
            <thead><tr><th>Tipo</th><th>Descrizione</th><th>Lavoratore</th><th>Data</th><th>Priorità</th><th>Stato</th></tr></thead>
            <tbody>
              {filtered.map(d=>(
                <tr key={d.id}>
                  <td><span style={{fontSize:"11px",color:"var(--c-muted)",fontWeight:700}}>{d.tipo}</span></td>
                  <td style={{fontWeight:600}}>{d.descrizione}</td>
                  <td>{d.lavoratore}</td>
                  <td style={{color:new Date(d.data)<new Date()?"var(--c-red)":"var(--c-text)"}}>{d.data}</td>
                  <td><Badge text={d.priorita}/></td>
                  <td><Badge text={d.stato}/></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DocumentsView({ onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Documenti</div><div className="section-sub">{DOCUMENTS.length} documenti archiviati</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Carica</button>
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Titolo</th><th>Categoria</th><th>Azienda</th><th>Data</th><th>Ver.</th><th>Stato</th></tr></thead>
            <tbody>
              {DOCUMENTS.map(d=>(
                <tr key={d.id}>
                  <td><div style={{display:"flex",alignItems:"center",gap:"8px"}}><Icon d={Icons.documents} size={15} color="var(--c-muted)"/><span style={{fontWeight:600}}>{d.titolo}</span></div></td>
                  <td><Badge text={d.categoria}/></td>
                  <td>{d.azienda}</td>
                  <td>{d.data}</td>
                  <td style={{color:"var(--c-muted)"}}>v{d.versione}</td>
                  <td><Badge text={d.stato}/></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DPIView({ onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">DPI</div><div className="section-sub">Dispositivi di Protezione Individuale</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuovo DPI</button>
      </div>
      <div className="kpi-grid" style={{gridTemplateColumns:"repeat(3,1fr)"}}>
        {[{label:"Totale DPI",val:DPI_ITEMS.length,color:"var(--c-blue)"},{label:"Assegnati",val:DPI_ITEMS.filter(d=>d.stato==="ASSIGNED").length,color:"var(--c-orange)"},{label:"Manutenzione",val:DPI_ITEMS.filter(d=>d.stato==="MAINTENANCE").length,color:"var(--c-yellow)"}].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color}}>{k.val}</div></div>
        ))}
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Codice</th><th>Nome</th><th>Categoria</th><th>Stato</th><th>Assegnato a</th><th>Scadenza</th></tr></thead>
            <tbody>
              {DPI_ITEMS.map(d=>(
                <tr key={d.id}>
                  <td style={{fontFamily:"monospace",color:"var(--c-orange)",fontSize:"12px"}}>{d.codice}</td>
                  <td style={{fontWeight:600}}>{d.nome}</td>
                  <td><span style={{fontSize:"11px",color:"var(--c-muted)"}}>{d.categoria}</span></td>
                  <td><Badge text={d.stato}/></td>
                  <td>{d.lavoratore}</td>
                  <td style={{color:new Date(d.scadenza)<new Date()?"var(--c-red)":"var(--c-text)"}}>{d.scadenza}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function CompaniesView({ onAdd }) {
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Aziende</div><div className="section-sub">{COMPANIES.length} aziende clienti</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuova Azienda</button>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:"16px"}}>
        {COMPANIES.map(c=>(
          <div key={c.id} className="card" style={{cursor:"pointer"}}>
            <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",marginBottom:"14px"}}>
              <div style={{display:"flex",alignItems:"center",gap:"12px"}}>
                <div className="avatar" style={{width:44,height:44,fontSize:16,background:avatarColor(c.nome),borderRadius:"12px"}}>{initials(c.nome)}</div>
                <div><div style={{fontFamily:"var(--font-head)",fontWeight:800,fontSize:"16px"}}>{c.nome}</div><div style={{fontSize:"12px",color:"var(--c-muted)"}}>{c.settore}</div></div>
              </div>
              <Badge text={c.stato}/>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"10px"}}>
              <div style={{background:"var(--c-surface2)",borderRadius:"8px",padding:"10px"}}><div style={{fontSize:"11px",color:"var(--c-muted)",marginBottom:"4px"}}>Lavoratori</div><div style={{fontFamily:"var(--font-head)",fontSize:"22px",fontWeight:800,color:"var(--c-teal)"}}>{c.lavoratori}</div></div>
              <div style={{background:"var(--c-surface2)",borderRadius:"8px",padding:"10px"}}><div style={{fontSize:"11px",color:"var(--c-muted)",marginBottom:"4px"}}>P.IVA</div><div style={{fontFamily:"monospace",fontSize:"12px",color:"var(--c-muted)"}}>{c.piva}</div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MedicalView({ onAdd }) {
  const [tab, setTab] = useState("visite");
  const idonei    = MEDICAL_VISITS.filter(v=>v.esito==="IDONEO").length;
  const limitati  = MEDICAL_VISITS.filter(v=>v.esito==="IDONEO_LIMITAZIONI").length;
  const scheduled = MEDICAL_VISITS.filter(v=>v.stato==="SCHEDULED").length;
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Medicina del Lavoro</div><div className="section-sub">Protocolli sanitari e visite mediche D.Lgs.81/08</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuova Visita</button>
      </div>
      <div className="kpi-grid">
        {[{label:"Visite Totali",val:MEDICAL_VISITS.length,color:"var(--c-blue)"},{label:"Idonei",val:idonei,color:"var(--c-green)"},{label:"Con Limitazioni",val:limitati,color:"var(--c-yellow)"},{label:"Da Effettuare",val:scheduled,color:"var(--c-orange)"}].map((k,i)=>(
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
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lavoratore</th><th>Tipo</th><th>Medico</th><th>Data</th><th>Prossima</th><th>Esito</th><th>Stato</th></tr></thead>
              <tbody>
                {MEDICAL_VISITS.map(v=>(
                  <tr key={v.id}>
                    <td><div style={{display:"flex",alignItems:"center",gap:"8px"}}><div className="avatar" style={{background:avatarColor(v.lavoratore)}}>{initials(v.lavoratore)}</div><span style={{fontWeight:600}}>{v.lavoratore}</span></div></td>
                    <td><span style={{fontSize:"11px",color:"var(--c-muted)",fontWeight:700}}>{v.tipo}</span></td>
                    <td style={{color:"var(--c-muted)"}}>{v.medico}</td>
                    <td>{v.data}</td>
                    <td style={{color:v.prossima&&new Date(v.prossima)<new Date()?"var(--c-red)":"var(--c-text)"}}>{v.prossima||"—"}</td>
                    <td>{v.esito?<Badge text={v.esito}/>:<span style={{color:"var(--c-muted)"}}>—</span>}</td>
                    <td><Badge text={v.stato}/></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {tab==="protocolli" && (
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:"16px"}}>
          {PROTOCOLS.map(p=>(
            <div key={p.id} className="card">
              <div style={{display:"flex",alignItems:"center",gap:"10px",marginBottom:"14px"}}>
                <div style={{width:40,height:40,borderRadius:"10px",background:"linear-gradient(135deg,var(--c-teal),var(--c-blue))",display:"flex",alignItems:"center",justifyContent:"center"}}><Icon d={Icons.medical} size={18} color="white"/></div>
                <div><div style={{fontWeight:700,fontSize:"14px"}}>{p.azienda}</div><div style={{fontSize:"11px",color:"var(--c-muted)"}}>Approv. {p.approvazione}</div></div>
              </div>
              <div style={{fontSize:"13px",fontWeight:600,marginBottom:"6px"}}>{p.titolo}</div>
              <div style={{fontSize:"12px",color:"var(--c-muted)"}}>👨‍⚕️ {p.medico}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TrainingView({ onAdd }) {
  const [tab, setTab] = useState("corsi");
  const superati    = PARTICIPATIONS.filter(p=>p.esito==="SUPERATO").length;
  const nonSuperati = PARTICIPATIONS.filter(p=>p.esito==="NON_SUPERATO").length;
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Formazione</div><div className="section-sub">Gestione corsi, edizioni e attestati</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Nuovo Corso</button>
      </div>
      <div className="kpi-grid">
        {[{label:"Corsi Attivi",val:COURSES.length,color:"var(--c-purple)"},{label:"Partecipazioni",val:PARTICIPATIONS.length,color:"var(--c-blue)"},{label:"Attestati OK",val:superati,color:"var(--c-green)"},{label:"Non Superati",val:nonSuperati,color:"var(--c-red)"}].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color,fontSize:"32px"}}>{k.val}</div></div>
        ))}
      </div>
      <div style={{display:"flex",gap:"8px",marginBottom:"16px"}}>
        {["corsi","attestati"].map(t=>(
          <button key={t} className="btn" onClick={()=>setTab(t)} style={{background:tab===t?"var(--c-orange)":"var(--c-surface2)",color:tab===t?"white":"var(--c-muted)",border:`1px solid ${tab===t?"var(--c-orange)":"var(--c-border)"}`}}>{t==="corsi"?"Catalogo Corsi":"Attestati Lavoratori"}</button>
        ))}
      </div>
      {tab==="corsi" && (
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"16px"}}>
          {COURSES.map(c=>(
            <div key={c.id} className="card" style={{cursor:"pointer"}}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:"12px"}}>
                <div style={{fontFamily:"monospace",fontSize:"11px",color:"var(--c-orange)",fontWeight:700}}>{c.codice}</div>
                <Badge text={c.tipo}/>
              </div>
              <div style={{fontFamily:"var(--font-head)",fontWeight:800,fontSize:"15px",marginBottom:"8px"}}>{c.titolo}</div>
              <div style={{display:"flex",gap:"16px",fontSize:"12px",color:"var(--c-muted)"}}><span>⏱ {c.durata}h</span><span>🏫 {c.provider}</span><span>📅 {c.edizioni} edizioni</span></div>
              <div className="progress-bar" style={{marginTop:"12px"}}><div className="progress-fill" style={{width:`${(c.edizioni/5)*100}%`,background:"linear-gradient(90deg,var(--c-purple),var(--c-blue))"}}/></div>
            </div>
          ))}
        </div>
      )}
      {tab==="attestati" && (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lavoratore</th><th>Corso</th><th>Data</th><th>Esito</th><th>Scadenza Attestato</th></tr></thead>
              <tbody>
                {PARTICIPATIONS.map(p=>(
                  <tr key={p.id}>
                    <td><div style={{display:"flex",alignItems:"center",gap:"8px"}}><div className="avatar" style={{background:avatarColor(p.lavoratore)}}>{initials(p.lavoratore)}</div><span style={{fontWeight:600}}>{p.lavoratore}</span></div></td>
                    <td>{p.corso}</td>
                    <td>{p.data}</td>
                    <td><Badge text={p.esito}/></td>
                    <td style={{color:p.scadenza&&new Date(p.scadenza)<new Date()?"var(--c-red)":"var(--c-text)"}}>{p.scadenza||"—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function AttendanceView({ onAdd }) {
  const [tab, setTab] = useState("oggi");
  const presenti = ATTENDANCE_RECORDS.filter(r=>r.stato==="PRESENT").length;
  const assenti  = ATTENDANCE_RECORDS.filter(r=>r.stato==="ABSENT").length;
  const ritardi  = ATTENDANCE_RECORDS.filter(r=>r.stato==="LATE").length;
  const straord  = ATTENDANCE_RECORDS.reduce((acc,r)=>acc+(r.straord||0),0);
  const metodoBadge = (m) => ({GPS:"green",NFC:"blue",MANUALE:"yellow",QR_CODE:"purple"}[m]||"blue");
  return (
    <div>
      <div className="section-header">
        <div><div className="section-title">Presenze</div><div className="section-sub">Timbrature GPS e registro presenze giornaliero</div></div>
        <button className="btn btn-primary" onClick={onAdd}><Icon d={Icons.plus} size={15} color="white"/>Timbratura Manuale</button>
      </div>
      <div className="kpi-grid">
        {[{label:"Presenti Oggi",val:presenti,color:"var(--c-green)"},{label:"Assenti",val:assenti,color:"var(--c-red)"},{label:"Ritardi",val:ritardi,color:"var(--c-yellow)"},{label:"Ore Straordinario",val:`${straord.toFixed(1)}h`,color:"var(--c-orange)"}].map((k,i)=>(
          <div key={i} className="kpi-card" style={{"--accent":k.color}}><div className="kpi-glow"/><div className="kpi-label">{k.label}</div><div className="kpi-value" style={{color:k.color,fontSize:"32px"}}>{k.val}</div></div>
        ))}
      </div>
      <div style={{display:"flex",gap:"8px",marginBottom:"16px"}}>
        {["oggi","timbrature"].map(t=>(
          <button key={t} className="btn" onClick={()=>setTab(t)} style={{background:tab===t?"var(--c-orange)":"var(--c-surface2)",color:tab===t?"white":"var(--c-muted)",border:`1px solid ${tab===t?"var(--c-orange)":"var(--c-border)"}`}}>{t==="oggi"?"Registro Oggi":"Timbrature GPS"}</button>
        ))}
      </div>
      {tab==="oggi" && (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lavoratore</th><th>Data</th><th>Stato</th><th>Entrata</th><th>Uscita</th><th>Ore Lav.</th><th>Straord.</th><th>Approvato</th></tr></thead>
              <tbody>
                {ATTENDANCE_RECORDS.map(r=>(
                  <tr key={r.id}>
                    <td><div style={{display:"flex",alignItems:"center",gap:"8px"}}><div className="avatar" style={{background:avatarColor(r.lavoratore)}}>{initials(r.lavoratore)}</div><span style={{fontWeight:600}}>{r.lavoratore}</span></div></td>
                    <td style={{color:"var(--c-muted)"}}>{r.data}</td>
                    <td><Badge text={r.stato}/></td>
                    <td style={{fontFamily:"monospace",color:"var(--c-teal)",fontWeight:700}}>{r.entrata}</td>
                    <td style={{fontFamily:"monospace",color:r.uscita==="—"?"var(--c-muted)":"var(--c-orange)",fontWeight:700}}>{r.uscita}</td>
                    <td style={{fontWeight:700}}>{r.ore?`${r.ore}h`:"—"}</td>
                    <td style={{color:r.straord>0?"var(--c-yellow)":"var(--c-muted)"}}>{r.straord>0?`+${r.straord}h`:"—"}</td>
                    <td>{r.approvato?<span style={{color:"var(--c-green)",fontWeight:700}}>✓</span>:<span style={{color:"var(--c-muted)"}}>Pending</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {tab==="timbrature" && (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Lavoratore</th><th>Tipo</th><th>Timestamp</th><th>Metodo</th><th>Coordinate</th><th>Valida</th></tr></thead>
              <tbody>
                {TIMBRATURE.map(t=>(
                  <tr key={t.id}>
                    <td><div style={{display:"flex",alignItems:"center",gap:"8px"}}><div className="avatar" style={{background:avatarColor(t.lavoratore)}}>{initials(t.lavoratore)}</div><span style={{fontWeight:600}}>{t.lavoratore}</span></div></td>
                    <td><span style={{fontWeight:700,fontSize:"12px",color:t.tipo==="ENTRATA"?"var(--c-green)":"var(--c-orange)"}}>{t.tipo==="ENTRATA"?"↗ ENTRATA":"↙ USCITA"}</span></td>
                    <td style={{fontFamily:"monospace",fontSize:"12px"}}>{t.timestamp}</td>
                    <td><span className={`badge badge-${metodoBadge(t.metodo)}`}>{t.metodo}</span></td>
                    <td style={{fontFamily:"monospace",fontSize:"11px",color:"var(--c-muted)"}}>{t.lat?`${t.lat}, ${t.lng}`:"—"}</td>
                    <td>{t.valida?<span style={{color:"var(--c-green)",fontWeight:700}}>✓</span>:<span style={{color:"var(--c-red)",fontWeight:700}}>✗</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function AddModal({ view, onClose }) {
  const titles = { workers:"Nuovo Lavoratore", deadlines:"Nuova Scadenza", documents:"Carica Documento", dpi:"Nuovo DPI", companies:"Nuova Azienda", medical:"Nuova Visita", training:"Nuovo Corso", attendance:"Timbratura Manuale" };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e=>e.stopPropagation()}>
        <div className="modal-title">{titles[view]||"Nuovo"}</div>
        {view==="workers" && (
          <div className="form-grid">
            <div className="form-group"><label>Nome</label><input placeholder="Mario"/></div>
            <div className="form-group"><label>Cognome</label><input placeholder="Rossi"/></div>
            <div className="form-group"><label>Ruolo</label><input placeholder="Operaio"/></div>
            <div className="form-group"><label>Azienda</label><select>{COMPANIES.map(c=><option key={c.id}>{c.nome}</option>)}</select></div>
            <div className="form-group"><label>Codice Fiscale</label><input placeholder="RSSMRA80A01H501Z"/></div>
            <div className="form-group"><label>Data Assunzione</label><input type="date"/></div>
          </div>
        )}
        {view==="deadlines" && (
          <div className="form-grid">
            <div className="form-group"><label>Tipo</label><select><option>FORMAZIONE</option><option>VISITA_MEDICA</option><option>MANUTENZIONE</option></select></div>
            <div className="form-group"><label>Priorità</label><select><option>LOW</option><option>MEDIUM</option><option>HIGH</option></select></div>
            <div className="form-group full"><label>Descrizione</label><input placeholder="Descrizione scadenza..."/></div>
            <div className="form-group"><label>Lavoratore</label><select><option>—</option>{WORKERS.map(w=><option key={w.id}>{w.nome}</option>)}</select></div>
            <div className="form-group"><label>Data Scadenza</label><input type="date"/></div>
          </div>
        )}
        {view==="documents" && (
          <div className="form-grid">
            <div className="form-group full"><label>Titolo</label><input placeholder="Titolo documento"/></div>
            <div className="form-group"><label>Categoria</label><select><option>SICUREZZA</option><option>FORMAZIONE</option><option>MEDICINA</option><option>CONTRATTO</option><option>DPI</option></select></div>
            <div className="form-group"><label>Azienda</label><select>{COMPANIES.map(c=><option key={c.id}>{c.nome}</option>)}</select></div>
            <div className="form-group"><label>Data Emissione</label><input type="date"/></div>
            <div className="form-group"><label>Data Scadenza</label><input type="date"/></div>
          </div>
        )}
        {view==="dpi" && (
          <div className="form-grid">
            <div className="form-group"><label>Codice</label><input placeholder="DPI-006"/></div>
            <div className="form-group"><label>Nome</label><input placeholder="Nome dispositivo"/></div>
            <div className="form-group"><label>Categoria</label><select><option>TESTA</option><option>OCCHI_VISO</option><option>UDITO</option><option>MANI_BRACCIA</option><option>PIEDI_GAMBE</option><option>ANTICADUTA</option></select></div>
            <div className="form-group"><label>Marca</label><input placeholder="3M, Honeywell..."/></div>
            <div className="form-group"><label>Data Acquisto</label><input type="date"/></div>
            <div className="form-group"><label>Data Scadenza</label><input type="date"/></div>
          </div>
        )}
        {view==="companies" && (
          <div className="form-grid">
            <div className="form-group full"><label>Ragione Sociale</label><input placeholder="Nome Azienda SRL"/></div>
            <div className="form-group"><label>P.IVA</label><input placeholder="01234567890"/></div>
            <div className="form-group"><label>Settore</label><input placeholder="Edilizia, Logistica..."/></div>
            <div className="form-group"><label>Email</label><input type="email" placeholder="info@azienda.it"/></div>
            <div className="form-group"><label>Telefono</label><input placeholder="+39 02 1234567"/></div>
            <div className="form-group"><label>Città</label><input placeholder="Milano"/></div>
          </div>
        )}
        {view==="medical" && (
          <div className="form-grid">
            <div className="form-group"><label>Lavoratore</label><select>{WORKERS.map(w=><option key={w.id}>{w.nome}</option>)}</select></div>
            <div className="form-group"><label>Tipo Visita</label><select><option>PREVENTIVA</option><option>PERIODICA</option><option>REINTEGRO</option><option>CAMBIO_MANSIONE</option><option>CESSAZIONE</option></select></div>
            <div className="form-group"><label>Data Visita</label><input type="date"/></div>
            <div className="form-group"><label>Medico</label><input placeholder="Dr. Bianchi"/></div>
            <div className="form-group"><label>Struttura</label><input placeholder="Nome clinica/studio"/></div>
            <div className="form-group"><label>Prossima Visita</label><input type="date"/></div>
            <div className="form-group full"><label>Note</label><textarea rows={2} placeholder="Note aggiuntive..."/></div>
          </div>
        )}
        {view==="training" && (
          <div className="form-grid">
            <div className="form-group"><label>Codice</label><input placeholder="FOR-006"/></div>
            <div className="form-group"><label>Titolo</label><input placeholder="Nome corso"/></div>
            <div className="form-group"><label>Tipo</label><select><option>OBBLIGATORIO</option><option>FACOLTATIVO</option><option>AGGIORNAMENTO</option></select></div>
            <div className="form-group"><label>Durata (ore)</label><input type="number" defaultValue={8} min={1}/></div>
            <div className="form-group"><label>Provider</label><input placeholder="Ente erogatore"/></div>
            <div className="form-group"><label>Validità (anni)</label><input type="number" defaultValue={3} min={1}/></div>
          </div>
        )}
        {view==="attendance" && (
          <div className="form-grid">
            <div className="form-group"><label>Lavoratore</label><select>{WORKERS.map(w=><option key={w.id}>{w.nome}</option>)}</select></div>
            <div className="form-group"><label>Tipo</label><select><option>ENTRATA</option><option>USCITA</option><option>PAUSA_INIZIO</option><option>PAUSA_FINE</option></select></div>
            <div className="form-group"><label>Data e Ora</label><input type="datetime-local"/></div>
            <div className="form-group"><label>Metodo</label><select><option>MANUALE</option><option>GPS</option><option>NFC</option><option>QR_CODE</option></select></div>
            <div className="form-group full"><label>Note</label><input placeholder="Motivazione timbratura manuale..."/></div>
          </div>
        )}
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Annulla</button>
          <button className="btn btn-primary" onClick={onClose}><Icon d={Icons.check} size={14} color="white"/>Salva</button>
        </div>
      </div>
    </div>
  );
}

// ─── Login Screen ────────────────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState("admin@engipro.it");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = async () => {
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
          <div style={{fontSize:"2rem",fontWeight:"800",color:"#fff"}}>Engi<span style={{color:"#6c63ff"}}>Pro</span></div>
          <div style={{color:"#888",fontSize:"0.85rem",marginTop:"0.25rem"}}>Safety Platform</div>
        </div>
        {error && <div style={{background:"#ff4d4f22",border:"1px solid #ff4d4f",color:"#ff4d4f",padding:"0.75rem",borderRadius:"8px",marginBottom:"1rem",fontSize:"0.85rem"}}>{error}</div>}
        <div style={{marginBottom:"1rem"}}>
          <label style={{color:"#aaa",fontSize:"0.8rem",display:"block",marginBottom:"0.4rem"}}>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} style={{width:"100%",background:"#0f1117",border:"1px solid #2a2d3e",borderRadius:"8px",padding:"0.65rem",color:"#fff",fontSize:"0.9rem",boxSizing:"border-box"}} />
        </div>
        <div style={{marginBottom:"1.5rem"}}>
          <label style={{color:"#aaa",fontSize:"0.8rem",display:"block",marginBottom:"0.4rem"}}>Password</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} onKeyDown={e=>e.key==="Enter"&&handleSubmit()} style={{width:"100%",background:"#0f1117",border:"1px solid #2a2d3e",borderRadius:"8px",padding:"0.65rem",color:"#fff",fontSize:"0.9rem",boxSizing:"border-box"}} />
        </div>
        <button onClick={handleSubmit} disabled={loading} style={{width:"100%",background:"#6c63ff",color:"#fff",border:"none",borderRadius:"8px",padding:"0.75rem",fontSize:"0.95rem",fontWeight:"600",cursor:"pointer"}}>
          {loading ? "Accesso..." : "Accedi"}
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState(auth.isLoggedIn());
  const [activeView, setActiveView] = useState("dashboard");
  const [showModal, setShowModal] = useState(false);
  const [apiData, setApiData] = useState({ workers:[], companies:[], deadlines:[], documents:[], dpiItems:[], dpiAssignments:[], protocols:[], visits:[], courses:[], editions:[], participations:[], timbrature:[], records:[] });
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    if (!auth.isLoggedIn()) return;
    setLoading(true);
    try {
      const [workers, companies, deadlines, documents, dpiItems, dpiAssignments, protocols, visits, courses, editions, participations, timbrature, records] = await Promise.allSettled([
        apiWorkers.list(), apiCompanies.list(), apiDeadlines.list(), apiDocuments.list(),
        apiDPI.items(), apiDPI.assignments(), apiMedical.protocols(), apiMedical.visits(),
        apiTraining.courses(), apiTraining.editions(), apiTraining.participations(),
        apiAttendance.timbrature(), apiAttendance.records()
      ]);
      setApiData({
        workers:       workers.value?.items       || workers.value       || [],
        companies:     companies.value?.items     || companies.value     || [],
        deadlines:     deadlines.value?.items     || deadlines.value     || [],
        documents:     documents.value?.items     || documents.value     || [],
        dpiItems:      dpiItems.value?.items      || dpiItems.value      || [],
        dpiAssignments:dpiAssignments.value?.items|| dpiAssignments.value|| [],
        protocols:     protocols.value?.items     || protocols.value     || [],
        visits:        visits.value?.items        || visits.value        || [],
        courses:       courses.value?.items       || courses.value       || [],
        editions:      editions.value?.items      || editions.value      || [],
        participations:participations.value?.items|| participations.value|| [],
        timbrature:    timbrature.value?.items    || timbrature.value    || [],
        records:       records.value?.items       || records.value       || [],
      });
    } catch(e) { console.error('Load error:', e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { if (loggedIn) loadData(); }, [loggedIn, loadData]);

  if (!loggedIn) return <LoginScreen onLogin={() => setLoggedIn(true)} />;

  const WORKERS = apiData.workers;
  const COMPANIES = apiData.companies;
  const DEADLINES = apiData.deadlines;
  const DOCUMENTS = apiData.documents;
  const DPI_ITEMS = apiData.dpiItems;
  const MEDICAL_VISITS = apiData.visits;
  const PROTOCOLS = apiData.protocols;
  const COURSES = apiData.courses;
  const PARTICIPATIONS = apiData.participations;
  const TIMBRATURE = apiData.timbrature;
  const ATTENDANCE_RECORDS = apiData.records;

  const alertCount = DEADLINES.filter(d=>d.stato==="ALERT"||d.stato==="EXPIRED").length;
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
            <div className="user-card">
              <div className="user-avatar">FC</div>
              <div><div className="user-name">Francesco C.</div><div className="user-role">Admin · EngiPro</div></div>
            </div>
          </div>
        </aside>
        <main className="main">
          <header className="topbar">
            <div className="topbar-title">{viewTitles[activeView]}</div>
            <div className="search-box"><Icon d={Icons.search} size={15} color="var(--c-muted)"/><input placeholder="Cerca..."/></div>
            <div className="icon-btn" style={{position:"relative"}}><Icon d={Icons.bell} size={17} color="var(--c-muted)"/>{alertCount>0&&<span className="notif-dot"/>}</div>
          </header>
          <div className="content">
            {activeView==="dashboard"  && <DashboardView/>}
            {activeView==="workers"    && <WorkersView    onAdd={()=>setShowModal(true)}/>}
            {activeView==="deadlines"  && <DeadlinesView  onAdd={()=>setShowModal(true)}/>}
            {activeView==="documents"  && <DocumentsView  onAdd={()=>setShowModal(true)}/>}
            {activeView==="dpi"        && <DPIView        onAdd={()=>setShowModal(true)}/>}
            {activeView==="companies"  && <CompaniesView  onAdd={()=>setShowModal(true)}/>}
            {activeView==="medical"    && <MedicalView    onAdd={()=>setShowModal(true)}/>}
            {activeView==="training"   && <TrainingView   onAdd={()=>setShowModal(true)}/>}
            {activeView==="attendance" && <AttendanceView onAdd={()=>setShowModal(true)}/>}
          </div>
        </main>
      </div>
      {showModal && <AddModal view={activeView} onClose={()=>setShowModal(false)}/>}
    </>
  );
}
