import React, { useState } from 'react';
import { RotateCw, Database, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Card, CardContent } from '../../../components/ui/card';
import { apiClient } from '../../../api/client';

interface DashboardSimulationControlsProps {
  onSimulationCompleted: () => void;
}

export const DashboardSimulationControls: React.FC<DashboardSimulationControlsProps> = ({
  onSimulationCompleted,
}) => {
  const [isRunningBaseline, setIsRunningBaseline] = useState(false);
  const [isRunningAi, setIsRunningAi] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const handleGenerateData = async () => {
    setIsGenerating(true);
    setStatusMessage(null);
    try {
      const res = await apiClient.generateData({ transaction_count: 100, failure_rate: 0.28 });
      setStatusMessage({
        text: `Synthetic Cohort Generated: ${res.transactions_generated} transactions & ${res.failures_generated} failures seeded.`,
        type: 'success',
      });
      onSimulationCompleted();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Server error';
      setStatusMessage({
        text: `Data generation failed: ${message}`,
        type: 'error',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRunBaseline = async () => {
    setIsRunningBaseline(true);
    setStatusMessage(null);
    try {
      const res = await apiClient.runBaselineSimulation({ limit: 50 });
      setStatusMessage({
        text: `Baseline benchmark executed on ${res.cases_processed} cases. Recovered ₹${res.metrics.total_recovered_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })} (${res.metrics.recovery_rate_percent}%).`,
        type: 'success',
      });
      onSimulationCompleted();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Server error';
      setStatusMessage({
        text: `Baseline run failed: ${message}`,
        type: 'error',
      });
    } finally {
      setIsRunningBaseline(false);
    }
  };

  const handleRunAi = async () => {
    setIsRunningAi(true);
    setStatusMessage(null);
    try {
      const res = await apiClient.runAiSimulation({ limit: 50, use_mock_llm: true });
      setStatusMessage({
        text: `AI Multi-Agent Orchestrator executed on ${res.cases_processed} cases. Recovered ₹${res.metrics.total_recovered_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })} (${res.metrics.recovery_rate_percent}%).`,
        type: 'success',
      });
      onSimulationCompleted();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Server error';
      setStatusMessage({
        text: `AI Orchestrator run failed: ${message}`,
        type: 'error',
      });
    } finally {
      setIsRunningAi(false);
    }
  };

  return (
    <Card className="bg-gradient-to-r from-slate-900 via-[#0c2340] to-slate-900 text-white border-slate-800 shadow-md overflow-hidden">
      <CardContent className="p-4 sm:p-5">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-500/20 text-brand-300 border border-brand-500/30">
                Track 03 Benchmark Engine
              </span>
              <span className="text-xs text-slate-400">Measured Recovery Evaluation</span>
            </div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              Batch Simulation & Strategy Execution
            </h2>
            <p className="text-xs text-slate-300 max-w-xl">
              Trigger independent batch runs on identical failure cohorts to verify measured revenue recovered, RAG precedent learning, and policy guardrails.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={handleGenerateData}
              disabled={isGenerating || isRunningBaseline || isRunningAi}
              className="bg-slate-800/80 border-slate-700 hover:bg-slate-700 text-slate-200 text-xs h-9 px-3"
            >
              {isGenerating ? (
                <img
                  src="/revenue-recovery-logo-alone.png"
                  alt="Loading"
                  className="w-3.5 h-3.5 mr-1.5 animate-logo-pulse object-contain inline-block"
                />
              ) : (
                <Database className="w-3.5 h-3.5 mr-1.5" />
              )}
              <span>{isGenerating ? 'Seeding Cohort...' : 'Seed Test Cohort'}</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleRunBaseline}
              disabled={isGenerating || isRunningBaseline || isRunningAi}
              className="bg-slate-800/80 border-slate-700 hover:bg-slate-700 text-sky-300 text-xs h-9 px-3"
            >
              {isRunningBaseline ? (
                <img
                  src="/revenue-recovery-logo-alone.png"
                  alt="Loading"
                  className="w-3.5 h-3.5 mr-1.5 animate-logo-pulse object-contain inline-block"
                />
              ) : (
                <RotateCw className="w-3.5 h-3.5 mr-1.5" />
              )}
              <span>{isRunningBaseline ? 'Simulating Baseline...' : 'Run Baseline Benchmark'}</span>
            </Button>

            <Button
              size="sm"
              onClick={handleRunAi}
              disabled={isGenerating || isRunningBaseline || isRunningAi}
              className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs h-9 px-4 shadow-lg shadow-brand-600/30"
            >
              {isRunningAi ? (
                <img
                  src="/revenue-recovery-logo-alone.png"
                  alt="Loading"
                  className="w-4 h-4 mr-1.5 animate-logo-pulse object-contain inline-block"
                />
              ) : (
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              )}
              <span>{isRunningAi ? 'Orchestrating Agents...' : 'Run AI Multi-Agent Recovery'}</span>
            </Button>
          </div>
        </div>

        {statusMessage && (
          <div
            className={`mt-3 p-2.5 rounded-lg border text-xs flex items-center gap-2 ${
              statusMessage.type === 'success'
                ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                : 'bg-rose-950/60 border-rose-800 text-rose-300'
            }`}
          >
            {statusMessage.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{statusMessage.text}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
