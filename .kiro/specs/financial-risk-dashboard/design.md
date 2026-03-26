# Design Document: Financial Risk Dashboard

## Overview

The Financial Risk Dashboard is a professional-grade web application for visualizing machine learning model risk assessment results and account analysis information. The system provides comprehensive risk visualization capabilities including KPI cards, 8 types of evaluation charts (Validation Curve, Learning Curve, Confusion Matrix, ROC Curve, PR Curve, Lift Curve, Threshold Analysis, Feature Importance), suspicious account lists, and detailed single-account analysis.

### Design Goals

1. **Professional Visualization**: Clean, professional, hierarchical interface design meeting fintech product standards
2. **Comprehensive Evaluation**: Cover multiple dimensions including model performance, risk distribution, and account analysis
3. **Big Data Support**: Efficient visualization for large datasets (up to 10,000 accounts)
4. **Flexible Data Sources**: Support both CSV file uploads and API data loading
5. **Responsive Design**: Adapt to different screen sizes for optimal display
6. **Accessibility**: WCAG AA compliant for inclusive user experience

### Technology Stack

- **Frontend Framework**: React 18 with TypeScript for type safety and component reusability
- **Charting Library**: Apache ECharts 5.x for professional, interactive visualizations
- **UI Framework**: Tailwind CSS for responsive, utility-first styling
- **State Management**: React Context API with useReducer for centralized state management
- **Data Validation**: Zod for runtime type validation of CSV and API data
- **Build Tool**: Vite for fast development and optimized production builds
- **Testing**: Vitest for unit tests, React Testing Library for component tests

## Architecture

### System Architecture

The dashboard follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ KPI Cards│  │  Charts  │  │ Account  │  │ Account │ │
│  │          │  │          │  │   List   │  │ Detail  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │    State     │  │   Business   │  │   Layout      │ │
│  │  Management  │  │    Logic     │  │   Manager     │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │     CSV      │  │     API      │  │     Data      │ │
│  │    Loader    │  │    Loader    │  │  Validation   │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Data Loading**: User uploads CSV or system fetches from API
2. **Validation**: Data is validated against schema using Zod
3. **State Update**: Validated data is stored in application state
4. **Component Rendering**: React components subscribe to state and render visualizations
5. **User Interaction**: User interactions trigger state updates and re-renders
6. **Export**: Charts can be exported as images using ECharts built-in functionality

### Component Hierarchy

```
App
├── DashboardLayout
│   ├── Header
│   │   ├── Title
│   │   ├── RefreshButton
│   │   └── DataSourceSelector
│   ├── KPISection
│   │   ├── KPICard (Total Accounts)
│   │   ├── KPICard (High Risk Accounts)
│   │   ├── KPICard (Risk Ratio)
│   │   └── KPICard (Average Risk Score)
│   ├── ChartsSection
│   │   ├── ChartContainer (Validation Curve)
│   │   ├── ChartContainer (Learning Curve)
│   │   ├── ChartContainer (Confusion Matrix)
│   │   ├── ChartContainer (ROC Curve)
│   │   ├── ChartContainer (PR Curve)
│   │   ├── ChartContainer (Lift Curve)
│   │   ├── ChartContainer (Threshold Analysis)
│   │   └── ChartContainer (Feature Importance)
│   └── AccountsSection
│       ├── AccountList
│       │   ├── FilterBar
│       │   ├── SearchBar
│       │   ├── AccountTable
│       │   └── Pagination
│       └── AccountDetail (conditional)
└── ErrorBoundary
```

## Components and Interfaces

### Core Data Types

```typescript
// Risk assessment types
type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

interface Account {
  account_id: string;
  risk_score: number; // 0-100
  risk_level: RiskLevel;
  risk_factors: RiskFactor[];
  feature_values: Record<string, number>;
  explanation: string;
}

interface RiskFactor {
  factor_name: string;
  contribution_percentage: number;
  description: string;
}

// Chart data types
interface ValidationCurveData {
  param_values: number[];
  train_scores: number[];
  validation_scores: number[];
  param_name: string;
}

interface LearningCurveData {
  train_sizes: number[];
  train_scores: number[];
  validation_scores: number[];
  train_scores_std?: number[];
  validation_scores_std?: number[];
}

interface ConfusionMatrixData {
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
}

interface ROCCurveData {
  fpr: number[];
  tpr: number[];
  auc: number;
}

interface PRCurveData {
  recall: number[];
  precision: number[];
  average_precision: number;
}

interface LiftCurveData {
  percentiles: number[];
  cumulative_positives: number[];
  baseline: number[];
}

interface ThresholdAnalysisData {
  thresholds: number[];
  precision: number[];
  recall: number[];
  f1_score: number[];
  optimal_threshold: number;
}

interface FeatureImportanceData {
  features: string[];
  importance: number[];
}

// Dashboard state
interface DashboardState {
  accounts: Account[];
  selectedAccount: Account | null;
  filters: {
    risk_level: RiskLevel | null;
    search_query: string;
  };
  charts: {
    validation_curve: ValidationCurveData | null;
    learning_curve: LearningCurveData | null;
    confusion_matrix: ConfusionMatrixData | null;
    roc_curve: ROCCurveData | null;
    pr_curve: PRCurveData | null;
    lift_curve: LiftCurveData | null;
    threshold_analysis: ThresholdAnalysisData | null;
    feature_importance: FeatureImportanceData | null;
  };
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}
```

### Component Interfaces

#### KPICard Component

```typescript
interface KPICardProps {
  title: string;
  value: number | string;
  formatter?: (value: number) => string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

// Usage
<KPICard
  title="Total Accounts"
  value={totalAccounts}
  formatter={(v) => v.toLocaleString()}
  icon={<UsersIcon />}
/>
```

