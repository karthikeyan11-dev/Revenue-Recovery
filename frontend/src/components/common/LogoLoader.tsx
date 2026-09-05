import React from 'react';
import { cn } from '../../lib/utils';
import logoAlone from '../../assets/revenue-recovery-logo-alone.png';
import logoFull from '../../assets/revenue-recovery-logo.png';

export interface LogoLoaderProps {
  variant?: 'inline' | 'card' | 'table' | 'fullscreen' | 'dashboard';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  label?: string;
  useFullLogo?: boolean;
}

export const LogoLoader: React.FC<LogoLoaderProps> = ({
  variant = 'card',
  size = 'md',
  className,
  label = 'Loading intelligent recovery data...',
  useFullLogo = false,
}) => {
  const logoSrc = useFullLogo ? logoFull : logoAlone;

  const sizeClasses = {
    xs: 'w-4 h-4',
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20',
  }[size];

  if (variant === 'inline') {
    return (
      <img
        src={logoSrc}
        alt="Loading"
        className={cn('inline-block object-contain animate-logo-pulse', sizeClasses, className)}
      />
    );
  }

  if (variant === 'table') {
    return (
      <div className={cn('relative w-full min-h-[340px] bg-white border border-slate-200/80 rounded-xl overflow-hidden shadow-xs flex flex-col justify-center items-center p-8', className)}>
        {/* Background table skeleton lines */}
        <div className="absolute inset-0 p-5 space-y-3 opacity-30 pointer-events-none">
          <div className="h-6 bg-slate-200 rounded-md w-full" />
          <div className="h-10 bg-slate-100 rounded-md w-full" />
          <div className="h-10 bg-slate-100 rounded-md w-full" />
          <div className="h-10 bg-slate-100 rounded-md w-full" />
          <div className="h-10 bg-slate-100 rounded-md w-full" />
          <div className="h-10 bg-slate-100 rounded-md w-full" />
        </div>

        {/* Pulsing Logo in Center */}
        <div className="relative z-10 flex flex-col items-center justify-center space-y-3 bg-white/90 backdrop-blur-xs p-6 rounded-2xl border border-slate-200/60 shadow-sm">
          <img
            src={logoAlone}
            alt="RevRecovery Loading"
            className="w-12 h-12 object-contain animate-logo-pulse drop-shadow-sm"
          />
          <div className="text-center space-y-0.5">
            <span className="text-xs font-semibold text-slate-800 tracking-tight block">
              {label}
            </span>
            <span className="text-[10px] text-slate-400 font-medium">
              Synchronizing with Razorpay Agent Swarm
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'dashboard') {
    return (
      <div className={cn('relative w-full space-y-6', className)}>
        {/* Background Dashboard skeleton */}
        <div className="space-y-6 opacity-35">
          <div className="h-32 bg-slate-200/70 rounded-xl" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-28 bg-slate-200/70 rounded-xl" />
            ))}
          </div>
          <div className="h-44 bg-slate-200/70 rounded-xl" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-72 bg-slate-200/70 rounded-xl" />
            <div className="h-72 bg-slate-200/70 rounded-xl" />
          </div>
        </div>

        {/* Center Overlay Logo */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="flex flex-col items-center justify-center space-y-3 bg-white/95 backdrop-blur-sm px-8 py-6 rounded-2xl border border-slate-200/80 shadow-lg">
            <img
              src={logoAlone}
              alt="RevRecovery Loading"
              className="w-14 h-14 object-contain animate-logo-pulse"
            />
            <div className="text-center space-y-0.5">
              <span className="text-sm font-bold text-slate-900 tracking-tight block">
                RevRecovery Orchestrator
              </span>
              <span className="text-xs text-slate-500 font-medium">
                {label}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'fullscreen') {
    return (
      <div className={cn('fixed inset-0 z-50 bg-white/90 backdrop-blur-sm flex flex-col items-center justify-center p-6', className)}>
        <img
          src={logoAlone}
          alt="RevRecovery Loading"
          className="w-16 h-16 object-contain animate-logo-pulse drop-shadow-md"
        />
        <div className="mt-4 text-center space-y-1">
          <h3 className="text-base font-bold text-slate-900 tracking-tight">RevRecovery</h3>
          <p className="text-xs text-slate-500 font-medium">{label}</p>
        </div>
      </div>
    );
  }

  // Default 'card' variant
  return (
    <div className={cn('flex flex-col items-center justify-center p-8 space-y-3', className)}>
      <img
        src={logoAlone}
        alt="RevRecovery Loading"
        className={cn('object-contain animate-logo-pulse', sizeClasses)}
      />
      {label && <span className="text-xs font-medium text-slate-500 text-center">{label}</span>}
    </div>
  );
};
