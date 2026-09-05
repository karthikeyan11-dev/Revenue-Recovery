export const RECOVERY_CASES_CONSTANTS = {
  PAGE_TITLE: 'Recovery Cases',
  PAGE_SUBTITLE: 'View and manage all failed payment recovery cases',
  
  SEARCH_PLACEHOLDER: 'Search by Case ID, customer name, email...',
  
  FILTER_LABELS: {
    ALL_STATUSES: 'All Statuses',
    ALL_REASONS: 'All Failure Reasons',
    ALL_PRIORITIES: 'All Priorities',
    RESET_FILTERS: 'Reset Filters',
    STATUS: 'Status',
    REASON: 'Failure Reason',
    PRIORITY: 'Priority',
  },

  STATUS_OPTIONS: [
    { value: 'all', label: 'All Statuses' },
    { value: 'OPEN', label: 'Open' },
    { value: 'IN_PROGRESS', label: 'In Progress' },
    { value: 'RECOVERED', label: 'Recovered' },
    { value: 'FAILED', label: 'Failed' },
    { value: 'ESCALATED', label: 'Escalated' },
    { value: 'BLOCKED', label: 'Blocked' },
  ],

  REASON_OPTIONS: [
    { value: 'all', label: 'All Failure Reasons' },
    { value: 'INSUFFICIENT_FUNDS', label: 'Insufficient Funds' },
    { value: 'NETWORK_ERROR', label: 'Network Error' },
    { value: 'EXPIRED_CARD', label: 'Expired Card' },
    { value: 'BANK_DECLINED', label: 'Bank Declined' },
    { value: 'AUTHENTICATION_FAILED', label: 'Auth Failed' },
    { value: 'USER_DROPOFF', label: 'User Dropoff' },
    { value: 'LIMIT_EXCEEDED', label: 'Limit Exceeded' },
  ],


  PRIORITY_OPTIONS: [
    { value: 'all', label: 'All Priorities' },
    { value: 'HIGH', label: 'High Priority' },
    { value: 'MEDIUM', label: 'Medium Priority' },
    { value: 'LOW', label: 'Low Priority' },
  ],

  TABLE_COLUMNS: {
    CASE_ID: 'Case ID',
    CUSTOMER: 'Customer',
    AMOUNT: 'Amount',
    STATUS: 'Status',
    PRIORITY: 'Priority',
    RECOVERY_RATE: 'Recovery %',
    AGENTS_INVOLVED: 'Agents Involved',
    CURRENT_STEP: 'Current Step',
    ACTIONS: 'Actions',
  },

  DRAWER: {
    TITLE: 'Recovery Case Details',
    SUBTITLE: 'Full audit timeline, agent decisions, and executed recovery actions',
    OVERVIEW_TAB: 'Case Overview',
    TIMELINE_TAB: 'Agent Timeline',
    ACTIONS_TAB: 'Actions & Outcomes',
    PRECEDENTS_TAB: 'RAG Precedents (ChromaDB)',
    CUSTOMER_INFO: 'Customer Information',
    FINANCIAL_INFO: 'Financial Summary',
    CLOSE_BUTTON: 'Close',
  },

  EMPTY_STATE: 'No recovery cases found matching the selected filters.',
} as const;
