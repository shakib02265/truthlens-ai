'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { fetchWithAuth } from '@/lib/api';
import { FileSearch, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

export default function NewInvestigationPage() {
  const router = useRouter();
  const [claim, setClaim] = useState('');
  const [mode, setMode] = useState('DEMO');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const sampleClaims = [
    'Artificial intelligence causes permanent memory loss.',
    'Drinking green tea completely reverses type-2 diabetes within 30 days.',
    '5G cellular network radiation alters human cellular DNA structure.',
    'Electric vehicles generate more net carbon emissions over their lifecycle than gas vehicles.'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setSubmitting(true);
    setError('');

    try {
      const res = await fetchWithAuth('/investigations', {
        method: 'POST',
        body: JSON.stringify({ claim, mode }),
      });

      if (!res.ok) {
        throw new Error('Failed to create investigation');
      }

      const inv = await res.json();
      router.push(`/investigations/${inv.id}`);
    } catch (err: any) {
      setError(err.message || 'Error creating investigation');
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 max-w-4xl mx-auto w-full">
          <div className="mb-8">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Launch Fact Verification Investigation</h1>
            <p className="text-xs text-slate-500 mt-1">Submit a factual claim for autonomous multi-agent analysis & evidence verification</p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
            {error && (
              <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  Factual Claim to Investigate
                </label>
                <textarea
                  rows={4}
                  required
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="e.g., Artificial intelligence usage causes permanent neurological memory loss."
                  className="w-full p-4 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-inner"
                />
              </div>

              {/* Sample Claims Suggestions */}
              <div>
                <span className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Or select a sample benchmark claim:
                </span>
                <div className="flex flex-wrap gap-2">
                  {sampleClaims.map((sample, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setClaim(sample)}
                      className="text-xs bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 transition-colors text-left"
                    >
                      "{sample}"
                    </button>
                  ))}
                </div>
              </div>

              {/* Execution Mode */}
              <div className="pt-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  Execution Mode
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setMode('DEMO')}
                    className={`p-4 rounded-xl border text-left transition-all ${
                      mode === 'DEMO'
                        ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-500/20'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center gap-2 font-bold text-xs text-slate-900 mb-1">
                      <Sparkles className="w-4 h-4 text-emerald-600" />
                      DEMO MODE (Offline)
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Deterministic realistic multi-agent verification without requiring external API keys.
                    </p>
                  </button>

                  <button
                    type="button"
                    onClick={() => setMode('LIVE')}
                    className={`p-4 rounded-xl border text-left transition-all ${
                      mode === 'LIVE'
                        ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-500/20'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center gap-2 font-bold text-xs text-slate-900 mb-1">
                      <FileSearch className="w-4 h-4 text-blue-600" />
                      LIVE WEB SEARCH MODE
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Executes live Tavily/Serper search queries and live page extraction.
                    </p>
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex justify-end">
                <button
                  type="submit"
                  disabled={submitting || !claim.trim()}
                  className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-6 py-3 rounded-xl shadow-md transition-all disabled:opacity-50"
                >
                  {submitting ? 'Initializing Multi-Agent Graph...' : 'Start Investigation'}
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