#### ChartContainer Component

```typescript
interface ChartContainerProps {
  title: string;
  chartType: ChartType;
  data: ChartData;
  height?: number;
  exportable?: boolean;
  onExport?: (format: 'png' | 'jpeg' | 'svg') => void;
}

type ChartType =
  | 'validation_curve'
  | 'learning_curve'
  | 'confusion_matrix'
  | 'roc_curve'
  | 'pr_curve'
  | 'lift_curve'
  | 'threshold_analysis'
  | 'feature_importance';

type ChartData =
  | ValidationCurveData
  | LearningCurveData
  | ConfusionMatrixData
  | ROCCurveData
  | PRCurveData
  | LiftCurveData
  | ThresholdAnalysisData
  | FeatureImportanceData;
```

#### AccountList Component

```typescript
interface AccountListProps {
  accounts: Account[];
  filters: {
    risk_level: RiskLevel | null;
    search_query: string;
  };
  onFilterChange: (filters: Partial<AccountListProps['filters']>) => void;
  onAccountSelect: (account: Account) => void;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}
```

#### AccountDetail Component

```typescript
interface AccountDetailProps {
  account: Account;
  onBack: () => void;
}
```

#### DataLoader Component

```typescript
interface DataLoaderProps {
  onDataLoaded: (data: DashboardData) => void;
  onError: (error: Error) => void;
}

interface DashboardData {
  accounts: Account[];
  charts: DashboardState['charts'];
}

// CSV Loader
interface CSVLoaderConfig {
  acceptedFormats: string[];
  maxFileSize: number;
  requiredColumns: string[];
}

// API Loader
interface APILoaderConfig {
  endpoint: string;
  method: 'GET' | 'POST';
  headers?: Record<string, string>;
  refreshInterval?: number;
  retryAttempts: number;
  retryDelay: number;
}
```

### Data Validation Schemas

```typescript
import { z } from 'zod';

const RiskLevelSchema = z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']);

const RiskFactorSchema = z.object({
  factor_name: z.string(),
  contribution_percentage: z.number().min(0).max(100),
  description: z.string(),
});

const AccountSchema = z.object({
  account_id: z.string(),
  risk_score: z.number().min(0).max(100),
  risk_level: RiskLevelSchema,
  risk_factors: z.array(RiskFactorSchema),
  feature_values: z.record(z.number()),
  explanation: z.string(),
});

const ValidationCurveSchema = z.object({
  param_values: z.array(z.number()),
  train_scores: z.array(z.number()),
  validation_scores: z.array(z.number()),
  param_name: z.string(),
});

// Similar schemas for other chart types...

const DashboardDataSchema = z.object({
  accounts: z.array(AccountSchema),
  charts: z.object({
    validation_curve: ValidationCurveSchema.nullable(),
    learning_curve: z.any().nullable(), // Define specific schemas
    confusion_matrix: z.any().nullable(),
    roc_curve: z.any().nullable(),
    pr_curve: z.any().nullable(),
    lift_curve: z.any().nullable(),
    threshold_analysis: z.any().nullable(),
    feature_importance: z.any().nullable(),
  }),
});
```

## Data Models

### State Management

The application uses React Context API with useReducer for centralized state management:

```typescript
// Actions
type DashboardAction =
  | { type: 'LOAD_DATA_START' }
  | { type: 'LOAD_DATA_SUCCESS'; payload: DashboardData }
  | { type: 'LOAD_DATA_ERROR'; payload: string }
  | { type: 'SELECT_ACCOUNT'; payload: Account | null }
  | { type: 'UPDATE_FILTERS'; payload: Partial<DashboardState['filters']> }
  | { type: 'REFRESH_DATA' }
  | { type: 'CLEAR_ERROR' };

// Reducer
function dashboardReducer(
  state: DashboardState,
  action: DashboardAction
): DashboardState {
  switch (action.type) {
    case 'LOAD_DATA_START':
      return { ...state, loading: true, error: null };
    
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
      return { ...state, loading: false, error: action.payload };
    
    case 'SELECT_ACCOUNT':
      return { ...state, selectedAccount: action.payload };
    
    case 'UPDATE_FILTERS':
      return {
        ...state,
        filters: { ...state.filters, ...action.payload },
      };
    
    case 'REFRESH_DATA':
      return { ...state, loading: true };
    
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    
    default:
      return state;
  }
}

// Context
interface DashboardContextValue {
  state: DashboardState;
  dispatch: React.Dispatch<DashboardAction>;
  loadCSVData: (file: File) => Promise<void>;
  loadAPIData: () => Promise<void>;
  exportChart: (chartType: ChartType, format: 'png' | 'jpeg' | 'svg') => void;
}

const DashboardContext = React.createContext<DashboardContextValue | null>(null);
```

### Data Processing Pipeline

