'use client';

import React, { useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { Settings, Cpu, Search, Sliders, ShieldCheck } from 'lucide-react';

export default function SettingsPage() {
  const [llmProvider, setLlmProvider] = useState('demo');
  const [searchProvider, setSearchProvider] = useState('demo');

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 max-w-4xl mx-auto w-full">
          <div className="mb-8">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">System Settings & Multi-Agent Config</h1>
            <p className="text-xs text-slate-500 mt-1">Configure LLM providers, search tool connections, and confidence engine weights</p>
          </div>

          <div className="space-y-6">
            {/* LLM Provider Selection */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900">LLM Engine Abstraction</h2>
                  <p className="text-xs text-slate-500">Configure default reasoning and extraction LLM provider</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                {['demo', 'openai', 'gemini', 'anthropic'].map((p) => (
                  <button
                    key={p}
                    onClick={() => setLlmProvider(p)}
                    className={`p-3 rounded-xl border text-left font-bold capitalize transition-all ${
                      llmProvider === p
                        ? 'border-emerald-600 bg-emerald-50 text-emerald-800 ring-2 ring-emerald-500/20'
                        : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {p === 'demo' ? 'Mock / Demo Provider (Offline)' : `${p} Provider`}
                  </button>
                ))}
              </div>
            </div>

            {/* Search Provider Selection */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-50 text-purple-600 rounded-xl">
                  <Search className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900">Search Engine Provider</h2>
                  <p className="text-xs text-slate-500">Select web research engine abstraction</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                {['demo', 'tavily', 'serper', 'google'].map((s) => (
                  <button
                    key={s}
                    onClick={() => setSearchProvider(s)}
                    className={`p-3 rounded-xl border text-left font-bold capitalize transition-all ${
                      searchProvider === s
                        ? 'border-emerald-600 bg-emerald-50 text-emerald-800 ring-2 ring-emerald-500/20'
                        : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {s === 'demo' ? 'Deterministic Mock Search (Offline)' : `${s} Search API`}
                  </button>
                ))}
              </div>
            </div>

            {/* Deterministic Confidence Engine Weights */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900">Deterministic Confidence Engine Formula</h2>
                  <p className="text-xs text-slate-500">Configured weights used in formula evaluation</p>
                </div>
              </div>

              <div className="space-y-3 text-xs text-slate-700 font-mono">
                <div className="flex justify-between p-2 bg-slate-50 rounded">
                  <span>Source Quality Factor</span>
                  <span className="font-bold">30%</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-50 rounded">
                  <span>Evidence Agreement Factor</span>
                  <span className="font-bold">25%</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-50 rounded">
                  <span>Evidence Strength Factor</span>
                  <span className="font-bold">20%</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-50 rounded">
                  <span>Recency Factor</span>
                  <span className="font-bold">10%</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-50 rounded">
                  <span>Independent Sources Factor</span>
                  <span className="font-bold">10%</span>
                </div>
                <div className="flex justify-between p-2 bg-slate-50 rounded text-rose-700">
                  <span>Contradiction Penalty</span>
                  <span className="font-bold">-5%</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
