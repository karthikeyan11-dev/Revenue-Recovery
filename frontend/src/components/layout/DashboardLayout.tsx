import React from 'react';
import { Header } from './Header';
import { StatusBanner } from './StatusBanner';
import type { RouteKey } from '../../constants/routes';

export interface DashboardLayoutProps {
  activeTab: RouteKey;
  onTabChange: (tab: RouteKey) => void;
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  activeTab,
  onTabChange,
  children,
}) => {
  return (
    <div className="min-h-screen bg-[#07162c] text-slate-100 flex flex-col">
      <Header activeTab={activeTab} onTabChange={onTabChange} />
      <StatusBanner />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};