```typescript
// CSV Processing
class CSVProcessor {
  async parseFile(file: File): Promise<DashboardData> {
    const text = await file.text();
    const rows = this.parseCSV(text);
    const validated = this.validateData(rows);
    return this.transformData(validated);
  }

  private parseCSV(text: string): any[] {
    // Use Papa Parse or similar library
    // Return array of row objects
  }

  private validateData(rows: any[]): any[] {
    // Validate using Zod schemas
    // Throw descriptive errors for invalid data
  }

  private transformData(rows: any[]): DashboardData {
    // Transform CSV rows into DashboardData structure
  }
}

// API Processing
class APIProcessor {
  constructor(private config: APILoaderConfig) {}

  async fetchData(): Promise<DashboardData> {
    const response = await this.makeRequest();
    const validated = this.validateResponse(response);
    return validated;
  }

  private async makeRequest(attempt = 1): Promise<any> {
    try {
      const response = await fetch(this.config.endpoint, {
        method: this.config.method,
        headers: this.config.headers,
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      if (attempt < this.config.retryAttempts) {
        await this.delay(this.config.retryDelay);
        return this.makeRequest(attempt + 1);
      }
      throw error;
    }
  }

  private validateResponse(data: any): DashboardData {
    return DashboardDataSchema.parse(data);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### Chart Configuration

Each chart type has a dedicated configuration function that returns ECharts options:

```typescript
// Validation Curve Configuration
function getValidationCurveOptions(data: ValidationCurveData): EChartsOption {
  return {
    title: {
      text: `Validation Curve - ${data.param_name}`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        // Custom tooltip formatting
      },
    },
    legend: {
      data: ['Training Score', 'Validation Score'],
      bottom: 10,
    },
    xAxis: {
      type: 'category',
      data: data.param_values,
      name: data.param_name,
      nameLocation: 'middle',
      nameGap: 30,
    },
    yAxis: {
      type: 'value',
      name: 'Score',
      min: 0,
      max: 1,
    },
    series: [
      {
        name: 'Training Score',
        type: 'line',
        data: data.train_scores,
        smooth: true,
        lineStyle: { color: '#3b82f6' },
      },
      {
        name: 'Validation Score',
        type: 'line',
        data: data.validation_scores,
        smooth: true,
        lineStyle: { color: '#10b981' },
      },
    ],
    toolbox: {
      feature: {
        saveAsImage: { pixelRatio: 2 },
      },
    },
  };
}

// ROC Curve Configuration
function getROCCurveOptions(data: ROCCurveData): EChartsOption {
  return {
    title: {
      text: `ROC Curve (AUC = ${data.auc.toFixed(3)})`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'value',
      name: 'False Positive Rate',
      min: 0,
      max: 1,
    },
    yAxis: {
      type: 'value',
      name: 'True Positive Rate',
      min: 0,
      max: 1,
    },
    series: [
      {
        name: 'ROC Curve',
        type: 'line',
        data: data.fpr.map((fpr, i) => [fpr, data.tpr[i]]),
        smooth: true,
        lineStyle: { color: '#3b82f6', width: 2 },
      },
      {
        name: 'Random Classifier',
        type: 'line',
        data: [[0, 0], [1, 1]],
        lineStyle: { color: '#94a3b8', type: 'dashed' },
      },
    ],
  };
}

// Confusion Matrix Configuration
function getConfusionMatrixOptions(data: ConfusionMatrixData): EChartsOption {
  const matrix = [
    [data.true_negatives, data.false_positives],
    [data.false_negatives, data.true_positives],
  ];

  return {
    title: {
      text: 'Confusion Matrix',
      left: 'center',
    },
    tooltip: {
      position: 'top',
    },
    grid: {
      height: '50%',
      top: '15%',
    },
    xAxis: {
      type: 'category',
      data: ['Negative', 'Positive'],
      name: 'Predicted',
      splitArea: { show: true },
    },
    yAxis: {
      type: 'category',
      data: ['Positive', 'Negative'],
      name: 'Actual',
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: Math.max(...matrix.flat()),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#f0f9ff', '#0369a1'],
      },
    },
    series: [
      {
        type: 'heatmap',
        data: matrix.flatMap((row, i) =>
          row.map((value, j) => [j, 1 - i, value])
        ),
        label: {
          show: true,
          fontSize: 16,
        },
      },
    ],
  };
}

// Feature Importance Configuration
function getFeatureImportanceOptions(data: FeatureImportanceData): EChartsOption {
  // Sort and take top 10
  const sorted = data.features
    .map((feature, i) => ({ feature, importance: data.importance[i] }))
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 10);

  return {
    title: {
      text: 'Feature Importance (Top 10)',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    grid: {
      left: '20%',
      right: '10%',
      bottom: '10%',
      top: '15%',
    },
    xAxis: {
      type: 'value',
      name: 'Importance',
    },
    yAxis: {
      type: 'category',
      data: sorted.map(s => s.feature),
      inverse: true,
    },
    series: [
      {
        type: 'bar',
        data: sorted.map(s => s.importance),
        itemStyle: {
          color: '#3b82f6',
        },
      },
    ],
  };
}
```

### Performance Optimization

```typescript
// Virtual scrolling for account list
interface VirtualScrollConfig {
  itemHeight: number;
  containerHeight: number;
  overscan: number;
}

function useVirtualScroll(
  items: Account[],
  config: VirtualScrollConfig
) {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / config.itemHeight);
    const visibleCount = Math.ceil(config.containerHeight / config.itemHeight);
    const end = start + visibleCount + config.overscan;
    
    return {
      start: Math.max(0, start - config.overscan),
      end: Math.min(items.length, end),
    };
  }, [scrollTop, items.length, config]);

  const visibleItems = useMemo(
    () => items.slice(visibleRange.start, visibleRange.end),
    [items, visibleRange]
  );

  return {
    visibleItems,
    totalHeight: items.length * config.itemHeight,
    offsetY: visibleRange.start * config.itemHeight,
    onScroll: (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    },
  };
}

// Chart data sampling for large datasets
function sampleChartData<T>(data: T[], maxPoints: number): T[] {
  if (data.length <= maxPoints) return data;
  
  const step = data.length / maxPoints;
  const sampled: T[] = [];
  
  for (let i = 0; i < maxPoints; i++) {
    const index = Math.floor(i * step);
    sampled.push(data[index]);
  }
  
  return sampled;
}

// Memoized chart options
function useChartOptions<T>(
  data: T | null,
  getOptions: (data: T) => EChartsOption
): EChartsOption | null {
  return useMemo(() => {
    if (!data) return null;
    return getOptions(data);
  }, [data, getOptions]);
}
```


### Responsive Layout Implementation

```typescript
// Breakpoint system
const breakpoints = {
  mobile: 640,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
};

