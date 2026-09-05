import React from 'react';
import { ArrowUpRight } from 'lucide-react';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '../../../components/ui/table';
import { formatCurrency, formatDate, formatPercent } from '../../../lib/utils';
import { DASHBOARD_CONSTANTS } from '../constants/dashboard.constants';
import type { DashboardRecentCasesTableProps } from '../types/dashboard.types';

export const DashboardRecentCasesTable: React.FC<DashboardRecentCasesTableProps> = ({
  cases,
  onViewAll,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'RECOVERED':
        return <Badge variant="success">Recovered</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="warning">In Progress</Badge>;
      case 'OPEN':
        return <Badge variant="info">Open</Badge>;
      case 'ESCALATED':
        return <Badge variant="destructive">Escalated</Badge>;
      case 'BLOCKED':
        return <Badge variant="destructive">Blocked</Badge>;
      case 'FAILED':
        return <Badge variant="secondary">Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getReasonBadge = (reason?: string, code?: string) => {
    const val = reason || code;
    if (!val) return <Badge variant="outline">Technical</Badge>;
    const formatted = val.replace(/_/g, ' ').replace(/\b\w/g, (ch) => ch.toUpperCase());
    const normalized = val.toUpperCase().replace(/\s+/g, '_');
    switch (normalized) {
      case 'BANK_DECLINED':
        return <Badge variant="info">{formatted}</Badge>;
      case 'AUTHENTICATION_FAILED':
        return <Badge variant="warning">{formatted}</Badge>;
      case 'NETWORK_ERROR':
        return <Badge variant="default" className="bg-sky-600 text-white hover:bg-sky-600">{formatted}</Badge>;
      case 'INSUFFICIENT_FUNDS':
        return <Badge variant="secondary">{formatted}</Badge>;
      case 'EXPIRED_CARD':
        return <Badge variant="purple">{formatted}</Badge>;
      case 'USER_DROPOFF':
        return <Badge variant="outline">{formatted}</Badge>;
      case 'LIMIT_EXCEEDED':
        return <Badge variant="destructive">{formatted}</Badge>;
      default:
        return <Badge variant="secondary">{formatted}</Badge>;
    }
  };

  return (
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle>{DASHBOARD_CONSTANTS.TABLES.RECENT_CASES_TITLE}</CardTitle>
          <CardDescription>{DASHBOARD_CONSTANTS.TABLES.RECENT_CASES_SUBTITLE}</CardDescription>
        </div>
        {onViewAll && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onViewAll}
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 text-xs font-semibold flex items-center space-x-1"
          >
            <span>{DASHBOARD_CONSTANTS.TABLES.VIEW_ALL_CASES}</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Button>
        )}
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.CASE_ID}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.CUSTOMER}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.AMOUNT}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.STATUS}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.SEGMENT}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.RECOVERY_RATE}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.CASES_COLUMNS.CREATED_AT}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {cases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-slate-500 text-xs">
                  No recovery cases recorded yet.
                </TableCell>
              </TableRow>
            ) : (
              cases.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono text-xs font-semibold text-slate-900">
                    {c.id}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-slate-900">{c.customer_name}</div>
                    <div className="text-xs text-slate-400">{c.customer_email}</div>
                  </TableCell>
                  <TableCell className="font-semibold text-slate-900">
                    {formatCurrency(c.amount_at_risk ?? c.leak_amount ?? 0)}
                  </TableCell>
                  <TableCell>{getStatusBadge(c.status)}</TableCell>
                  <TableCell>{getReasonBadge(c.failure_reason, c.failure_code)}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full"
                          style={{ width: `${Math.min(100, c.recovery_rate_percent)}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-slate-700">
                        {formatPercent(c.recovery_rate_percent)}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-xs text-slate-500">
                    {formatDate(c.created_at)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};
