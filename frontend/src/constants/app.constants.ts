export const APP_CONSTANTS = {
  BRAND_NAME: 'RevRecovery',
  DATE_RANGE_LABEL: 'Aug 23 – Aug 29, 2025',
  FILTER_BUTTON: 'Filters',
  RESET_BUTTON: 'Reset',
  SEARCH_PLACEHOLDER: 'Search...',
  SHOWING_TEXT: (from: number, to: number, total: number) =>
    `Showing ${from} to ${to} of ${total.toLocaleString()}`,
} as const;

