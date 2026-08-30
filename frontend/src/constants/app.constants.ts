export const APP_CONSTANTS = {
  BRAND_NAME: 'RevRecovery',
  USER_NAME: 'Karthikeyan M',
  USER_ROLE: 'Tenant Admin',
  USER_INITIALS: 'KM',
  SYSTEM_STATUS: 'All Systems Operational',
  DATE_RANGE_LABEL: 'Aug 23 – Aug 29, 2025',
  EXPORT_BUTTON: 'Export',
  EXPORT_REPORT_BUTTON: 'Export Report',
  EXPORT_LOGS_BUTTON: 'Export Logs',
  EXPORT_CUSTOMERS_BUTTON: 'Export Customers',
  FILTER_BUTTON: 'Filters',
  RESET_BUTTON: 'Reset',
  SEARCH_PLACEHOLDER: 'Search...',
  SHOWING_TEXT: (from: number, to: number, total: number) =>
    `Showing ${from} to ${to} of ${total.toLocaleString()}`,
} as const;
