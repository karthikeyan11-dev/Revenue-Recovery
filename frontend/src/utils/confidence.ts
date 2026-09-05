export function getConfidenceBadgeVariant(confidence: number): 'success' | 'warning' | 'danger' {
  if (confidence >= 0.7) return 'success';
  if (confidence >= 0.4) return 'warning';
  return 'danger';
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.7) return 'text-emerald-400';
  if (confidence >= 0.4) return 'text-amber-400';
  return 'text-rose-400';
}
