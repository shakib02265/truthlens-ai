'use client';

import React, { useState } from 'react';
import { UserCheck, CheckCircle, XCircle, RotateCcw, AlertTriangle } from 'lucide-react';
import { fetchWithAuth } from '@/lib/api';

interface HumanReviewModalProps {
  investigationId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  reason?: string;
}

export const HumanReviewModal: React.FC<HumanReviewModalProps> = ({
  investigationId,
  isOpen,
  onClose,
  onSuccess,
  reason
}) => {
  const [action, setAction] = useState<'ACCEPT' | 'REJECT' | 'REQUEST_MORE_INVESTIGATION'>('ACCEPT');
  const [feedback, setFeedback] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetchWithAuth(`/investigations/${investigationId}/review`, {
        method: 'POST',
        body: JSON.stringify({ action, feedback }),
      });
      if (res.ok) {
        onSuccess();
        onClose();
      }
    } catch (err) {
      console.error('Human review submission error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
        <div className="flex items-center gap-3 border-b border-slate-100 pb-4 mb-4">
          <div className="p-2.5 bg-amber-100 text-amber-800 rounded-xl">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Human-in-the-Loop Verification Review</h2>
            <p className="text-xs text-slate-500">Manual review required before finalizing investigation report</p>
          </div>
        </div>

        {reason && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
            <strong>Trigger Reason:</strong> {reason}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Select Decision Action
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setAction('ACCEPT')}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-bold transition-all ${
                  action === 'ACCEPT'
                    ? 'border-emerald-600 bg-emerald-50 text-emerald-700 ring-2 ring-emerald-500/20'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <CheckCircle className="w-5 h-5 mb-1 text-emerald-600" />
                Accept Verdict
              </button>

              <button
                type="button"
                onClick={() => setAction('REJECT')}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-bold transition-all ${
                  action === 'REJECT'
                    ? 'border-rose-600 bg-rose-50 text-rose-700 ring-2 ring-rose-500/20'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <XCircle className="w-5 h-5 mb-1 text-rose-600" />
                Reject Verdict
              </button>

              <button
                type="button"
                onClick={() => setAction('REQUEST_MORE_INVESTIGATION')}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-bold transition-all ${
                  action === 'REQUEST_MORE_INVESTIGATION'
                    ? 'border-blue-600 bg-blue-50 text-blue-700 ring-2 ring-blue-500/20'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <RotateCcw className="w-5 h-5 mb-1 text-blue-600" />
                More Research
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Reviewer Notes / Justification
            </label>
            <textarea
              rows={3}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Add qualitative notes regarding source credibility, evidence strength, or revision criteria..."
              className="w-full text-xs p-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-lg shadow-sm"
            >
              {submitting ? 'Submitting...' : 'Submit Decision'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