// Layout configuration
interface LayoutConfig {
  kpiColumns: number;
  chartColumns: number;
  chartHeight: number;
}

function useResponsiveLayout(): LayoutConfig {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (windowWidth < breakpoints.mobile) {
    return { kpiColumns: 1, chartColumns: 1, chartHeight: 300 };
  } else if (windowWidth < breakpoints.tablet) {
    return { kpiColumns: 2, chartColumns: 1, chartHeight: 350 };
  } else if (windowWidth < breakpoints.desktop) {
    return { kpiColumns: 2, chartColumns: 2, chartHeight: 400 };
  } else {
    return { kpiColumns: 4, chartColumns: 2, chartHeight: 450 };
  }
}

// Chart resize handling
function useChartResize(chartRef: React.RefObject<HTMLDivElement>) {
  useEffect(() => {
    if (!chartRef.current) return;

    const resizeObserver = new ResizeObserver(() => {
      const chart = echarts.getInstanceByDom(chartRef.current!);
      if (chart) {
        chart.resize();
      }
    });

    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, [chartRef]);
}
```

### Accessibility Implementation

```typescript
// Keyboard navigation
function useKeyboardNavigation(
  items: Account[],
  onSelect: (account: Account) => void
) {
  const [focusedIndex, setFocusedIndex] = useState(0);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex(prev => Math.min(prev + 1, items.length - 1));
          break;
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          onSelect(items[focusedIndex]);
          break;
      }
    },
    [items, focusedIndex, onSelect]
  );

  return { focusedIndex, handleKeyDown };
}

// ARIA announcements
function useAriaAnnouncement() {
  const announce = useCallback((message: string) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }, []);

  return announce;
}

// Color contrast utilities
const colorPalette = {
  // WCAG AA compliant colors
  risk: {
    critical: '#dc2626', // Red 600
    high: '#ea580c', // Orange 600
    medium: '#ca8a04', // Yellow 600
    low: '#16a34a', // Green 600
  },
  chart: {
    primary: '#3b82f6', // Blue 500
    secondary: '#10b981', // Green 500
    tertiary: '#8b5cf6', // Purple 500
    quaternary: '#f59e0b', // Amber 500
  },
  text: {
    primary: '#0f172a', // Slate 900
    secondary: '#475569', // Slate 600
    disabled: '#94a3b8', // Slate 400
  },
  background: {
    primary: '#ffffff',
    secondary: '#f8fafc', // Slate 50
    tertiary: '#f1f5f9', // Slate 100
  },
};
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

1. **Chart Responsiveness**: Requirements 2.7, 3.7, 4.7, 5.7, 6.7, 7.7, 8.7, 9.7, and 14.5 all test that charts resize when containers change. These can be consolidated into a single property about chart resize behavior.

2. **Risk Level Color Mapping**: Requirements 10.3 and 11.3 both test that risk levels map to specific colors. These can be consolidated into a single property.

3. **State Updates**: Requirements 12.7, 13.6, and 17.4 all test that dashboard components update when data changes. These can be consolidated into a single property about state propagation.

4. **Automatic Refresh**: Requirements 13.7 and 17.5 both test interval-based data refresh. These can be consolidated into a single property.

5. **Error Handling**: Requirements 20.1, 20.2, 20.3, and 20.4 all test that errors are displayed. These can be consolidated into a single property about error display.

The following properties represent the unique, testable behaviors after eliminating redundancy:

### Property 1: Number Formatting with Thousand Separators

*For any* number displayed in a KPI card, the formatted output should include thousand separators (commas) at the appropriate positions.

**Validates: Requirements 1.5**

### Property 2: Chart Responsiveness

*For any* chart component and any container size change, the chart should resize to fit the new container dimensions.

**Validates: Requirements 2.7, 3.7, 4.7, 5.7, 6.7, 7.7, 8.7, 9.7, 14.5**

### Property 3: AUC Score Calculation

*For any* ROC curve data with valid FPR and TPR arrays, the calculated AUC score should match the trapezoidal rule integration of the curve.

**Validates: Requirements 5.3**

### Property 4: Average Precision Calculation

*For any* PR curve data with valid Precision and Recall arrays, the calculated Average Precision score should match the area under the PR curve.

**Validates: Requirements 6.3**

### Property 5: Lift Value Calculation

*For any* lift curve data with valid percentiles and cumulative positives, the calculated lift values should correctly represent the ratio of model performance to random selection at each percentile.

**Validates: Requirements 7.4**

### Property 6: Feature Importance Sorting

*For any* feature importance data, the rendered chart should display features sorted by importance in descending order.

**Validates: Requirements 9.2**

### Property 7: Feature Importance Top-N Limiting

*For any* feature importance data with more than 10 features, the rendered chart should display only the top 10 features by importance.

**Validates: Requirements 9.6**

### Property 8: Account List Sorting

*For any* collection of accounts, the account list should display accounts sorted by risk_score in descending order.

**Validates: Requirements 10.1**

### Property 9: Risk Level Color Mapping

*For any* risk level value (LOW, MEDIUM, HIGH, CRITICAL), the system should map it to the correct color (green, yellow, orange, red respectively).

**Validates: Requirements 10.3, 11.3**

### Property 10: Account List Pagination

*For any* collection of accounts, the account list should display exactly 20 accounts per page (or fewer on the last page).

**Validates: Requirements 10.4**

### Property 11: Risk Level Filtering

*For any* collection of accounts and any selected risk level filter, the filtered account list should contain only accounts matching that risk level.

**Validates: Requirements 10.5**

### Property 12: Account ID Search

*For any* collection of accounts and any search query, the filtered account list should contain only accounts whose account_id contains the search query (case-insensitive).

