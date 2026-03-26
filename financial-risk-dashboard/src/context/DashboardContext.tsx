import React, { createContext, useReducer, useCallback, useContext } from 'react';
import type { DashboardState, DashboardAction, DashboardData, ChartType } from '../types';
import { dashboardReducer, initialDashboardState } from './dashboardReducer';
import { CSVProcessor } from '../data/CSVProcessor';
import { APIProcessor } from '../data/APIProcessor';

// Context value interface
export interface DashboardContextValue {
  state: DashboardState;
  dispatch: React.Dispatch<DashboardAction>;
  loadCSVData: (file: File) => Promise<void>;
  loadAPIData: (endpoint: string, headers?: Record<string, string>) => Promise<void>;
  exportChart: (chartType: ChartType, format: 'png' | 'jpeg' | 'svg') => void;
}

// Create context
export const DashboardContext = createContext<DashboardContextValue | null>(null);

// Provider props
interface DashboardProviderProps {
  children: React.ReactNode;
}

// Dashboard Provider component
export function DashboardProvider({ children }: DashboardProviderProps) {
  const [state, dispatch] = useReducer(dashboardReducer, initialDashboardState);

  // Load CSV data
  const loadCSVData = useCallback(async (file: File) => {
    dispatch({ type: 'LOAD_DATA_START' });

    try {
      const csvProcessor = new CSVProcessor();
      const data = await csvProcessor.parseFile(file);

      dispatch({
        type: 'LOAD_DATA_SUCCESS',
        payload: data,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load CSV data';
      dispatch({
        type: 'LOAD_DATA_ERROR',
        payload: errorMessage,
      });
      throw error;
    }
  }, []);

  // Load API data
  const loadAPIData = useCallback(async (endpoint: string, headers?: Record<string, string>) => {
    dispatch({ type: 'LOAD_DATA_START' });

    try {
      const apiProcessor = new APIProcessor({
        endpoint,
        method: 'GET',
        headers,
        retryAttempts: 3,
        retryDelay: 1000,
      });

      const data = await apiProcessor.fetchData();

      dispatch({
        type: 'LOAD_DATA_SUCCESS',
        payload: data,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load API data';
      dispatch({
        type: 'LOAD_DATA_ERROR',
        payload: errorMessage,
      });
      throw error;
    }
  }, []);

  // Export chart
  const exportChart = useCallback((chartType: ChartType, format: 'png' | 'jpeg' | 'svg') => {
    // This function will be called by chart components
    // The actual export logic is handled by ECharts' built-in functionality
    // This is a placeholder for triggering the export from the context
    console.log(`Exporting ${chartType} as ${format}`);
    
    // In a real implementation, this would:
    // 1. Find the chart instance by chartType
    // 2. Use ECharts' getDataURL() or getConnectedDataURL() method
    // 3. Trigger a download with the appropriate filename
    
    // For now, we'll let individual chart components handle their own exports
    // This function serves as a centralized API for future enhancements
  }, []);

  const contextValue: DashboardContextValue = {
    state,
    dispatch,
    loadCSVData,
    loadAPIData,
    exportChart,
  };

  return (
    <DashboardContext.Provider value={contextValue}>
      {children}
    </DashboardContext.Provider>
  );
}

// Custom hook for accessing Dashboard context
export function useDashboard() {
  const context = useContext(DashboardContext);
  
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  
  return context;
}
