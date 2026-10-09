'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldCheck, PlusCircle, User, LogOut, FileSearch } from 'lucide-react';
import { removeAuthToken } from '@/lib/api';

export const Navbar: React.FC = () => {
  const handleLogout = () => {
    removeAuthToken();
    window.location.href = '/login';
  };

  return (
    <header className="h-16 bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40 px-3 md:px-6 flex items-center justify-between">
      <div className="flex items-center gap-2 md:gap-3">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="p-1.5 md:p-2 bg-emerald-600 text-white rounded-xl shadow-md">
            <ShieldCheck className="w-4 h-4 md:w-5 md:h-5" />
          </div>
          <div>
            <span className="font-extrabold text-base md:text-lg tracking-tight text-white">TruthLens<span className="text-emerald-400">.AI</span></span>
            <span className="hidden sm:block text-[10px] text-slate-400 font-mono -mt-1">Fact Verification Engine</span>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-2 md:gap-4">
        <Link
          href="/investigations/new"
          className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 md:px-4 md:py-2 rounded-xl transition-all shadow-sm"
        >
          <PlusCircle className="w-3.5 h-3.5 md:w-4 md:h-4" />
          <span className="hidden xs:inline sm:inline">New Investigation</span>
          <span className="xs:hidden sm:hidden">New</span>
        </Link>

        <button
          onClick={handleLogout}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white px-2 py-1.5 md:px-3 md:py-2 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <LogOut className="w-3.5 h-3.5 md:w-4 md:h-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
};