**Validates: Requirements 10.6**

### Property 13: CSV Column Validation

*For any* uploaded CSV file, if the file is missing required columns (account_id, risk_score, risk_level), the validation should fail with a descriptive error message.

**Validates: Requirements 12.2**

### Property 14: CSV Parsing Round-Trip

*For any* valid CSV file containing account data, parsing the file should produce account objects that, when serialized back to CSV format, preserve all data values.

**Validates: Requirements 12.3**

### Property 15: Risk Score Range Validation

*For any* risk_score value in CSV or API data, if the value is outside the range [0, 100], the validation should fail with a descriptive error message.

**Validates: Requirements 12.4**

### Property 16: Risk Level Enum Validation

*For any* risk_level value in CSV or API data, if the value is not one of LOW, MEDIUM, HIGH, or CRITICAL, the validation should fail with a descriptive error message.

**Validates: Requirements 12.5**

### Property 17: CSV Validation Error Display

*For any* CSV file that fails validation, the system should display an error message that includes the specific validation issue and the line number where it occurred.

**Validates: Requirements 12.6**

### Property 18: API Response Validation

*For any* API response, if the response does not match the expected schema (missing required fields or incorrect types), the validation should fail with a descriptive error message.

**Validates: Requirements 13.3**

### Property 19: JSON Parsing Round-Trip

*For any* valid dashboard data object, serializing to JSON and then deserializing should produce an equivalent object with all data preserved.

**Validates: Requirements 13.4**

### Property 20: API Retry Logic

*For any* failed API request, the system should retry the request up to 3 times before displaying an error message.

**Validates: Requirements 13.5**

### Property 21: Automatic Refresh Interval

*For any* configured refresh interval, the system should reload data at that interval (within a tolerance of ±100ms) when automatic refresh is enabled.

**Validates: Requirements 13.7, 17.5**

### Property 22: Layout Responsiveness

*For any* window resize event, the layout should update to reflect the new screen size without requiring a page reload.

**Validates: Requirements 14.4**

### Property 23: Color Palette Consistency

*For any* component that uses colors, the colors should come from the defined color palette (no arbitrary color values).

**Validates: Requirements 15.1, 15.6**

### Property 24: Chart Export DPI

*For any* chart exported as PNG, the image resolution should be at least 300 DPI.

**Validates: Requirements 16.3**

### Property 25: Export Filename Format

*For any* exported chart, the filename should follow the format: `{chart_type}_{timestamp}.{extension}` where timestamp is in ISO 8601 format.

**Validates: Requirements 16.5**

### Property 26: State Preservation During Refresh

*For any* data refresh operation, the current user interactions (selected filters, search query, selected account) should be preserved after the refresh completes.

**Validates: Requirements 17.7**

### Property 27: Virtual Scrolling Rendering

*For any* account list with more than 100 accounts, only the visible rows (plus a small overscan buffer) should be rendered in the DOM.

**Validates: Requirements 18.2**

### Property 28: Chart Data Sampling

*For any* chart data with more than 1000 data points, the system should sample or aggregate the data to reduce the number of rendered points while preserving the visual shape of the curve.

**Validates: Requirements 18.3**

### Property 29: Lazy Loading Implementation

*For any* chart component, the component should not be loaded until it is needed (either visible in viewport or explicitly requested).

**Validates: Requirements 18.6**

### Property 30: Data Caching

*For any* expensive calculation (KPI aggregations, chart data transformations), the result should be cached and reused if the input data has not changed.

**Validates: Requirements 18.7**

### Property 31: Keyboard Navigation

*For any* interactive element in the dashboard, the element should be reachable and operable using only keyboard input (Tab, Enter, Arrow keys, Escape).

**Validates: Requirements 19.1**

### Property 32: ARIA Labels Presence

*For any* interactive element or dynamic content region, appropriate ARIA labels (aria-label, aria-labelledby, aria-describedby) should be present.

**Validates: Requirements 19.2, 19.4**

### Property 33: Color Contrast Compliance

*For any* text element and its background, the color contrast ratio should meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text).

**Validates: Requirements 19.3**

### Property 34: ARIA Live Regions

*For any* dynamic content update (data refresh, filter change, error display), the update should be announced to screen readers using ARIA live regions.

**Validates: Requirements 19.5**

### Property 35: Form Label Association

*For any* form input element, the input should have an associated label element (via htmlFor/id or aria-labelledby).

**Validates: Requirements 19.6**

### Property 36: Focus Indicators

*For any* focusable element, when focused via keyboard navigation, a visible focus indicator should be displayed.

**Validates: Requirements 19.7**

### Property 37: Error Message Display

*For any* error condition (data loading failure, validation failure, chart rendering failure), the system should display a user-friendly error message describing the issue.

**Validates: Requirements 20.1, 20.2, 20.3, 20.4**

### Property 38: Error Logging

*For any* error that occurs in the system, the error should be logged to the browser console with sufficient detail for debugging (error message, stack trace, context).

**Validates: Requirements 20.7**


## Error Handling

### Error Categories

The system handles four main categories of errors:

1. **Data Loading Errors**: CSV upload failures, API request failures, network errors
2. **Validation Errors**: Invalid data format, missing required fields, out-of-range values
3. **Rendering Errors**: Chart rendering failures, component mount errors
4. **User Input Errors**: Invalid filter selections, malformed search queries

### Error Handling Strategy

