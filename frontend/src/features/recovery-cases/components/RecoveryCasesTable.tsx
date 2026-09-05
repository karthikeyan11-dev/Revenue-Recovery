import React from 'react';
import { Eye, ChevronLeft, ChevronRight } from 'lucide-react';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Card, CardContent } from '../../../components/ui/card';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '../../../components/ui/table';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import { APP_CONSTANTS } from '../../../constants/app.constants';
import { RECOVERY_CASES_CONSTANTS } from '../constants/recovery-cases.constants';
import type { RecoveryCasesTableProps } from '../types/recovery-cases.types';

export const RecoveryCasesTable: React.FC<RecoveryCasesTableProps> = ({
  cases,
  total,
  inProgressCount,
  currentPage,
  pageSize,
  onPageChange,
  onViewCase,
}) => {
  const totalPages = Math.ceil(total / pageSize) || 1;
  const startRecord = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endRecord = Math.min(currentPage * pageSize, total);

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

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return <Badge variant="destructive">HIGH</Badge>;
      case 'MEDIUM':
        return <Badge variant="warning">MEDIUM</Badge>;
      case 'LOW':
        return <Badge variant="info">LOW</Badge>;
      default:
        return <Badge variant="outline">{priority}</Badge>;
    }
  };

  return (
    <Card className="bg-white border-slate-200/80 shadow-sm overflow-hidden">
      {/* Table Header Bar */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <span className="text-sm font-bold text-slate-900">
            Total Cases ({total.toLocaleString()})
          </span>
          <Badge variant="secondary" className="bg-blue-50 text-blue-700 font-medium">
            {inProgressCount} in progress
          </Badge>
        </div>
      </div>

      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{RECOVERY_CASES_CONSTANTS.TABLE_COLUMNS.CASE_ID}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.CUSTOMER}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.AMOUNT}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.STATUS}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.PRIORITY}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.RECOVERY_RATE}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.AGENTS_INVOLVED}</TableHead>
              <TableHead>{RECOVERY_CASES_COLUMNS.CURRENT_STEP}</TableHead>
              <TableHead className="text-right">{RECOVERY_CASES_COLUMNS.ACTIONS}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {cases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-12 text-slate-500 text-xs">
                  {RECOVERY_CASES_CONSTANTS.EMPTY_STATE}
                </TableCell>
              </TableRow>
            ) : (
              cases.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono text-xs font-semibold text-slate-900">
                    {c.id}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-slate-900 text-xs">{c.customer_name}</div>
                    <div className="text-[11px] text-slate-400">{c.customer_email}</div>
                  </TableCell>
                  <TableCell className="font-semibold text-slate-900 text-xs">
                    {formatCurrency(c.amount_at_risk ?? c.leak_amount ?? 0)}
                  </TableCell>
                  <TableCell>{getStatusBadge(c.status)}</TableCell>
                  <TableCell>{getPriorityBadge(c.priority)}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <div className="w-14 bg-slate-100 rounded-full h-1.5 overflow-hidden">
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
                  <TableCell>
                    <Badge variant="outline" className="text-slate-600 bg-slate-50 text-[11px] font-medium">
                      {Array.isArray(c.agents_involved)
                        ? `${c.agents_involved.length} agents`
                        : typeof c.agents_involved === 'number'
                        ? `${c.agents_involved} agents`
                        : '5 agents'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-slate-700 font-medium">
                    {c.current_step || (c.status === 'RECOVERED' ? 'Resolution Complete' : c.status === 'ESCALATED' ? 'Escalated to Human' : c.status === 'FAILED' ? 'Execution Finished' : 'In Orchestration')}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewCase(c.id)}
                      className="h-8 w-8 p-0 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      <Eye className="w-4 h-4" />
                      <span className="sr-only">View Case Details</span>
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            {APP_CONSTANTS.SHOWING_TEXT(startRecord, endRecord, total)}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage <= 1}
              onClick={() => onPageChange(currentPage - 1)}
              className="h-8 px-2.5 text-xs text-slate-600 border-slate-200 shadow-sm"
            >
              <ChevronLeft className="w-3.5 h-3.5 mr-1" />
              <span>Previous</span>
            </Button>
            <span className="text-xs text-slate-600 px-2">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage >= totalPages}
              onClick={() => onPageChange(currentPage + 1)}
              className="h-8 px-2.5 text-xs text-slate-600 border-slate-200 shadow-sm"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
const RECOVERY_CASES_COLUMNS = RECOVERY_CASES_CONSTANTS.TABLE_COLUMNS;
