import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import {
  Sparkles,
  X,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Move,
  ChevronDown,
  ChevronUp,
  Award,
  Zap,
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { formatCurrency, formatPercent } from '../../lib/utils';
import type { RecoveryDiagnosticResponse } from '../../types/api.types';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';

interface FloatingDiagnosticWidgetProps {
  hasNewInsight?: boolean;
  onClearNewInsight?: () => void;
}

export const FloatingDiagnosticWidget: React.FC<FloatingDiagnosticWidgetProps> = ({
  hasNewInsight = false,
  onClearNewInsight,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [diagnosticData, setDiagnosticData] = useState<RecoveryDiagnosticResponse | null>(null);
  const [showEscalatedDetails, setShowEscalatedDetails] = useState(false);

  // Position state (pixels from top-left) - lazy initializer on mount
  const [position, setPosition] = useState<{ x: number; y: number } | null>(() => {
    if (typeof window !== 'undefined') {
      return {
        x: Math.max(20, window.innerWidth - 84),
        y: Math.max(100, window.innerHeight - 100),
      };
    }
    return null;
  });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const startMousePos = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const hasMovedSignificantly = useRef(false);

  // Fetch diagnostic data with optional live LLM forced regeneration
  const fetchDiagnostics = useCallback(async (forceRefresh: boolean = false) => {
    if (forceRefresh) {
      setIsRegenerating(true);
    } else {
      setIsLoading(true);
    }
    try {
      const data = await apiClient.getDashboardDiagnostics({ force_refresh: forceRefresh });
      setDiagnosticData(data);
    } catch (err) {
      console.error('Failed to load recovery diagnostics:', err);
    } finally {
      setIsLoading(false);
      setIsRegenerating(false);
    }
  }, []);

  // Re-fetch when opened or when hasNewInsight triggers
  useEffect(() => {
    if (!isOpen && !hasNewInsight) return;
    const timer = setTimeout(() => {
      void fetchDiagnostics(false);
    }, 0);
    return () => clearTimeout(timer);
  }, [isOpen, hasNewInsight, fetchDiagnostics]);

  // Handle Drag Start
  const handleMouseDown = (e: React.MouseEvent) => {
    // Only drag with left click
    if (e.button !== 0) return;
    setIsDragging(true);
    hasMovedSignificantly.current = false;
    startMousePos.current = { x: e.clientX, y: e.clientY };
    dragStartPos.current = position || { x: 0, y: 0 };
  };

  // Handle Drag Move & Window boundaries
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;

      const deltaX = e.clientX - startMousePos.current.x;
      const deltaY = e.clientY - startMousePos.current.y;

      if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) {
        hasMovedSignificantly.current = true;
      }

      const widgetWidth = 64;
      const widgetHeight = 64;
      const maxX = window.innerWidth - widgetWidth - 10;
      const maxY = window.innerHeight - widgetHeight - 10;

      const newX = Math.min(maxX, Math.max(10, dragStartPos.current.x + deltaX));
      const newY = Math.min(maxY, Math.max(60, dragStartPos.current.y + deltaY));

      setPosition({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const handleIconClick = () => {
    // If the mouse was dragged across the screen, don't trigger click toggle
    if (hasMovedSignificantly.current) return;

    if (!isOpen) {
      if (onClearNewInsight) onClearNewInsight();
      fetchDiagnostics();
    }
    setIsOpen(!isOpen);
  };

  if (!position) return null;

  const isAiAhead = diagnosticData?.verdict === 'AI_AHEAD';
  const hasEscalated = (diagnosticData?.escalated_cases?.length || 0) > 0;

  return (
    <>
      {/* 1. MOVABLE FLOATING ICON BUTTON */}
      <div
        style={{
          position: 'fixed',
          left: `${position.x}px`,
          top: `${position.y}px`,
          zIndex: 9999,
          touchAction: 'none',
        }}
        className="select-none"
      >
        <div className="relative group">
          {/* Glowing pulse ring if new insight is ready */}
          {hasNewInsight && (
            <span className="absolute -inset-1 rounded-full bg-emerald-400 opacity-75 animate-ping" />
          )}

          <button
            type="button"
            onMouseDown={handleMouseDown}
            onClick={handleIconClick}
            className={`relative w-14 h-14 rounded-full shadow-2xl flex items-center justify-center cursor-grab active:cursor-grabbing transition-transform duration-200 border-2 ${
              hasNewInsight
                ? 'bg-gradient-to-tr from-emerald-600 to-teal-500 text-white border-emerald-300 ring-4 ring-emerald-400/40 animate-bounce'
                : isOpen
                ? 'bg-slate-900 text-white border-slate-700 ring-2 ring-blue-500/50 scale-105'
                : 'bg-gradient-to-tr from-[#0c2340] to-blue-700 text-white border-blue-400/50 hover:scale-110 hover:shadow-blue-500/25'
            }`}
            title="Drag anywhere • Click for AI Recovery Diagnostic"
          >
            {hasNewInsight ? (
              <Zap className="w-6 h-6 animate-pulse text-amber-300" />
            ) : isOpen ? (
              <X className="w-6 h-6 text-white" />
            ) : (
              <Sparkles className="w-6 h-6 text-blue-200" />
            )}

            {/* Notification Badge */}
            {hasNewInsight && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-4 w-4 bg-amber-500 border-2 border-slate-900" />
              </span>
            )}
          </button>

          {/* Quick Tooltip on Hover */}
          {!isOpen && (
            <div className="absolute right-16 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center px-3 py-1.5 rounded-lg bg-slate-900/95 text-white text-xs font-semibold whitespace-nowrap shadow-xl border border-slate-700 backdrop-blur-sm pointer-events-none">
              <Move className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
              {hasNewInsight ? '✨ New Diagnostic Insight Ready!' : 'AI Recovery Forensic Intelligence'}
            </div>
          )}
        </div>
      </div>

      {/* 2. EXPANDABLE DIAGNOSTIC INTELLIGENCE CARD (PORTAL TO DOCUMENT.BODY) */}
      {isOpen &&
        typeof document !== 'undefined' &&
        createPortal(
          <div
            className="fixed inset-0 z-[10000] w-screen h-screen flex items-center justify-center p-4 sm:p-6 bg-slate-950/60 backdrop-blur-md animate-in fade-in duration-200"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setIsOpen(false);
              }
            }}
          >
            <Card
              className="w-full max-w-2xl bg-white/95 backdrop-blur-md border-slate-200 shadow-2xl rounded-2xl overflow-hidden max-h-[90vh] flex flex-col relative z-[10001]"
              onClick={(e) => e.stopPropagation()}
            >
            {/* CARD HEADER */}
            <div className="p-4 sm:p-5 bg-gradient-to-r from-slate-900 via-[#0c2340] to-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-300">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white tracking-tight">
                      AI Recovery Forensic Intelligence
                    </h3>
                    <Badge className="bg-blue-500/20 text-blue-300 border-blue-400/30 text-[10px] uppercase font-bold">
                      Track 03 Diagnostic
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-300">
                    Analytical root-cause breakdown comparing AI Multi-Agent vs. Naive Baseline
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => fetchDiagnostics(true)}
                  disabled={isLoading || isRegenerating}
                  className="h-8 px-2.5 text-xs font-semibold bg-white/10 hover:bg-white/20 text-white border-white/20 flex items-center gap-1.5"
                  title="Force fresh live LLM reasoning call bypassing cohort cache"
                >
                  <Sparkles className={`w-3.5 h-3.5 text-amber-300 ${isRegenerating ? 'animate-spin' : ''}`} />
                  <span>{isRegenerating ? 'Analyzing...' : 'Regenerate'}</span>
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => fetchDiagnostics(false)}
                  disabled={isLoading || isRegenerating}
                  className="h-8 w-8 p-0 text-slate-400 hover:text-white hover:bg-slate-800"
                  title="Refresh Cohort Telemetry"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8 p-0 text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* CARD BODY (Scrollable) */}
            <CardContent className="p-5 sm:p-6 overflow-y-auto space-y-5 text-slate-800">
              {isLoading && !diagnosticData ? (
                <div className="py-12 flex flex-col items-center justify-center space-y-3">
                  <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
                  <p className="text-sm font-medium text-slate-500">
                    Synthesizing cohort telemetry and calling live LLM...
                  </p>
                </div>
              ) : diagnosticData ? (
                <>
                  {/* DYNAMIC VERDICT BANNER */}
                  <div
                    className={`p-4 rounded-xl border ${
                      isAiAhead
                        ? 'bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50/60 border-emerald-200 text-emerald-950'
                        : 'bg-gradient-to-r from-amber-50 via-indigo-50/40 to-amber-50/60 border-amber-200 text-slate-900'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                          isAiAhead
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}
                      >
                        {isAiAhead ? (
                          <Award className="w-5 h-5" />
                        ) : (
                          <ShieldCheck className="w-5 h-5" />
                        )}
                      </div>
                      <div className="space-y-1.5 w-full">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
                              Executive Cohort Diagnosis
                            </span>
                            <Badge
                              variant="outline"
                              className={`text-[11px] font-bold ${
                                isAiAhead
                                  ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                                  : 'bg-amber-100 text-amber-800 border-amber-300'
                              }`}
                            >
                              {isAiAhead ? 'AI Outperformed Baseline' : 'Enterprise Guardrails Active'}
                            </Badge>
                          </div>
                        </div>

                        <h4 className="text-base font-bold text-slate-900">
                          {diagnosticData.headline}
                        </h4>

                        {/* Summary text or regenerating skeleton */}
                        {isRegenerating ? (
                          <div className="space-y-1.5 py-1">
                            <div className="h-3.5 bg-slate-200/80 rounded animate-pulse w-full" />
                            <div className="h-3.5 bg-slate-200/80 rounded animate-pulse w-4/5" />
                          </div>
                        ) : (
                          <p className="text-xs text-slate-700 leading-relaxed">
                            {diagnosticData.summary}
                          </p>
                        )}

                        {/* Honest Real Model Attribution Tag */}
                        {diagnosticData.real_model_attribution ? (
                          <div className="flex items-center gap-1.5 text-[11px] text-slate-500 pt-1 font-medium">
                            <Sparkles className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                            <span>
                              Analysis synthesized live via{' '}
                              <strong className="text-slate-800 font-semibold">
                                {diagnosticData.real_model_attribution}
                              </strong>
                            </span>
                            {diagnosticData.llm_reasoning_status === 'cached' && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 font-mono ml-1">
                                Cached for cohort run
                              </span>
                            )}
                          </div>
                        ) : diagnosticData.llm_reasoning_status === 'unavailable' ? (
                          <div className="flex items-center gap-1.5 text-[11px] text-amber-800 pt-1 font-medium">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                            <span>
                              Live LLM reasoning temporarily unavailable. Telemetry below is computed directly from live PostgreSQL state.
                            </span>
                          </div>
                        ) : null}
                      </div>
                    </div>
                  </div>

                  {/* COMPARATIVE METRICS GRID */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {/* Metric 1: Revenue Outcome */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase">
                        AI Gross Revenue
                      </span>
                      <div className="text-base font-bold text-slate-900 mt-1">
                        {formatCurrency(diagnosticData.metrics.ai_recovered)}
                      </div>
                      <div className="text-[11px] font-medium text-slate-600 mt-0.5">
                        Base: {formatCurrency(diagnosticData.metrics.baseline_recovered)}
                      </div>
                      <div
                        className={`text-[11px] font-bold mt-1 ${
                          diagnosticData.metrics.rev_diff_inr >= 0
                            ? 'text-emerald-700'
                            : 'text-amber-700'
                        }`}
                      >
                        {diagnosticData.metrics.rev_diff_inr >= 0
                          ? `+${formatCurrency(diagnosticData.metrics.rev_diff_inr)} Diff`
                          : `-${formatCurrency(Math.abs(diagnosticData.metrics.rev_diff_inr))} Diff`}
                      </div>
                    </div>

                    {/* Metric 2: Win Rate */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase">
                        AI Win Rate
                      </span>
                      <div className="text-base font-bold text-emerald-700 mt-1">
                        {formatPercent(diagnosticData.metrics.ai_case_rate)}
                      </div>
                      <div className="text-[11px] font-medium text-slate-600 mt-0.5">
                        Base: {formatPercent(diagnosticData.metrics.baseline_case_rate)}
                      </div>
                      <div className="text-[11px] font-bold text-emerald-700 mt-1">
                        +{formatPercent(diagnosticData.metrics.case_rate_diff_percent)} Lead
                      </div>
                    </div>

                    {/* Metric 3: Cases Rescued */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase">
                        Accounts Saved
                      </span>
                      <div className="text-base font-bold text-slate-900 mt-1">
                        {diagnosticData.metrics.ai_recovered_cases} /{' '}
                        {diagnosticData.metrics.total_cases}
                      </div>
                      <div className="text-[11px] font-medium text-slate-600 mt-0.5">
                        Base: {diagnosticData.metrics.baseline_recovered_cases} cases
                      </div>
                      <div className="text-[11px] font-bold text-emerald-700 mt-1">
                        +{diagnosticData.metrics.case_diff_count} extra customers
                      </div>
                    </div>

                    {/* Metric 4: Escalation Queue Telemetry */}
                    <div className="p-3 rounded-xl bg-purple-50/60 border border-purple-200/80">
                      <span className="text-[11px] font-semibold text-purple-900 uppercase">
                        Human Queue
                      </span>
                      <div className="text-base font-bold text-purple-900 mt-1">
                        {formatCurrency(diagnosticData.metrics.escalated_revenue_inr)}
                      </div>
                      <div className="text-[11px] font-medium text-purple-700 mt-0.5">
                        {diagnosticData.metrics.escalated_cases_count} whale cases
                      </div>
                      <div className="text-[11px] font-bold text-purple-800 mt-1">
                        Held for compliance
                      </div>
                    </div>
                  </div>

                  {/* WHY THIS HAPPENED: DETAILED FORENSIC DRIVERS */}
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
                      Analytical Root-Cause Factors
                    </h5>
                    <div className="space-y-2">
                      {diagnosticData.primary_reasons.map((reason, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-50 border border-slate-200/70 text-xs text-slate-700"
                        >
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                          <span className="leading-relaxed">{reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* ESCALATED CASES TELEMETRY (IF ANY ARE HELD IN QUEUE) */}
                  {hasEscalated && (
                    <div className="border border-purple-200 rounded-xl overflow-hidden bg-purple-50/30">
                      <button
                        type="button"
                        onClick={() => setShowEscalatedDetails(!showEscalatedDetails)}
                        className="w-full p-3 flex items-center justify-between text-left hover:bg-purple-50/60 transition-colors"
                      >
                        <div className="flex items-center space-x-2">
                          <ShieldCheck className="w-4 h-4 text-purple-700" />
                          <span className="text-xs font-bold text-purple-900">
                            Enterprise Escalation Telemetry: {diagnosticData.escalated_cases.length}{' '}
                            Whale Transactions Held (
                            {formatCurrency(diagnosticData.metrics.escalated_revenue_inr)})
                          </span>
                        </div>
                        {showEscalatedDetails ? (
                          <ChevronUp className="w-4 h-4 text-purple-700" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-purple-700" />
                        )}
                      </button>

                      {showEscalatedDetails && (
                        <div className="p-3 pt-0 border-t border-purple-100 space-y-2">
                          <p className="text-[11px] text-purple-800 font-medium leading-relaxed">
                            These high-value transactions were blocked from unverified automated
                            retries to comply with Visa/Mastercard retry limits and merchant safety
                            thresholds. They are queued for manual concierge review:
                          </p>
                          <div className="space-y-1.5 max-h-40 overflow-y-auto">
                            {diagnosticData.escalated_cases.map((c) => (
                              <div
                                key={c.case_id}
                                className="p-2 rounded bg-white border border-purple-200/80 text-[11px] flex items-center justify-between gap-2"
                              >
                                <div className="truncate">
                                  <span className="font-bold text-slate-900">
                                    {formatCurrency(c.amount)}
                                  </span>{' '}
                                  <span className="text-slate-500">
                                    ({c.failure_reason.replace('_', ' ')})
                                  </span>
                                  <p className="text-slate-600 truncate text-[10px]">
                                    {c.reasoning}
                                  </p>
                                </div>
                                <Badge
                                  variant="outline"
                                  className="bg-purple-50 text-purple-700 border-purple-200 text-[9px] shrink-0"
                                >
                                  {c.policy_rule}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <div className="py-8 text-center text-slate-500 text-xs">
                  No diagnostic data available. Run the AI Multi-Agent simulation to generate fresh
                  cohort diagnostics.
                </div>
              )}
            </CardContent>

            {/* CARD FOOTER */}
            <div className="p-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
              <span>Drag the floating icon anywhere on your screen</span>
              <Button size="sm" onClick={() => setIsOpen(false)} className="h-8 px-4 text-xs font-semibold">
                Close Diagnostic
              </Button>
            </div>
          </Card>
        </div>,
        document.body
      )}
    </>
  );
};
