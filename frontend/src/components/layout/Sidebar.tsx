import React from 'react';
import { NAV_ITEMS } from '../../constants/routes';
import type { RouteKey } from '../../constants/routes';


export interface SidebarProps {
  activeTab: RouteKey;
  onTabChange: (tab: RouteKey) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <aside className="w-64 bg-[#0c2340]/90 border-r border-slate-800 p-4 space-y-1">
      {NAV_ITEMS.map((item) => (
        <button
          key={item.key}
          onClick={() => onTabChange(item.key as RouteKey)}
          className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
            activeTab === item.key
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'text-slate-300 hover:bg-slate-800/60'
          }`}
        >
          {item.label}
        </button>
      ))}
    </aside>
  );
};
