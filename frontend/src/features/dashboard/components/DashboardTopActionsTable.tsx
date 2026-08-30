import React from 'react';
import { Badge } from '../../../components/ui/badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '../../../components/ui/table';
import { formatCurrency, formatPercent } from '../../../lib/utils';
import { DASHBOARD_CONSTANTS } from '../constants/dashboard.constants';
import type { DashboardTopActionsTableProps } from '../types/dashboard.types';

export const DashboardTopActionsTable: React.FC<DashboardTopActionsTableProps> = ({ actions }) => {
  const getTypeBadge = (type?: string) => {
    if (!type) return <Badge variant="secondary">STANDARD</Badge>;
    const normalized = type.toUpperCase().replace(/\s+/g, '_');
    switch (normalized) {
      case 'COMMUNICATION':
      case 'SEND_WHATSAPP':
      case 'SEND_EMAIL':
      case 'SEND_SMS':
        return <Badge variant="info">COMMUNICATION</Badge>;
      case 'PAYMENT_RETRY':
      case 'RETRY':
      case 'SEND_PAYMENT_LINK':
        return <Badge variant="purple">PAYMENT RETRY</Badge>;
      case 'INCENTIVE':
      case 'DISCOUNT':
      case 'OFFER_INCENTIVE':
        return <Badge variant="warning">INCENTIVE</Badge>;
      case 'ESCALATION':
      case 'HUMAN_REVIEW':
      case 'ESCALATE_TO_AGENT':
        return <Badge variant="destructive">ESCALATION</Badge>;
      default:
        return <Badge variant="secondary">{type}</Badge>;
    }
  };

  return (
    <Card className="bg-white border-slate-200/80 shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle>{DASHBOARD_CONSTANTS.TABLES.TOP_ACTIONS_TITLE}</CardTitle>
        <CardDescription>{DASHBOARD_CONSTANTS.TABLES.TOP_ACTIONS_SUBTITLE}</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.ACTIONS_COLUMNS.ACTION}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.ACTIONS_COLUMNS.TYPE}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.ACTIONS_COLUMNS.SUCCESS_RATE}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.ACTIONS_COLUMNS.ATTEMPTS}</TableHead>
              <TableHead>{DASHBOARD_CONSTANTS.TABLES.ACTIONS_COLUMNS.RECOVERED}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {actions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-slate-500 text-xs">
                  No recovery actions executed yet.
                </TableCell>
              </TableRow>
            ) : (
              actions.map((act, index) => {
                const actionLabel = act.action || act.action_type || 'Action';
                const actionType = act.action_type || act.type_display || 'Standard';
                const recoveredAmt = act.recovered_inr ?? act.recovered_amount_inr ?? 0;
                return (
                  <TableRow key={`${actionLabel}-${index}`}>
                    <TableCell className="font-semibold text-slate-900 text-xs">
                      {actionLabel}
                    </TableCell>
                    <TableCell>{getTypeBadge(actionType)}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${Math.min(100, act.success_rate_percent || 0)}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-slate-700">
                          {formatPercent(act.success_rate_percent || 0)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-xs font-medium text-slate-700">
                      {(act.attempts_count || 0).toLocaleString()}
                    </TableCell>
                    <TableCell className="font-semibold text-slate-900 text-xs">
                      {formatCurrency(recoveredAmt)}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};
