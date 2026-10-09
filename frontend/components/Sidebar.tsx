'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileSearch, Settings, Database, Sparkles, BookOpen } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { label: 'New Investigation', href: '/investigations/new', icon: FileSearch },
    { label: 'System Settings', href: '/settings', icon: Settings },
  ];

  return (
    <aside className="hidden lg:flex w-64 bg-slate-900 border-r border-slate-800 flex-col justify-between p-4 min-h-[calc(100vh-4rem)] shrink-0">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Navigation</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </div>

      <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl text-xs space-y-2">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-[11px]">
          <Sparkles className="w-4 h-4" /> Multi-Agent Mode
        </div>
        <p className="text-[11px] text-slate-400 leading-normal">
          LangGraph 10-Stage Pipeline with Prompt Injection Boundaries & Deterministic Confidence Engine.
        </p>
      </div>
    </aside>
  );
};
