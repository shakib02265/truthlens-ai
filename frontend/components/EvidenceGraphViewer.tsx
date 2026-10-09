'use client';

import React, { useState } from 'react';
import { Network, Database, ShieldAlert, FileText, CheckCircle2 } from 'lucide-react';

export interface GraphNode {
  id: string;
  label: string;
  type: string; // claim, source, evidence, verdict
  credibility_score?: number;
  stance?: string;
  data?: any;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string; // SUPPORTS, CONTRADICTS, NEUTRAL, DERIVED_FROM, CITES, PROVIDES
  weight?: number;
}

interface EvidenceGraphViewerProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export const EvidenceGraphViewer: React.FC<EvidenceGraphViewerProps> = ({ nodes = [], edges = [] }) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  if (!nodes || nodes.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
        <Network className="w-8 h-8 text-slate-400 mx-auto mb-2 animate-pulse" />
        <p className="text-sm font-medium">Evidence graph building in progress...</p>
      </div>
    );
  }

  // Pre-calculate positions for simple radial/structured layout
  const width = 700;
  const height = 400;
  const centerX = width / 2;
  const centerY = height / 2;

  const nodePositions: { [id: string]: { x: number; y: number } } = {};

  const claims = nodes.filter((n) => n.type === 'claim');
  const verdicts = nodes.filter((n) => n.type === 'verdict');
  const sources = nodes.filter((n) => n.type === 'source');
  const evidence = nodes.filter((n) => n.type === 'evidence');

  // Place Claim at top-center, Verdict at bottom-center, Sources left, Evidence right
  claims.forEach((n) => {
    nodePositions[n.id] = { x: centerX, y: 70 };
  });

  verdicts.forEach((n) => {
    nodePositions[n.id] = { x: centerX, y: height - 60 };
  });

  sources.forEach((n, idx) => {
    const total = sources.length || 1;
    const spacing = (height - 180) / Math.max(1, total - 1);
    const y = total === 1 ? centerY : 120 + idx * spacing;
    nodePositions[n.id] = { x: 120, y };
  });

  evidence.forEach((n, idx) => {
    const total = evidence.length || 1;
    const spacing = (height - 180) / Math.max(1, total - 1);
    const y = total === 1 ? centerY : 120 + idx * spacing;
    nodePositions[n.id] = { x: width - 120, y };
  });

  const getNodeColor = (node: GraphNode) => {
    if (node.type === 'claim') return 'fill-blue-600 stroke-blue-700';
    if (node.type === 'verdict') return 'fill-purple-600 stroke-purple-700';
    if (node.type === 'source') return 'fill-slate-700 stroke-slate-800';
    if (node.stance === 'SUPPORTS') return 'fill-emerald-500 stroke-emerald-600';
    if (node.stance === 'CONTRADICTS') return 'fill-rose-500 stroke-rose-600';
    return 'fill-amber-500 stroke-amber-600';
  };

  const getEdgeColor = (rel: string) => {
    if (rel === 'SUPPORTS') return '#16a34a';
    if (rel === 'CONTRADICTS') return '#dc2626';
    if (rel === 'DERIVED_FROM') return '#9333ea';
    return '#64748b';
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <Network className="w-4 h-4 text-emerald-600" />
          Interactive Multi-Agent Evidence Graph
        </h3>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-600" /> Claim</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-slate-700" /> Source</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Supports</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Contradicts</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-purple-600" /> Verdict</span>
        </div>
      </div>

      <div className="relative overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto bg-slate-50 rounded-lg">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
            </marker>
          </defs>

          {/* Render Edges */}
          {edges.map((e) => {
            const srcPos = nodePositions[e.source];
            const tgtPos = nodePositions[e.target];
            if (!srcPos || !tgtPos) return null;

            return (
              <g key={e.id}>
                <line
                  x1={srcPos.x}
                  y1={srcPos.y}
                  x2={tgtPos.x}
                  y2={tgtPos.y}
                  stroke={getEdgeColor(e.relationship)}
                  strokeWidth={e.weight ? Math.max(1.5, e.weight * 2.5) : 2}
                  strokeDasharray={e.relationship === 'CONTRADICTS' ? '4,4' : undefined}
                  opacity={0.7}
                  markerEnd="url(#arrow)"
                />
              </g>
            );
          })}

          {/* Render Nodes */}
          {nodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;

            const isSelected = selectedNode?.id === node.id;

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => setSelectedNode(node)}
                className="cursor-pointer transition-transform hover:scale-110"
              >
                <circle
                  r={isSelected ? 22 : 18}
                  className={`${getNodeColor(node)} shadow-md`}
                  strokeWidth={isSelected ? 3 : 2}
                />
                <text
                  y={32}
                  textAnchor="middle"
                  className="text-[10px] font-semibold fill-slate-700 pointer-events-none"
                >
                  {node.label.length > 25 ? node.label.substring(0, 22) + '...' : node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs flex items-start justify-between">
          <div>
            <span className="font-bold text-slate-800 uppercase text-[10px] bg-slate-200 px-2 py-0.5 rounded mr-2">
              {selectedNode.type}
            </span>
            <span className="font-semibold text-slate-700">{selectedNode.label}</span>
            {selectedNode.data?.text && <p className="text-slate-600 mt-1 italic font-sans">"{selectedNode.data.text}"</p>}
            {selectedNode.data?.url && <p className="text-blue-600 mt-1 font-mono text-[10px]">{selectedNode.data.url}</p>}
          </div>
          <button
            onClick={() => setSelectedNode(null)}
            className="text-slate-400 hover:text-slate-600 text-sm font-bold"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};
