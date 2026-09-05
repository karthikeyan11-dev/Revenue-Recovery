export const DASHBOARD_CONSTANTS = {
  PAGE_TITLE: 'Dashboard',
  PAGE_SUBTITLE: 'AI Revenue Recovery Orchestrator Overview',
  
  KPI_TITLES: {
    REVENUE_AT_RISK: 'Revenue at Risk',
    AI_RECOVERED: 'AI Recovered Revenue',
    AI_RECOVERY_RATE: 'AI Recovery Rate',
    NET_ROI: 'Net Recovery ROI',
  },

  BANNER: {
    TITLE_PREFIX: 'Naive Baseline Completed:',
    VIEW_DETAILS: 'View Details',
    DISMISS: 'Dismiss',
  },

  CHARTS: {
    COMPARISON_TITLE: 'Revenue Recovery Comparison by Failure Reason',
    COMPARISON_SUBTITLE: 'Compare At Risk vs. Baseline vs. AI Orchestrator across failure reasons',
    DONUT_TITLE: 'Recovery by Failure Reason (AI)',
    DONUT_SUBTITLE: 'Distribution of AI recovered revenue across failure categories',
    LEGEND_AT_RISK: 'At Risk',
    LEGEND_BASELINE: 'Baseline (Retry Once)',
    LEGEND_AI: 'AI Orchestrator',
  },

  TABLES: {
    RECENT_CASES_TITLE: 'Recent Recovery Cases',
    RECENT_CASES_SUBTITLE: 'Latest payment failure cases processed by the orchestrator',
    VIEW_ALL_CASES: 'View All Cases',
    TOP_ACTIONS_TITLE: 'Top Recovery Actions (AI)',
    TOP_ACTIONS_SUBTITLE: 'Most effective interventions executed across all recovery cohorts',
    
    CASES_COLUMNS: {
      CASE_ID: 'Case ID',
      CUSTOMER: 'Customer',
      AMOUNT: 'Amount',
      STATUS: 'Status',
      SEGMENT: 'Failure Reason',
      RECOVERY_RATE: 'Recovery %',
      CREATED_AT: 'Created At',
    },

    ACTIONS_COLUMNS: {
      ACTION: 'Action',
      TYPE: 'Type',
      SUCCESS_RATE: 'Success Rate',
      ATTEMPTS: 'Attempts',
      RECOVERED: 'Recovered Amount',
    },
  },
} as const;
