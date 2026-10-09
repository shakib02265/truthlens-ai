'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { VerdictBadge } from '@/components/VerdictBadge';
import { ConfidenceBar } from '@/components/ConfidenceBar';
import { fetchWithAuth } from '@/lib/api';
import { FileSearch, ShieldCheck, CheckCircle2, TrendingUp, ArrowRight, Sparkles } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const res = await fetchWithAuth('/investigations/dashboard/stats');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Failed to load dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">Fact Verification Research Dashboard</h1>
              <p className="text-xs text-slate-500 mt-1">Autonomous Multi-Agent Investigation Metrics & Recent Cases</p>
            </div>
            <Link
              href="/investigations/new"
              className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-5 py-2.5 rounded-xl shadow-sm transition-all"
            >
              <FileSearch className="w-4 h-4" /> Investigate New Claim
            </Link>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                <FileSearch className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Claims</span>
                <p className="text-2xl font-black text-slate-900">{stats?.total_investigations ?? 0}</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Completed Cases</span>
                <p className="text-2xl font-black text-slate-900">{stats?.verified_investigations ?? 0}</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Avg Confidence</span>
                <p className="text-2xl font-black text-slate-900">
                  {Math.round((stats?.average_confidence || 0) * 100)}%
                </p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="p-3 bg-amber-50 text-amber-600 rounded-xl">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Agent Engine</span>
                <p className="text-sm font-bold text-slate-900">LangGraph Active</p>
              </div>
            </div>
          </div>

          {/* Recent Investigations List */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-8">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900">Recent Misinformation Investigations</h2>
              <span className="text-xs text-slate-400">Live Agent Pipeline Status</span>
            </div>

            {loading ? (
              <p className="text-xs text-slate-500 py-8 text-center italic">Loading investigation records...</p>
            ) : !stats?.recent_investigations || stats.recent_investigations.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <FileSearch className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                <p className="text-sm font-medium">No investigations found.</p>
                <p className="text-xs text-slate-400 mt-1">Submit a factual claim to launch your first autonomous investigation.</p>
                <Link
                  href="/investigations/new"
                  className="inline-flex items-center gap-2 mt-4 bg-emerald-600 text-white text-xs font-bold px-4 py-2 rounded-xl"
                >
                  Launch Demo Investigation
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {stats.recent_investigations.map((inv: any) => (
                  <div key={inv.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1 max-w-2xl">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                          {inv.mode} MODE
                        </span>
                        <span className="text-xs text-slate-400">
                          {new Date(inv.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <Link
                        href={`/investigations/${inv.id}`}
                        className="text-sm font-bold text-slate-900 hover:text-emerald-600 transition-colors line-clamp-1"
                      >
                        {inv.claim?.text || inv.title}
                      </Link>
                    </div>

                    <div className="flex items-center gap-6 shrink-0">
                      <div className="w-32">
                        <ConfidenceBar score={inv.confidence_score} showLabel={false} />
                      </div>
                      <VerdictBadge verdict={inv.verdict_status || 'UNVERIFIED'} size="sm" />
                      <Link
                        href={`/investigations/${inv.id}`}
                        className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