```typescript
// Error types
class DashboardError extends Error {
  constructor(
    message: string,
    public category: ErrorCategory,
    public recoverable: boolean,
    public context?: any
  ) {
    super(message);
    this.name = 'DashboardError';
  }
}

type ErrorCategory = 'data_loading' | 'validation' | 'rendering' | 'user_input';

// Error handler
class ErrorHandler {
  handle(error: Error | DashboardError): ErrorDisplayInfo {
    // Log to console
    console.error('[Dashboard Error]', {
      message: error.message,
      stack: error.stack,
      context: error instanceof DashboardError ? error.context : undefined,
    });

    // Determine user-facing message
    if (error instanceof DashboardError) {
      return this.handleDashboardError(error);
    } else {
      return this.handleUnknownError(error);
    }
  }

  private handleDashboardError(error: DashboardError): ErrorDisplayInfo {
    switch (error.category) {
      case 'data_loading':
        return {
          title: 'Data Loading Failed',
          message: error.message,
          actions: error.recoverable
            ? [{ label: 'Retry', action: 'retry' }]
            : [{ label: 'Dismiss', action: 'dismiss' }],
        };

      case 'validation':
        return {
          title: 'Data Validation Error',
          message: error.message,
          details: error.context?.validationErrors,
          actions: [{ label: 'Dismiss', action: 'dismiss' }],
        };

      case 'rendering':
        return {
          title: 'Display Error',
          message: 'Unable to render this component. Please try refreshing.',
          actions: [
            { label: 'Refresh', action: 'refresh' },
            { label: 'Dismiss', action: 'dismiss' },
          ],
        };

      case 'user_input':
        return {
          title: 'Invalid Input',
          message: error.message,
          actions: [{ label: 'Dismiss', action: 'dismiss' }],
        };
    }
  }

  private handleUnknownError(error: Error): ErrorDisplayInfo {
    return {
      title: 'Unexpected Error',
      message: 'An unexpected error occurred. Please try refreshing the page.',
      actions: [
        { label: 'Refresh Page', action: 'reload' },
        { label: 'Dismiss', action: 'dismiss' },
      ],
    };
  }
}

interface ErrorDisplayInfo {
  title: string;
  message: string;
  details?: any;
  actions: Array<{ label: string; action: string }>;
}
```

### Error Boundaries

```typescript
// React Error Boundary for catching rendering errors
class DashboardErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[Error Boundary]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          onReset={() => this.setState({ hasError: false, error: null })}
        />
      );
    }

    return this.props.children;
  }
}

// Chart-specific error boundary
function ChartErrorBoundary({ children, chartType }: {
  children: React.ReactNode;
  chartType: string;
}) {
  return (
    <ErrorBoundary
      fallback={
        <div className="chart-error">
          <p>Unable to render {chartType} chart</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}
```

### Validation Error Details

```typescript
// CSV validation errors
interface CSVValidationError {
  line: number;
  column: string;
  value: any;
  error: string;
}

function validateCSVRow(row: any, lineNumber: number): CSVValidationError[] {
  const errors: CSVValidationError[] = [];

  // Check required columns
  if (!row.account_id) {
    errors.push({
      line: lineNumber,
      column: 'account_id',
      value: row.account_id,
      error: 'Missing required field',
    });
  }

  // Validate risk_score range
  if (row.risk_score !== undefined) {
    const score = Number(row.risk_score);
    if (isNaN(score) || score < 0 || score > 100) {
      errors.push({
        line: lineNumber,
        column: 'risk_score',
        value: row.risk_score,
        error: 'Risk score must be between 0 and 100',
      });
    }
  }

  // Validate risk_level enum
  const validLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
  if (row.risk_level && !validLevels.includes(row.risk_level)) {
    errors.push({
      line: lineNumber,
      column: 'risk_level',
      value: row.risk_level,
      error: `Risk level must be one of: ${validLevels.join(', ')}`,
    });
  }

  return errors;
}

// Format validation errors for display
function formatValidationErrors(errors: CSVValidationError[]): string {
  if (errors.length === 0) return '';

  const grouped = errors.reduce((acc, error) => {
    const key = error.line;
    if (!acc[key]) acc[key] = [];
    acc[key].push(error);
    return acc;
  }, {} as Record<number, CSVValidationError[]>);

  return Object.entries(grouped)
    .map(([line, lineErrors]) => {
      const errorMessages = lineErrors
        .map(e => `  - ${e.column}: ${e.error}`)
        .join('\n');
      return `Line ${line}:\n${errorMessages}`;
    })
    .join('\n\n');
}
```

### Retry Logic

```typescript
// Exponential backoff retry
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt < maxAttempts) {
        const delay = baseDelay * Math.pow(2, attempt - 1);
        console.log(`Retry attempt ${attempt} failed, waiting ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw new DashboardError(
    `Failed after ${maxAttempts} attempts: ${lastError!.message}`,
    'data_loading',
    false,
    { originalError: lastError }
  );
}
```

## Testing Strategy

### Dual Testing Approach

The Financial Risk Dashboard will use both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, and integration points
- **Property Tests**: Verify universal properties across all inputs using randomized testing

This dual approach ensures that:
- Unit tests catch concrete bugs in specific scenarios
- Property tests verify general correctness across a wide range of inputs
- Together, they provide confidence in both specific behaviors and general system properties

### Testing Tools

- **Unit Testing**: Vitest for test runner, React Testing Library for component testing
- **Property-Based Testing**: fast-check library for JavaScript/TypeScript
- **Mocking**: Vitest's built-in mocking for API calls and file uploads
- **Coverage**: Vitest coverage reports with minimum 80% coverage target

### Property-Based Testing Configuration

Each property test will:
- Run a minimum of 100 iterations to ensure thorough randomized testing
- Include a comment tag referencing the design document property
- Use fast-check generators to create random test data
- Verify the property holds for all generated inputs

Tag format: `// Feature: financial-risk-dashboard, Property {number}: {property_text}`

Example property test:

