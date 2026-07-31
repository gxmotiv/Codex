import React from 'react';
import { createRoot } from 'react-dom/client';
import { Stars, Database, BrainCircuit } from 'lucide-react';
import './styles.css';

function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-16">
        <div className="mb-8 inline-flex w-fit items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
          <Stars className="h-4 w-4" /> KP Astrology Workbench
        </div>
        <h1 className="max-w-4xl text-5xl font-bold tracking-tight md:text-7xl">
          Chart calculation, validation, and AI-assisted prediction in one stack.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-slate-300">
          React + Vite frontend, FastAPI backend, PostgreSQL persistence, KP calculation engine, and local LLM connectors for Ollama and LM Studio.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[
            [Stars, 'KP Engine', 'Ayanamsa, Placidus cusps, nakshatra/sub lords, dashas, significators, and predictions.'],
            [Database, 'Validation Store', 'Saved charts, user queries, and golden charts versioned through Alembic migrations.'],
            [BrainCircuit, 'Local LLMs', 'Generate narrative interpretations through Ollama or LM Studio without cloud dependencies.'],
          ].map(([Icon, title, description]) => (
            <article key={title} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-cyan-950/20">
              <Icon className="mb-4 h-8 w-8 text-cyan-300" />
              <h2 className="text-xl font-semibold">{title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
