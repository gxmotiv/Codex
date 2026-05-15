import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Brain, Calculator, Database, Sparkles } from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const modules = ['marriage','career','health','property','foreign','children','education','wealth','longevity','horary'];

const defaultChart = { name:'Test Native', date:'1990-05-15', time:'10:30:00', timezone:'Asia/Kolkata', latitude:19.076, longitude:72.8777, topocentric:true, include_outer:true };

function ChartWheel({ chart }) {
  const planets = chart?.planets || {};
  const cusps = chart?.cusps || {};
  const points = Object.values(planets).map((p) => {
    const angle = (p.longitude - 90) * Math.PI / 180;
    return { ...p, x: 150 + 92 * Math.cos(angle), y: 150 + 92 * Math.sin(angle) };
  });
  const cuspLines = Object.values(cusps).map((c) => {
    const angle = (c.longitude - 90) * Math.PI / 180;
    return { ...c, x2: 150 + 132 * Math.cos(angle), y2: 150 + 132 * Math.sin(angle), x1: 150 + 65 * Math.cos(angle), y1: 150 + 65 * Math.sin(angle) };
  });
  return <svg viewBox="0 0 300 300" className="wheel">
    <circle cx="150" cy="150" r="140" className="ring"/><circle cx="150" cy="150" r="72" className="ring muted"/>
    {[...Array(27)].map((_, i) => { const a = (i*13.333333-90)*Math.PI/180; return <line key={i} x1={150+116*Math.cos(a)} y1={150+116*Math.sin(a)} x2={150+140*Math.cos(a)} y2={150+140*Math.sin(a)} className="nak"/>; })}
    {cuspLines.map((c) => <line key={c.house} x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2} className="cusp"><title>{`Cusp ${c.house}: ${c.longitude_dms} | ${c.sign_lord}/${c.star_lord}/${c.sub_lord}`}</title></line>)}
    {points.map((p) => <g key={p.name}><circle cx={p.x} cy={p.y} r="9" className={p.retrograde ? 'planet rx' : 'planet'}><title>{`${p.name} ${p.longitude_dms} H${p.house} ${p.retrograde ? 'Rx' : ''}`}</title></circle><text x={p.x} y={p.y+3} textAnchor="middle" className="glyph">{p.name[0]}{p.retrograde?'℞':''}</text></g>)}
  </svg>;
}

function Table({ rows, kind }) {
  if (!rows) return null;
  return <div className="table-wrap"><table><thead><tr>{(kind === 'cusps' ? ['Cusp','Degree','Sign Lord','Star','Sub','Sub-Sub'] : ['Planet','Degree','House','Speed','SL','Star','Sub','Sub-Sub']).map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>
    {Object.values(rows).map((r) => kind === 'cusps' ? <tr key={r.house}><td>{r.house}</td><td>{r.longitude_dms}</td><td>{r.sign_lord}</td><td>{r.star_lord}</td><td>{r.sub_lord}</td><td>{r.sub_sub_lord}</td></tr> : <tr key={r.name}><td>{r.name}{r.retrograde?' ℞':''}</td><td>{r.longitude_dms}</td><td>{r.house}</td><td>{Number(r.speed).toFixed(4)}</td><td>{r.sign_lord}</td><td>{r.star_lord}</td><td>{r.sub_lord}</td><td>{r.sub_sub_lord}</td></tr>)}
  </tbody></table></div>;
}

function App() {
  const [form, setForm] = useState(defaultChart);
  const [chart, setChart] = useState(null);
  const [moduleName, setModuleName] = useState('marriage');
  const [question, setQuestion] = useState('When will I get married?');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const update = (k, v) => setForm((f) => ({...f, [k]: ['latitude','longitude'].includes(k) ? Number(v) : v}));
  const currentDasha = useMemo(() => chart?.current_dasha?.join(' → ') || 'Calculate chart', [chart]);
  async function calculate() { setLoading(true); const r = await fetch(`${API}/api/chart`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(form)}); setChart(await r.json()); setLoading(false); }
  async function predict() { setLoading(true); const r = await fetch(`${API}/api/predict`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ chart: form, module: moduleName, question, use_llm:true })}); setPrediction(await r.json()); setLoading(false); }
  return <main>
    <header><div><h1>Local KP Astrology AI</h1><p>Swiss Ephemeris + KP sub-lords + deterministic rules + optional local Ollama/LM Studio interpretation. No cloud astrology API.</p></div><span className="badge"><Database size={16}/> local-only</span></header>
    <section className="grid">
      <aside className="panel"><h2><Calculator/> Birth Data</h2>{Object.keys(defaultChart).filter(k=>typeof defaultChart[k] !== 'boolean').map(k=><label key={k}>{k}<input value={form[k]} onChange={e=>update(k,e.target.value)} /></label>)}<label className="check"><input type="checkbox" checked={form.topocentric} onChange={e=>update('topocentric', e.target.checked)}/> Topocentric planets</label><button onClick={calculate} disabled={loading}>Calculate Real Chart</button><div className="dash"><b>Current Dasha</b><span>{currentDasha}</span></div>{chart && <div className="dash"><b>Ruling Planets</b><span>{chart.ruling_planets.ruling_planets.join(', ')}</span></div>}</aside>
      <section className="panel center"><h2>Interactive Placidus Wheel</h2><ChartWheel chart={chart}/><div className="tabs"><button>Planets</button><button>Cusps</button><button>Significators</button></div></section>
      <aside className="panel"><h2><Brain/> AI Astrologer</h2><select value={moduleName} onChange={e=>setModuleName(e.target.value)}>{modules.map(m=><option key={m}>{m}</option>)}</select><textarea value={question} onChange={e=>setQuestion(e.target.value)} /><button onClick={predict} disabled={loading}><Sparkles size={16}/> Run Prediction</button>{prediction && <div className="answer"><b>Structured verdict:</b><p>{prediction.structured.verdict} — confidence {prediction.structured.confidence_score}%</p><b>LLM</b><p>{prediction.llm.text || prediction.llm.warning || 'Local LLM unavailable; showing deterministic data.'}</p><pre>{JSON.stringify(prediction.structured, null, 2)}</pre></div>}</aside>
    </section>
    {chart && <section className="panel"><h2>Planetary Positions</h2><Table rows={chart.planets}/><h2>Cuspal Positions</h2><Table rows={chart.cusps} kind="cusps"/><h2>Significator Matrix</h2><pre>{JSON.stringify(chart.significators, null, 2)}</pre></section>}
  </main>;
}

createRoot(document.getElementById('root')).render(<App/>);
