import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'TruthLens AI - Autonomous Multi-Agent Fact Verification',
  description: 'Autonomous Multi-Agent LLM Misinformation Investigation & Fact Verification System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