```typescript
import fc from 'fast-check';
import { describe, it, expect } from 'vitest';

describe('Property Tests', () => {
  // Feature: financial-risk-dashboard, Property 1: Number Formatting with Thousand Separators
  it('should format all numbers with thousand separators', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 10000000 }),
        (num) => {
          const formatted = formatNumberWithSeparators(num);
          
          // Verify thousand separators are present for numbers >= 1000
          if (num >= 1000) {
            expect(formatted).toMatch(/,/);
          }
          
          // Verify the formatted string can be parsed back to the original number
          const parsed = parseInt(formatted.replace(/,/g, ''), 10);
          expect(parsed).toBe(num);
        }
      ),
      { numRuns: 100 }
    );
  });

  // Feature: financial-risk-dashboard, Property 8: Account List Sorting
  it('should sort accounts by risk_score in descending order', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            account_id: fc.string(),
            risk_score: fc.float({ min: 0, max: 100 }),
            risk_level: fc.constantFrom('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
          }),
          { minLength: 1, maxLength: 100 }
        ),
        (accounts) => {
          const sorted = sortAccountsByRiskScore(accounts);
          
          // Verify descending order
          for (let i = 0; i < sorted.length - 1; i++) {
            expect(sorted[i].risk_score).toBeGreaterThanOrEqual(
              sorted[i + 1].risk_score
            );
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  // Feature: financial-risk-dashboard, Property 15: Risk Score Range Validation
  it('should reject risk scores outside [0, 100] range', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.float({ max: -0.01 }),
          fc.float({ min: 100.01 })
        ),
        (invalidScore) => {
          const result = validateRiskScore(invalidScore);
          
          expect(result.valid).toBe(false);
          expect(result.error).toContain('between 0 and 100');
        }
      ),
      { numRuns: 100 }
    );
  });

  // Feature: financial-risk-dashboard, Property 19: JSON Parsing Round-Trip
  it('should preserve data through JSON serialization round-trip', () => {
    fc.assert(
      fc.property(
        fc.record({
          accounts: fc.array(
            fc.record({
              account_id: fc.string(),
              risk_score: fc.float({ min: 0, max: 100 }),
              risk_level: fc.constantFrom('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
              risk_factors: fc.array(
                fc.record({
                  factor_name: fc.string(),
                  contribution_percentage: fc.float({ min: 0, max: 100 }),
                  description: fc.string(),
                })
              ),
              feature_values: fc.dictionary(fc.string(), fc.float()),
              explanation: fc.string(),
            })
          ),
        }),
        (dashboardData) => {
          const serialized = JSON.stringify(dashboardData);
          const deserialized = JSON.parse(serialized);
          
          expect(deserialized).toEqual(dashboardData);
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Unit Testing Strategy

Unit tests will focus on:

1. **Component Rendering**: Verify components render with correct props
2. **User Interactions**: Test button clicks, form submissions, navigation
3. **Data Transformations**: Test data processing functions with known inputs
4. **Edge Cases**: Test boundary conditions (empty arrays, null values, etc.)
5. **Integration Points**: Test component interactions and state updates

Example unit tests:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

describe('KPICard Component', () => {
  it('should display total accounts KPI card', () => {
    render(
      <KPICard
        title="Total Accounts"
        value={1234}
        formatter={(v) => v.toLocaleString()}
      />
    );
    
    expect(screen.getByText('Total Accounts')).toBeInTheDocument();
    expect(screen.getByText('1,234')).toBeInTheDocument();
  });

  it('should display risk ratio with 2 decimal places', () => {
    render(
      <KPICard
        title="Risk Ratio"
        value={12.3456}
        formatter={(v) => `${v.toFixed(2)}%`}
      />
    );
    
    expect(screen.getByText('12.35%')).toBeInTheDocument();
  });
});

describe('AccountList Component', () => {
  it('should filter accounts by risk level', () => {
    const accounts = [
      { account_id: 'A1', risk_score: 90, risk_level: 'HIGH' },
      { account_id: 'A2', risk_score: 30, risk_level: 'LOW' },
      { account_id: 'A3', risk_score: 95, risk_level: 'CRITICAL' },
    ];
    
    const { rerender } = render(
      <AccountList
        accounts={accounts}
        filters={{ risk_level: null, search_query: '' }}
        onFilterChange={vi.fn()}
        onAccountSelect={vi.fn()}
        currentPage={1}
        pageSize={20}
        onPageChange={vi.fn()}
      />
    );
    
    expect(screen.getAllByRole('row')).toHaveLength(4); // 3 accounts + header
    
    rerender(
      <AccountList
        accounts={accounts}
        filters={{ risk_level: 'HIGH', search_query: '' }}
        onFilterChange={vi.fn()}
        onAccountSelect={vi.fn()}
        currentPage={1}
        pageSize={20}
        onPageChange={vi.fn()}
      />
    );
    
    expect(screen.getAllByRole('row')).toHaveLength(2); // 1 account + header
  });

  it('should search accounts by account_id', () => {
    const accounts = [
      { account_id: 'ACC001', risk_score: 90, risk_level: 'HIGH' },
      { account_id: 'ACC002', risk_score: 30, risk_level: 'LOW' },
      { account_id: 'USR001', risk_score: 95, risk_level: 'CRITICAL' },
    ];
    
    render(
      <AccountList
        accounts={accounts}
        filters={{ risk_level: null, search_query: 'ACC' }}
        onFilterChange={vi.fn()}
        onAccountSelect={vi.fn()}
        currentPage={1}
        pageSize={20}
        onPageChange={vi.fn()}
      />
    );
    
    expect(screen.getAllByRole('row')).toHaveLength(3); // 2 accounts + header
    expect(screen.getByText('ACC001')).toBeInTheDocument();
    expect(screen.getByText('ACC002')).toBeInTheDocument();
    expect(screen.queryByText('USR001')).not.toBeInTheDocument();
  });
});

describe('CSV Validation', () => {
  it('should reject CSV with missing required columns', () => {
    const csvContent = 'account_id,risk_score\nACC001,90';
    
    expect(() => validateCSV(csvContent)).toThrow('Missing required column: risk_level');
  });

  it('should reject CSV with invalid risk score', () => {
    const csvContent = 'account_id,risk_score,risk_level\nACC001,150,HIGH';
    
    const errors = validateCSVRows(parseCSV(csvContent));
    
    expect(errors).toHaveLength(1);
    expect(errors[0].line).toBe(2);
    expect(errors[0].column).toBe('risk_score');
    expect(errors[0].error).toContain('between 0 and 100');
  });

  it('should reject CSV with invalid risk level', () => {
    const csvContent = 'account_id,risk_score,risk_level\nACC001,90,SUPER_HIGH';
    
    const errors = validateCSVRows(parseCSV(csvContent));
    
    expect(errors).toHaveLength(1);
    expect(errors[0].line).toBe(2);
    expect(errors[0].column).toBe('risk_level');
    expect(errors[0].error).toContain('must be one of');
  });
});

describe('API Retry Logic', () => {
  it('should retry failed requests up to 3 times', async () => {
    let attempts = 0;
    const mockFetch = vi.fn(() => {
      attempts++;
      if (attempts < 3) {
        return Promise.reject(new Error('Network error'));
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    
    await retryWithBackoff(mockFetch, 3, 100);
    
    expect(attempts).toBe(3);
  });

  it('should throw error after max attempts', async () => {
    const mockFetch = vi.fn(() => Promise.reject(new Error('Network error')));
    
    await expect(retryWithBackoff(mockFetch, 3, 100)).rejects.toThrow(
      'Failed after 3 attempts'
    );
    
    expect(mockFetch).toHaveBeenCalledTimes(3);
  });
});
```

