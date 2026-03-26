import { describe, it, expect } from 'vitest';
import { dashboardReducer, initialDashboardState } from '../dashboardReducer';
import type { DashboardState, DashboardData } from '../../types';

describe('dashboardReducer', () => {
  describe('LOAD_DATA_START', () => {
    it('should set loading to true and clear error', () => {
      const state: DashboardState = {
        ...initialDashboardState,
        error: 'Previous error',
      };

      const newState = dashboardReducer(state, { type: 'LOAD_DATA_START' });

      expect(newState.loading).toBe(true);
      expect(newState.error).toBe(null);
    });
  });

  describe('LOAD_DATA_SUCCESS', () => {
    it('should update accounts and charts with loaded data', () => {
      const mockData: DashboardData = {
        accounts: [
          {
            account_id: 'ACC001',
            risk_score: 85,
            risk_level: 'HIGH',
            risk_factors: [],
            feature_values: {},
            explanation: 'Test account',
          },
        ],
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
      };

      const newState = dashboardReducer(initialDashboardState, {
        type: 'LOAD_DATA_SUCCESS',
        payload: mockData,
      });

      expect(newState.loading).toBe(false);
      expect(newState.error).toBe(null);
      expect(newState.accounts).toEqual(mockData.accounts);
      expect(newState.charts).toEqual(mockData.charts);
      expect(newState.lastUpdated).toBeInstanceOf(Date);
    });
  });

  describe('LOAD_DATA_ERROR', () => {
    it('should set error message and stop loading', () => {
      const errorMessage = 'Failed to load data';

      const newState = dashboardReducer(initialDashboardState, {
        type: 'LOAD_DATA_ERROR',
        payload: errorMessage,
      });

      expect(newState.loading).toBe(false);
      expect(newState.error).toBe(errorMessage);
    });
  });

  describe('SELECT_ACCOUNT', () => {
    it('should set selected account', () => {
      const account = {
        account_id: 'ACC001',
        risk_score: 85,
        risk_level: 'HIGH' as const,
        risk_factors: [],
        feature_values: {},
        explanation: 'Test account',
      };

      const newState = dashboardReducer(initialDashboardState, {
        type: 'SELECT_ACCOUNT',
        payload: account,
      });

      expect(newState.selectedAccount).toEqual(account);
    });

    it('should clear selected account when payload is null', () => {
      const state: DashboardState = {
        ...initialDashboardState,
        selectedAccount: {
          account_id: 'ACC001',
          risk_score: 85,
          risk_level: 'HIGH',
          risk_factors: [],
          feature_values: {},
          explanation: 'Test account',
        },
      };

      const newState = dashboardReducer(state, {
        type: 'SELECT_ACCOUNT',
        payload: null,
      });

      expect(newState.selectedAccount).toBe(null);
    });
  });

  describe('UPDATE_FILTERS', () => {
    it('should update risk_level filter', () => {
      const newState = dashboardReducer(initialDashboardState, {
        type: 'UPDATE_FILTERS',
        payload: { risk_level: 'HIGH' },
      });

      expect(newState.filters.risk_level).toBe('HIGH');
      expect(newState.filters.search_query).toBe('');
    });

    it('should update search_query filter', () => {
      const newState = dashboardReducer(initialDashboardState, {
        type: 'UPDATE_FILTERS',
        payload: { search_query: 'ACC001' },
      });

      expect(newState.filters.search_query).toBe('ACC001');
      expect(newState.filters.risk_level).toBe(null);
    });

    it('should update multiple filters at once', () => {
      const newState = dashboardReducer(initialDashboardState, {
        type: 'UPDATE_FILTERS',
        payload: { risk_level: 'CRITICAL', search_query: 'test' },
      });

      expect(newState.filters.risk_level).toBe('CRITICAL');
      expect(newState.filters.search_query).toBe('test');
    });

    it('should preserve existing filters when updating partial filters', () => {
      const state: DashboardState = {
        ...initialDashboardState,
        filters: {
          risk_level: 'HIGH',
          search_query: 'existing',
        },
      };

      const newState = dashboardReducer(state, {
        type: 'UPDATE_FILTERS',
        payload: { search_query: 'new' },
      });

      expect(newState.filters.risk_level).toBe('HIGH');
      expect(newState.filters.search_query).toBe('new');
    });
  });

  describe('REFRESH_DATA', () => {
    it('should set loading to true', () => {
      const newState = dashboardReducer(initialDashboardState, {
        type: 'REFRESH_DATA',
      });

      expect(newState.loading).toBe(true);
    });

    it('should preserve existing data during refresh', () => {
      const state: DashboardState = {
        ...initialDashboardState,
        accounts: [
          {
            account_id: 'ACC001',
            risk_score: 85,
            risk_level: 'HIGH',
            risk_factors: [],
            feature_values: {},
            explanation: 'Test',
          },
        ],
      };

      const newState = dashboardReducer(state, {
        type: 'REFRESH_DATA',
      });

      expect(newState.loading).toBe(true);
      expect(newState.accounts).toEqual(state.accounts);
    });
  });

  describe('CLEAR_ERROR', () => {
    it('should clear error message', () => {
      const state: DashboardState = {
        ...initialDashboardState,
        error: 'Some error',
      };

      const newState = dashboardReducer(state, {
        type: 'CLEAR_ERROR',
      });

      expect(newState.error).toBe(null);
    });
  });

  describe('default case', () => {
    it('should return unchanged state for unknown action', () => {
      const state = initialDashboardState;
      const unknownAction = { type: 'UNKNOWN_ACTION' } as any;

      const newState = dashboardReducer(state, unknownAction);

      expect(newState).toBe(state);
    });
  });
});
