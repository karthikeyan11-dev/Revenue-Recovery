import React from 'react';
import { NAV_ITEMS } from '../../constants/routes';
import type { RouteKey } from '../../constants/routes';

export interface HeaderProps {
  activeTab: RouteKey;
  onTabChange: (tab: RouteKey) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  return (
    <header className="border-b border-slate-800 bg-[#0c2340]/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <img
            src="/revenue-recovery-logo-alone.png"
            alt="Revenue Recovery Logo"
            className="h-9 w-9 object-contain drop-shadow-md"
          />
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white tracking-tight text-lg">
                AI Revenue Recovery
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 font-medium border border-brand-500/30">
                Track 03
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Razorpay AI Buildathon — Autonomous Policy-Governed Orchestrator
            </p>
          </div>
        </div>

        <nav className="flex items-center space-x-1 sm:space-x-2">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.key}
              onClick={() => onTabChange(item.key as RouteKey)}
              id={item.id}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === item.key
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};
