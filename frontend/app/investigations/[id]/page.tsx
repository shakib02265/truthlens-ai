'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { VerdictBadge } from '@/components/VerdictBadge';
import { ConfidenceBar } from '@/components/ConfidenceBar';
import { AgentTraceViewer } from '@/components/AgentTraceViewer';
import { EvidenceGraphViewer } from '@/components/EvidenceGraphViewer';
import { HumanReviewModal } from '@/components/HumanReviewModal';
import { fetchWithAuth } from '@/lib/api';
import {
  FileText, ShieldCheck, AlertTriangle, Download, RefreshCw, CheckCircle2,
  ExternalLink, BrainCircuit, UserCheck, Layers, BookOpen
} from 'lucide-react';

export default function InvestigationDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [investigation, setInvestigation] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'evidence' | 'sources' | 'graph' | 'trace'>('overview');

  const loadData = async () => {
    try {
      const res = await fetchWithAuth(`/investigations/${id}`);
      if (res.ok) {
        const data = await res.json();
        setInvestigation(data);
      }

      const gRes = await fetchWithAuth(`/investigations/${id}/graph`);
      if (gRes.ok) {
        const gData = await gRes.json();
        setGraphData(gData);
      }
    } catch (err) {
      console.error('Failed to load investigation details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) loadData();
  }, [id]);

  useEffect(() => {
    if (!investigation || investigation.status !== 'IN_PROGRESS') return;

    const interval = setInterval(() => {
      loadData();
    }, 2000);

    return () => clearInterval(interval);
  }, [investigation?.status, id]);


  const handleExport = async (format: 'pdf' | 'html') => {
    try {
      const response = await fetchWithAuth(`/investigations/${id}/report?format=${format}`, {
        method: 'POST',
      });
      if (format === 'pdf') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `truthlens_report_${id}.pdf`;
        a.click();
      } else {
        const htmlText = await response.text();
        const win = window.open('', '_blank');
        if (win) {
          win.document.write(htmlText);
          win.document.close();
        }
      }
    } catch (err) {
      console.error('Report export failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-slate-500 text-xs font-mono">
          <RefreshCw className="w-5 h-5 animate-spin mr-2 text-emerald-600" />
          Loading Multi-Agent Investigation State...
        </div>
      </div>
    );
  }

  if (!investigation) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
          Investigation record not found.
        </div>
      </div>
    );
  }

  const verdict = investigation.verdicts?.[0] || {};
  const isAwaitingReview = investigation.status === 'AWAITING_HUMAN_REVIEW';

  const supportingEvidence = investigation.evidence?.filter((e: any) => e.stance === 'SUPPORTS') || [];
  const contradictingEvidence = investigation.evidence?.filter((e: any) => e.stance === 'CONTRADICTS') || [];
  const neutralEvidence = investigation.evidence?.filter((e: any) => e.stance === 'NEUTRAL') || [];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
          {/* Header Banner */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mb-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-5">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider font-mono text-emerald-600 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-md mb-2 inline-block">
                  Case ID: {investigation.id.substring(0, 8)} | Mode: {investigation.mode}
                </span>
                <h1 className="text-xl font-extrabold text-slate-900 leading-snug">
                  "{investigation.claim?.text}"
                </h1>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <button
                  onClick={() => handleExport('html')}
                  className="flex items-center gap-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-xl transition-colors"
                >
                  <FileText className="w-4 h-4" /> View HTML
                </button>
                <button
                  onClick={() => handleExport('pdf')}
                  className="flex items-center gap-1.5 text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 px-4 py-2 rounded-xl shadow-sm transition-colors"
                >
                  <Download className="w-4 h-4" /> Export PDF
                </button>
              </div>
            </div>

            {/* Verdict & Confidence Panel */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 items-center bg-slate-50 p-5 rounded-xl border border-slate-200">
              <div>
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Final Verdict</span>
                <VerdictBadge verdict={investigation.verdict_status} size="lg" />
              </div>

              <div>
                <ConfidenceBar score={investigation.confidence_score} />
              </div>

              <div>
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Agent Verification</span>
                {verdict.verified ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" /> Verified: True (Passed)
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" /> Verified: False (Revision)
                  </span>
                )}
              </div>

              <div className="text-right flex flex-col items-end">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Human Review Status</span>
                {isAwaitingReview ? (
                  <button
                    onClick={() => setShowReviewModal(true)}
                    className="flex items-center gap-2 text-xs font-bold text-amber-900 bg-amber-100 hover:bg-amber-200 border border-amber-300 px-3.5 py-1.5 rounded-lg transition-colors"
                  >
                    <AlertTriangle className="w-4 h-4 text-amber-600" /> Action Required: Review
                  </button>
                ) : (
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-lg inline-flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> {investigation.status}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-slate-200 mb-6">
            {[
              { id: 'overview', label: 'Executive Summary', icon: BookOpen },
              { id: 'evidence', label: `Evidence Statements (${investigation.evidence?.length || 0})`, icon: Layers },
              { id: 'sources', label: `Evaluated Sources (${investigation.sources?.length || 0})`, icon: ShieldCheck },
              { id: 'graph', label: 'Evidence Graph', icon: Layers },
              { id: 'trace', label: `Agent Execution Trace (${investigation.agent_runs?.length || 0})`, icon: BrainCircuit },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all ${
                    isActive
                      ? 'border-emerald-600 text-emerald-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* TAB 1: EXECUTIVE SUMMARY OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                    Synthesized Verdict & Reasoning
                  </h3>
                  <p className="text-sm text-slate-700 leading-relaxed font-sans">
                    {verdict.reasoning_summary || 'Investigation analysis in progress...'}
                  </p>
                </div>

                {/* QA Verification Audit Note Card */}
                {verdict.verification_notes && (
                  <div className="bg-slate-900 text-slate-100 rounded-2xl p-5 border border-slate-800 shadow-sm">
                    <div className="flex items-center gap-2 mb-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" /> Agent H Quality Assurance Verification Audit
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed font-mono">
                      {verdict.verification_notes}
                    </p>
                  </div>
                )}

                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">
                    Key Empirical Evidence Statements
                  </h3>
                  <ul className="space-y-2 text-xs text-slate-700">
                    {verdict.key_evidence?.map((item: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {verdict.limitations?.length > 0 && (
                  <div className="bg-amber-50/50 rounded-2xl border border-amber-200 p-6">
                    <h3 className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-2">
                      Investigation Limitations & Caveats
                    </h3>
                    <ul className="list-disc list-inside text-xs text-amber-800 space-y-1">
                      {verdict.limitations.map((lim: string, idx: number) => (
                        <li key={idx}>{lim}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Sidebar Agent Trace Widget */}
              <div>
                <AgentTraceViewer
                  investigationId={investigation.id}
                  initialTrace={investigation.agent_runs || []}
                  isLive={investigation.status === 'IN_PROGRESS'}
                  onComplete={loadData}
                />
              </div>
            </div>
          )}

          {/* TAB 2: EVIDENCE STATEMENTS */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl">
                  <span className="text-xs font-bold text-emerald-800 uppercase">Supporting Evidence ({supportingEvidence.length})</span>
                </div>
                <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl">
                  <span className="text-xs font-bold text-rose-800 uppercase">Contradicting Evidence ({contradictingEvidence.length})</span>
                </div>
                <div className="bg-slate-100 border border-slate-200 p-4 rounded-xl">
                  <span className="text-xs font-bold text-slate-800 uppercase">Neutral Context ({neutralEvidence.length})</span>
                </div>
              </div>

              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                {investigation.evidence?.map((ev: any) => (
                  <div key={ev.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 text-xs">
                    <div className="flex items-center justify-between mb-2">
                      <span className={`font-bold px-2.5 py-0.5 rounded-full text-[10px] ${
                        ev.stance === 'SUPPORTS' ? 'bg-emerald-100 text-emerald-800' :
                        ev.stance === 'CONTRADICTS' ? 'bg-rose-100 text-rose-800' : 'bg-slate-200 text-slate-700'
                      }`}>
                        {ev.stance} (Strength: {Math.round(ev.strength * 100)}%)
                      </span>
                      <span className="text-[10px] text-slate-500">Source ID: {ev.source_id.substring(0, 8)}</span>
                    </div>
                    <p className="text-slate-800 font-medium text-sm mb-2">"{ev.evidence_text}"</p>
                    {ev.context && <p className="text-slate-500 italic text-xs">Context: {ev.context}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SOURCES & CREDIBILITY SCORES */}
          {activeTab === 'sources' && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900 mb-4">Retrieved Sources & Domain Authority Evaluations</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 uppercase tracking-wider">
                      <th className="p-3 font-bold">Domain / Title</th>
                      <th className="p-3 font-bold">Type</th>
                      <th className="p-3 font-bold">Date</th>
                      <th className="p-3 font-bold">Credibility</th>
                      <th className="p-3 font-bold">Evaluation Rationale</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {investigation.sources?.map((src: any) => (
                      <tr key={src.id} className="hover:bg-slate-50">
                        <td className="p-3">
                          <a href={src.url} target="_blank" rel="noreferrer" className="font-bold text-blue-600 hover:underline flex items-center gap-1">
                            {src.title || src.domain} <ExternalLink className="w-3 h-3" />
                          </a>
                          <span className="text-[10px] text-slate-400 block font-mono">{src.domain}</span>
                        </td>
                        <td className="p-3 font-semibold text-slate-600 uppercase">{src.source_type}</td>
                        <td className="p-3 text-slate-500">{src.publication_date || 'Unknown'}</td>
                        <td className="p-3">
                          <span className="font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                            {Math.round((src.evaluation?.final_credibility_score || 0.5) * 100)}%
                          </span>
                        </td>
                        <td className="p-3 text-slate-600 italic max-w-md">{src.evaluation?.explanation || 'Evaluated'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: EVIDENCE GRAPH */}
          {activeTab === 'graph' && (
            <EvidenceGraphViewer nodes={graphData.nodes} edges={graphData.edges} />
          )}

          {/* TAB 5: AGENT EXECUTION TRACE */}
          {activeTab === 'trace' && (
            <AgentTraceViewer
              investigationId={investigation.id}
              initialTrace={investigation.agent_runs || []}
              isLive={investigation.status === 'IN_PROGRESS'}
            />
          )}

          {/* Human Review Modal Trigger */}
          <HumanReviewModal
            investigationId={investigation.id}
            isOpen={showReviewModal}
            onClose={() => setShowReviewModal(false)}
            onSuccess={loadData}
          />
        </main>
      </div>
    </div>
  );
}