### Accessibility Testing

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('should have no accessibility violations in KPI section', async () => {
    const { container } = render(<KPISection accounts={mockAccounts} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have no accessibility violations in account list', async () => {
    const { container } = render(
      <AccountList
        accounts={mockAccounts}
        filters={{ risk_level: null, search_query: '' }}
        onFilterChange={vi.fn()}
        onAccountSelect={vi.fn()}
        currentPage={1}
        pageSize={20}
        onPageChange={vi.fn()}
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should support keyboard navigation in account list', () => {
    render(
      <AccountList
        accounts={mockAccounts}
        filters={{ risk_level: null, search_query: '' }}
        onFilterChange={vi.fn()}
        onAccountSelect={vi.fn()}
        currentPage={1}
        pageSize={20}
        onPageChange={vi.fn()}
      />
    );
    
    const firstRow = screen.getAllByRole('row')[1];
    firstRow.focus();
    
    fireEvent.keyDown(firstRow, { key: 'ArrowDown' });
    expect(screen.getAllByRole('row')[2]).toHaveFocus();
    
    fireEvent.keyDown(screen.getAllByRole('row')[2], { key: 'Enter' });
    // Verify account detail is displayed
  });
});
```

### Performance Testing

```typescript
describe('Performance', () => {
  it('should render large account list efficiently', () => {
    const largeAccountList = Array.from({ length: 10000 }, (_, i) => ({
      account_id: `ACC${i}`,
      risk_score: Math.random() * 100,
      risk_level: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][
        Math.floor(Math.random() * 4)
      ] as RiskLevel,
    }));
    
    const startTime = performance.now();
    render(
      <AccountList
        accounts={largeAccountList}
        filters={{ risk_level: null, search_query: '' }}
        onFilterChange={vi.fn()}
        onAccountSelect={vi.fn()}
        currentPage={1}
        pageSize={20}
        onPageChange={vi.fn()}
      />
    );
    const endTime = performance.now();
    
    // Should render in less than 2 seconds
    expect(endTime - startTime).toBeLessThan(2000);
    
    // Should only render visible rows (virtual scrolling)
    const renderedRows = screen.getAllByRole('row');
    expect(renderedRows.length).toBeLessThan(50); // Header + ~20 visible + overscan
  });

  it('should cache KPI calculations', () => {
    const accounts = mockAccounts;
    const calculateKPIs = vi.fn((accts) => ({
      total: accts.length,
      highRisk: accts.filter(a => a.risk_level === 'HIGH' || a.risk_level === 'CRITICAL').length,
      riskRatio: 0.25,
      avgRiskScore: 45.5,
    }));
    
    const { rerender } = render(<KPISection accounts={accounts} calculateKPIs={calculateKPIs} />);
    
    expect(calculateKPIs).toHaveBeenCalledTimes(1);
    
    // Rerender with same accounts - should use cached result
    rerender(<KPISection accounts={accounts} calculateKPIs={calculateKPIs} />);
    
    expect(calculateKPIs).toHaveBeenCalledTimes(1); // Still 1, not 2
  });
});
```

### Test Coverage Goals

- **Overall Coverage**: Minimum 80% line coverage
- **Critical Paths**: 100% coverage for data validation, error handling, and security-related code
- **Component Coverage**: Minimum 90% coverage for all React components
- **Property Tests**: All 38 correctness properties must have corresponding property-based tests
- **Unit Tests**: All example-based acceptance criteria must have corresponding unit tests

### Continuous Integration

Tests will run automatically on:
- Every commit to feature branches
- Pull requests to main branch
- Scheduled nightly runs with extended property test iterations (1000+ runs)

CI pipeline will:
1. Run all unit tests
2. Run all property-based tests
3. Generate coverage reports
4. Run accessibility tests
5. Run performance benchmarks
6. Fail the build if coverage drops below 80%

