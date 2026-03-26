import type { DashboardState, DashboardAction } from '../types';

// Initial state
export const initialDashboardState: DashboardState = {
  accounts: [],
  selectedAccount: null,
  filters: {
    risk_level: null,
    search_query: '',
  },
  charts: {
    validation_curve: null,
    learning_curve: null,
    confusion_matrix: null,
    roc_curve: null,
    pr_curve: null,
    lift_curve: null,
    threshold_analysis: null,
    feature_importance: null,
  },
  loading: false,
  error: null,
  lastUpdated: null,
};

// Dashboard reducer
export function dashboardReducer(
  state: DashboardState,
  action: DashboardAction
): DashboardState {
  switch (action.type) {
    case 'LOAD_DATA_START':
      return {
        ...state,
        loading: true,
        error: null,
      };

    case 'LOAD_DATA_SUCCESS':
      return {
        ...state,
        loading: false,
        accounts: action.payload.accounts,
        charts: action.payload.charts,
        lastUpdated: new Date(),
        error: null,
      };

    case 'LOAD_DATA_ERROR':
      return {
        ...state,
        loading: false,
        error: action.payload,
      };

    case 'SELECT_ACCOUNT':
      return {
        ...state,
        selectedAccount: action.payload,
      };

    case 'UPDATE_FILTERS':
      return {
        ...state,
        filters: {
          ...state.filters,
          ...action.payload,
        },
      };

    case 'REFRESH_DATA':
      return {
        ...state,
        loading: true,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
}
