// Core type definitions for Financial Risk Dashboard

// Risk assessment types
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface RiskFactor {
  factor_name: string;
  contribution_percentage: number;
  description: string;
}

export interface Account {
  account_id: string;
  risk_score: number; // 0-100
  risk_level: RiskLevel;
  risk_factors: RiskFactor[];
  feature_values: Record<string, number>;
  explanation: string;
  risk_reason?: string;
}

// Chart data types
export interface ValidationCurveData {
  param_values: number[];
  train_scores: number[];
  validation_scores: number[];
  param_name: string;
}

export interface LearningCurveData {
  train_sizes: number[];
  train_scores: number[];
  validation_scores: number[];
  train_scores_std?: number[];
  validation_scores_std?: number[];
}

export interface ConfusionMatrixData {
  matrix: number[][];
  labels: string[];
}

export interface ROCCurveData {
  fpr: number[];
  tpr: number[];
  auc: number;
  thresholds?: number[];
}

export interface PRCurveData {
  recall: number[];
  precision: number[];
  average_precision: number;
}

export interface LiftCurveData {
  percentiles: number[];
  cumulative_positives: number[];
  baseline: number[];
}

export interface ThresholdAnalysisData {
  thresholds: number[];
  precision: number[];
  recall: number[];
  f1_score: number[];
  optimal_threshold: number;
}

export interface FeatureImportanceData {
  features: string[];
  importance: number[];
}

// Dashboard state types
export interface DashboardFilters {
  risk_level: RiskLevel | null;
  search_query: string;
}

export interface DashboardCharts {
  validation_curve: ValidationCurveData | null;
  learning_curve: LearningCurveData | null;
  confusion_matrix: ConfusionMatrixData | null;
  roc_curve: ROCCurveData | null;
  pr_curve: PRCurveData | null;
  lift_curve: LiftCurveData | null;
  threshold_analysis: ThresholdAnalysisData | null;
  feature_importance: FeatureImportanceData | null;
}

export interface DashboardState {
  accounts: Account[];
  selectedAccount: Account | null;
  filters: DashboardFilters;
  charts: DashboardCharts;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// Dashboard actions
export type DashboardAction =
  | { type: 'LOAD_DATA_START' }
  | { type: 'LOAD_DATA_SUCCESS'; payload: DashboardData }
  | { type: 'LOAD_DATA_ERROR'; payload: string }
  | { type: 'SELECT_ACCOUNT'; payload: Account | null }
  | { type: 'UPDATE_FILTERS'; payload: Partial<DashboardFilters> }
  | { type: 'REFRESH_DATA' }
  | { type: 'CLEAR_ERROR' };

export interface DashboardData {
  accounts: Account[];
  charts: DashboardCharts;
}

// Component prop interfaces
export interface KPICardProps {
  title: string;
  value: number | string;
  formatter?: (value: number) => string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

export type ChartType =
  | 'validation_curve'
  | 'learning_curve'
  | 'confusion_matrix'
  | 'roc_curve'
  | 'pr_curve'
  | 'lift_curve'
  | 'threshold_analysis'
  | 'feature_importance';

export type ChartData =
  | ValidationCurveData
  | LearningCurveData
  | ConfusionMatrixData
  | ROCCurveData
  | PRCurveData
  | LiftCurveData
  | ThresholdAnalysisData
  | FeatureImportanceData;

export interface ChartContainerProps {
  title: string;
  chartType: ChartType;
  data: ChartData;
  height?: number;
  exportable?: boolean;
  onExport?: (format: 'png' | 'jpeg' | 'svg') => void;
}

export interface AccountListProps {
  accounts: Account[];
  filters: DashboardFilters;
  onFilterChange: (filters: Partial<DashboardFilters>) => void;
  onAccountSelect: (account: Account) => void;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export interface AccountDetailProps {
  account: Account;
  onBack: () => void;
}

export interface DataLoaderProps {
  onDataLoaded: (data: DashboardData) => void;
  onError: (error: Error) => void;
}

export interface CSVLoaderConfig {
  acceptedFormats: string[];
  maxFileSize: number;
  requiredColumns: string[];
}

export interface APILoaderConfig {
  endpoint: string;
  method: 'GET' | 'POST';
  headers?: Record<string, string>;
  refreshInterval?: number;
  retryAttempts: number;
  retryDelay: number;
}
