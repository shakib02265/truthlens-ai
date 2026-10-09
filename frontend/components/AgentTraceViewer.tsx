'use client';

import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, AlertTriangle, ShieldCheck, Search, FileText, BrainCircuit } from 'lucide-react';

export interface TraceItem {
  agent_name: string;
  timestamp: string;
  decision: string;
  tool_used?: string;
  tool_result_summary?: string;
}

import { getAuthToken } from '@/lib/api';

interface AgentTraceViewerProps {
  investigationId: string;
  initialTrace?: TraceItem[];
  isLive?: boolean;
  onComplete?: () => void;
}

export const AgentTraceViewer: React.FC<AgentTraceViewerProps> = ({
  investigationId,
  initialTrace = [],
  isLive = true,
  onComplete
}) => {
  const [traceLogs, setTraceLogs] = useState<TraceItem[]>(initialTrace);

  useEffect(() => {
    setTraceLogs(initialTrace);
  }, [initialTrace]);

  useEffect(() => {
    if (!isLive || !investigationId) return;

    const token = getAuthToken();
    const streamUrl = `/api/investigations/${investigationId}/stream` + (token ? `?token=${encodeURIComponent(token)}` : '');
    const eventSource = new EventSource(streamUrl);

    eventSource.addEventListener('agent_trace', (e: MessageEvent) => {
      try {
        const item: TraceItem = JSON.parse(e.data);
        setTraceLogs((prev) => [...prev, item]);
      } catch (err) {
        console.error('Failed to parse SSE trace event:', err);
      }
    });

    eventSource.addEventListener('completed', () => {
      eventSource.close();
      if (onComplete) {
        onComplete();
      }
    });

    return () => {
      eventSource.close();
    };
  }, [investigationId, isLive, onComplete]);


  const getIcon = (agentName: string, decision: string) => {
    const dLower = decision.toLowerCase();
    if (dLower.includes('error') || dLower.includes('warning') || dLower.includes('contradiction')) {
      return <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />;
    }
    if (agentName.includes('Claim Analyzer')) return <BrainCircuit className="w-4 h-4 text-blue-500 shrink-0" />;
    if (agentName.includes('Planner') || agentName.includes('Research')) return <Search className="w-4 h-4 text-purple-500 shrink-0" />;
    if (agentName.includes('Source') || agentName.includes('Evidence')) return <FileText className="w-4 h-4 text-emerald-500 shrink-0" />;
    if (agentName.includes('Verification') || agentName.includes('Verdict')) return <ShieldCheck className="w-4 h-4 text-green-600 shrink-0" />;
    
    return <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />;
  };

  return (
    <div className="bg-slate-900 text-slate-100 rounded-xl p-5 border border-slate-800 shadow-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-emerald-400" />
          Autonomous Agent Execution Trace
        </h3>
        {isLive && (
          <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-0.5 rounded-full font-medium">
            <Loader2 className="w-3 h-3 animate-spin" /> Live Trace
          </span>
        )}
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
        {traceLogs.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-4 text-center">Initializing multi-agent graph workflow...</p>
        ) : (
          traceLogs.map((item, idx) => (
            <div key={idx} className="flex items-start gap-3 bg-slate-950/70 p-3 rounded-lg border border-slate-800 text-xs">
              <div className="mt-0.5">{getIcon(item.agent_name, item.decision)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-semibold text-slate-200">{item.agent_name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-slate-300 leading-relaxed">{item.decision}</p>
                {item.tool_used && (
                  <span className="inline-block mt-1 text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                    tool: {item.tool_used}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
