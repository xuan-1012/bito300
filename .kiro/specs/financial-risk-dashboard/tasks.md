# Implementation Plan: Financial Risk Dashboard

## Overview

This implementation plan breaks down the Financial Risk Dashboard into discrete coding tasks. The dashboard is a React 18 + TypeScript web application using Vite, Apache ECharts 5.x, Tailwind CSS, and Zod for data validation. The implementation follows a bottom-up approach: core utilities → data layer → components → integration → testing.

## Tasks

- [x] 1. Project setup and configuration
  - Initialize Vite project with React 18 and TypeScript
  - Configure Tailwind CSS with custom color palette
  - Install dependencies: echarts, echarts-for-react, zod, fast-check, vitest, @testing-library/react
  - Set up Vitest configuration with coverage reporting
  - Create project directory structure (components, hooks, utils, types, context)
  - _Requirements: 14.1, 15.1_

- [x] 2. Core type definitions and schemas
  - [x] 2.1 Create TypeScript type definitions
    - Define RiskLevel, Account, RiskFactor types
    - Define all chart data types (ValidationCurveData, LearningCurveData, etc.)
    - Define DashboardState and DashboardAction types
    - Define component prop interfaces
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1_

  - [x] 2.2 Create Zod validation schemas
    - Implement RiskLevelSchema, RiskFactorSchema, AccountSchema
    - Implement chart data schemas (ValidationCurveSchema, ROCCurveSchema, etc.)
    - Implement DashboardDataSchema for complete data validation
    - _Requirements: 12.2, 12.4, 12.5, 13.3_

  - [ ]* 2.3 Write property test for risk score range validation
    - **Property 15: Risk Score Range Validation**
    - **Validates: Requirements 12.4**

  - [ ]* 2.4 Write property test for risk level enum validation
    - **Property 16: Risk Level Enum Validation**
    - **Validates: Requirements 12.5**

- [x] 3. Utility functions and helpers
  - [x] 3.1 Implement number formatting utilities
    - Create formatNumberWithSeparators function
    - Create formatPercentage function (2 decimal places)
    - Create formatRiskScore function (1 decimal place)
    - _Requirements: 1.5, 1.6, 1.7_

  - [ ]* 3.2 Write property test for number formatting
    - **Property 1: Number Formatting with Thousand Separators**
    - **Validates: Requirements 1.5**

  - [x] 3.3 Implement color utilities
    - Create getRiskLevelColor function mapping risk levels to colors
    - Define colorPalette constant with WCAG AA compliant colors
    - _Requirements: 10.3, 11.3, 15.1, 19.3_

  - [ ]* 3.4 Write property test for risk level color mapping
    - **Property 9: Risk Level Color Mapping**
    - **Validates: Requirements 10.3, 11.3**

  - [ ]* 3.5 Write property test for color palette consistency
    - **Property 23: Color Palette Consistency**
    - **Validates: Requirements 15.1, 15.6**

  - [x] 3.6 Implement error handling utilities
    - Create DashboardError class with error categories
    - Create ErrorHandler class with error categorization logic
    - Create formatValidationErrors function for CSV errors
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.7_

  - [ ]* 3.7 Write property test for error logging
    - **Property 38: Error Logging**
    - **Validates: Requirements 20.7**

- [x] 4. Data processing layer
  - [x] 4.1 Implement CSV processor
    - Create CSVProcessor class with parseFile method
    - Implement CSV parsing using Papa Parse or similar
    - Implement validateCSVRow function with line number tracking
    - Implement transformData function to convert CSV to DashboardData
    - _Requirements: 12.1, 12.2, 12.3, 12.6_

  - [ ]* 4.2 Write property test for CSV column validation
    - **Property 13: CSV Column Validation**
    - **Validates: Requirements 12.2**

  - [ ]* 4.3 Write property test for CSV parsing round-trip
    - **Property 14: CSV Parsing Round-Trip**
    - **Validates: Requirements 12.3**

  - [ ]* 4.4 Write unit tests for CSV validation errors
    - Test missing required columns
    - Test invalid risk score values
    - Test invalid risk level values
    - _Requirements: 12.2, 12.4, 12.5_

  - [x] 4.5 Implement API processor
    - Create APIProcessor class with fetchData method
    - Implement retryWithBackoff function with exponential backoff
    - Implement API response validation using Zod schemas
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ]* 4.6 Write property test for API response validation
    - **Property 18: API Response Validation**
    - **Validates: Requirements 13.3**

  - [ ]* 4.7 Write property test for JSON parsing round-trip
    - **Property 19: JSON Parsing Round-Trip**
    - **Validates: Requirements 13.4**

  - [ ]* 4.8 Write property test for API retry logic
    - **Property 20: API Retry Logic**
    - **Validates: Requirements 13.5**

  - [ ]* 4.9 Write unit tests for API retry logic
    - Test successful retry after failures
    - Test failure after max attempts
    - _Requirements: 13.5_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. State management implementation
  - [x] 6.1 Create dashboard reducer
    - Implement dashboardReducer with all action handlers
    - Handle LOAD_DATA_START, LOAD_DATA_SUCCESS, LOAD_DATA_ERROR
    - Handle SELECT_ACCOUNT, UPDATE_FILTERS, REFRESH_DATA, CLEAR_ERROR
    - _Requirements: 12.7, 13.6, 17.1, 17.2, 17.4_

  - [x] 6.2 Create dashboard context
    - Implement DashboardContext with React.createContext
    - Create DashboardProvider component with useReducer
    - Implement loadCSVData and loadAPIData functions
    - Implement exportChart function
    - _Requirements: 12.1, 13.1, 16.1, 16.2_

  - [x] 6.3 Create custom hooks
    - Implement useDashboard hook for accessing context
    - Implement useResponsiveLayout hook for breakpoint detection
    - Implement useVirtualScroll hook for account list optimization
    - Implement useChartResize hook for responsive charts
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 18.2_

  - [ ]* 6.4 Write property test for state preservation during refresh
    - **Property 26: State Preservation During Refresh**
    - **Validates: Requirements 17.7**

- [x] 7. Chart configuration functions
  - [x] 7.1 Implement validation curve configuration
    - Create getValidationCurveOptions function
    - Configure dual-line chart with training and validation scores
    - Add tooltip, legend, axis labels, and export toolbox
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 7.2 Implement learning curve configuration
    - Create getLearningCurveOptions function
    - Configure dual-line chart with optional variance shading
    - Add tooltip, legend, axis labels
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 7.3 Implement confusion matrix configuration
    - Create getConfusionMatrixOptions function
    - Configure heatmap with cell values and color intensity
    - Add axis labels for Actual and Predicted
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 7.4 Implement ROC curve configuration
    - Create getROCCurveOptions function
    - Configure line chart with FPR/TPR axes
    - Add AUC score to title, include diagonal reference line
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 7.5 Write property test for AUC score calculation
    - **Property 3: AUC Score Calculation**
    - **Validates: Requirements 5.3**

  - [x] 7.6 Implement PR curve configuration
    - Create getPRCurveOptions function
    - Configure line chart with Recall/Precision axes
    - Add Average Precision score to title, include baseline reference
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 7.7 Write property test for average precision calculation
    - **Property 4: Average Precision Calculation**
    - **Validates: Requirements 6.3**

  - [x] 7.8 Implement lift curve configuration
    - Create getLiftCurveOptions function
    - Configure line chart with model curve and baseline
    - Calculate lift values at key percentiles
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 7.9 Write property test for lift value calculation
    - **Property 5: Lift Value Calculation**
    - **Validates: Requirements 7.4**

  - [x] 7.10 Implement threshold analysis configuration
    - Create getThresholdAnalysisOptions function
    - Configure multi-line chart for Precision, Recall, F1 Score
    - Mark optimal threshold with vertical line
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [x] 7.11 Implement feature importance configuration
    - Create getFeatureImportanceOptions function
    - Configure horizontal bar chart sorted by importance
    - Limit to top 10 features
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 7.12 Write property test for feature importance sorting
    - **Property 6: Feature Importance Sorting**
    - **Validates: Requirements 9.2**

  - [ ]* 7.13 Write property test for feature importance top-N limiting
    - **Property 7: Feature Importance Top-N Limiting**
    - **Validates: Requirements 9.6**

  - [ ] 7.14 Implement chart data sampling utility
    - Create sampleChartData function for large datasets
    - Implement sampling algorithm preserving curve shape
    - _Requirements: 18.3_

  - [ ]* 7.15 Write property test for chart data sampling
    - **Property 28: Chart Data Sampling**
    - **Validates: Requirements 18.3**

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Core UI components
  - [ ] 9.1 Create KPICard component
    - Implement KPICard with title, value, formatter, icon, trend props
    - Add smooth animation for value changes
    - Apply Tailwind styling with shadows and borders
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

  - [ ]* 9.2 Write unit tests for KPICard component
    - Test total accounts display
    - Test risk ratio formatting
    - Test average risk score formatting
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 9.3 Create ChartContainer component
    - Implement ChartContainer with title, chartType, data, height props
    - Integrate echarts-for-react for chart rendering
    - Add export button with PNG/JPEG/SVG options
    - Implement useChartResize hook integration
    - Add error boundary for chart rendering failures
    - _Requirements: 2.1, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 20.4_

  - [ ]* 9.4 Write property test for chart responsiveness
    - **Property 2: Chart Responsiveness**
    - **Validates: Requirements 2.7, 3.7, 4.7, 5.7, 6.7, 7.7, 8.7, 9.7, 14.5**

  - [ ]* 9.5 Write property test for chart export DPI
    - **Property 24: Chart Export DPI**
    - **Validates: Requirements 16.3**

  - [ ]* 9.6 Write property test for export filename format
    - **Property 25: Export Filename Format**
    - **Validates: Requirements 16.5**

  - [ ] 9.7 Create ErrorBoundary component
    - Implement DashboardErrorBoundary class component
    - Create ErrorFallback component for error display
    - Add reset functionality
    - _Requirements: 20.1, 20.4_

  - [ ]* 9.8 Write property test for error message display
    - **Property 37: Error Message Display**
    - **Validates: Requirements 20.1, 20.2, 20.3, 20.4**

- [ ] 10. Account list components
  - [ ] 10.1 Create AccountTable component
    - Implement table with account_id, risk_score, risk_level, risk_reason columns
    - Apply color coding for risk levels
    - Add row click handler for account selection
    - Integrate useVirtualScroll for performance
    - _Requirements: 10.1, 10.2, 10.3, 10.7, 18.2_

  - [ ]* 10.2 Write property test for account list sorting
    - **Property 8: Account List Sorting**
    - **Validates: Requirements 10.1**

  - [ ]* 10.3 Write property test for virtual scrolling rendering
    - **Property 27: Virtual Scrolling Rendering**
    - **Validates: Requirements 18.2**

  - [ ] 10.4 Create FilterBar component
    - Implement risk level filter dropdown
    - Add filter change handler
    - Apply Tailwind styling
    - _Requirements: 10.5_

  - [ ]* 10.5 Write property test for risk level filtering
    - **Property 11: Risk Level Filtering**
    - **Validates: Requirements 10.5**

  - [ ]* 10.6 Write unit tests for account list filtering
    - Test filtering by risk level
    - Test multiple filter combinations
    - _Requirements: 10.5_

  - [ ] 10.7 Create SearchBar component
    - Implement search input with debouncing
    - Add search change handler
    - Apply Tailwind styling
    - _Requirements: 10.6_

  - [ ]* 10.8 Write property test for account ID search
    - **Property 12: Account ID Search**
    - **Validates: Requirements 10.6**

  - [ ]* 10.9 Write unit tests for account search
    - Test case-insensitive search
    - Test partial match search
    - _Requirements: 10.6_

  - [ ] 10.10 Create Pagination component
    - Implement pagination with 20 items per page
    - Add page change handler
    - Display current page and total pages
    - Apply Tailwind styling
    - _Requirements: 10.4_

  - [ ]* 10.11 Write property test for account list pagination
    - **Property 10: Account List Pagination**
    - **Validates: Requirements 10.4**

  - [ ] 10.12 Create AccountList component
    - Integrate FilterBar, SearchBar, AccountTable, Pagination
    - Implement filtering and search logic
    - Handle account selection
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [ ] 11. Account detail component
  - [ ] 11.1 Create AccountDetail component
    - Display account_id prominently
    - Show risk_score with visual indicator (progress bar or gauge)
    - Show risk_level with color coding
    - List risk factors with contribution percentages
    - Display natural language explanation
    - Show key feature values in a table
    - Add "Back to List" button
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

  - [ ]* 11.2 Write unit tests for AccountDetail component
    - Test account information display
    - Test back button navigation
    - _Requirements: 11.1, 11.2, 11.3, 11.7_

- [ ] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Dashboard sections and layout
  - [ ] 13.1 Create KPISection component
    - Render 4 KPICard components (Total Accounts, High Risk, Risk Ratio, Avg Score)
    - Calculate KPI values from account data
    - Implement responsive grid layout
    - Add data caching for performance
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 18.7_

  - [ ]* 13.2 Write property test for data caching
    - **Property 30: Data Caching**
    - **Validates: Requirements 18.7**

  - [ ]* 13.3 Write unit tests for KPI calculations
    - Test total accounts calculation
    - Test high risk count calculation
    - Test risk ratio calculation
    - Test average risk score calculation
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 13.4 Create ChartsSection component
    - Render 8 ChartContainer components for all chart types
    - Implement responsive grid layout (2 columns on desktop, 1 on mobile)
    - Implement lazy loading for chart components
    - _Requirements: 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 14.1, 14.2, 14.3, 18.6_

  - [ ]* 13.5 Write property test for lazy loading implementation
    - **Property 29: Lazy Loading Implementation**
    - **Validates: Requirements 18.6**

  - [ ] 13.6 Create AccountsSection component
    - Conditionally render AccountList or AccountDetail
    - Handle view switching between list and detail
    - _Requirements: 10.1, 10.7, 11.1_

  - [ ] 13.7 Create Header component
    - Display dashboard title
    - Add refresh button with loading indicator
    - Add data source selector (CSV upload / API)
    - Display last updated timestamp
    - _Requirements: 17.1, 17.3, 17.6_

  - [ ] 13.8 Create DashboardLayout component
    - Integrate Header, KPISection, ChartsSection, AccountsSection
    - Implement responsive layout with useResponsiveLayout hook
    - Apply consistent spacing and styling
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 15.1, 15.2, 15.3, 15.4, 15.5_

  - [ ]* 13.9 Write property test for layout responsiveness
    - **Property 22: Layout Responsiveness**
    - **Validates: Requirements 14.4**

- [ ] 14. Data loading components
  - [ ] 14.1 Create CSVUploader component
    - Implement file input with drag-and-drop support
    - Add file validation (format, size, required columns)
    - Display upload progress
    - Show validation errors with line numbers
    - Integrate CSVProcessor
    - _Requirements: 12.1, 12.2, 12.6_

  - [ ]* 14.2 Write property test for CSV validation error display
    - **Property 17: CSV Validation Error Display**
    - **Validates: Requirements 12.6**

  - [ ] 14.3 Create APIDataLoader component
    - Implement automatic data fetching on mount
    - Add manual refresh capability
    - Implement automatic refresh with configurable interval
    - Display loading state
    - Handle API errors with retry logic
    - Integrate APIProcessor
    - _Requirements: 13.1, 13.2, 13.5, 13.7, 17.5_

  - [ ]* 14.4 Write property test for automatic refresh interval
    - **Property 21: Automatic Refresh Interval**
    - **Validates: Requirements 13.7, 17.5**

  - [ ] 14.5 Create DataSourceSelector component
    - Toggle between CSV upload and API loading
    - Conditionally render CSVUploader or APIDataLoader
    - _Requirements: 12.1, 13.1_

- [ ] 15. Accessibility implementation
  - [ ] 15.1 Add keyboard navigation support
    - Implement useKeyboardNavigation hook
    - Add keyboard handlers to AccountTable (Arrow keys, Enter, Escape)
    - Ensure all interactive elements are keyboard accessible
    - _Requirements: 19.1_

  - [ ]* 15.2 Write property test for keyboard navigation
    - **Property 31: Keyboard Navigation**
    - **Validates: Requirements 19.1**

  - [ ]* 15.3 Write unit tests for keyboard navigation
    - Test arrow key navigation in account list
    - Test Enter key for account selection
    - _Requirements: 19.1_

  - [ ] 15.4 Add ARIA labels and live regions
    - Add aria-label to all interactive elements
    - Add aria-live regions for dynamic content updates
    - Implement useAriaAnnouncement hook
    - Add role attributes to semantic elements
    - _Requirements: 19.2, 19.4, 19.5_

  - [ ]* 15.5 Write property test for ARIA labels presence
    - **Property 32: ARIA Labels Presence**
    - **Validates: Requirements 19.2, 19.4**

  - [ ]* 15.6 Write property test for ARIA live regions
    - **Property 34: ARIA Live Regions**
    - **Validates: Requirements 19.5**

  - [ ] 15.7 Add form labels and focus indicators
    - Associate all form inputs with labels
    - Add visible focus indicators with Tailwind focus: utilities
    - _Requirements: 19.6, 19.7_

  - [ ]* 15.8 Write property test for form label association
    - **Property 35: Form Label Association**
    - **Validates: Requirements 19.6**

  - [ ]* 15.9 Write property test for focus indicators
    - **Property 36: Focus Indicators**
    - **Validates: Requirements 19.7**

  - [ ]* 15.10 Write property test for color contrast compliance
    - **Property 33: Color Contrast Compliance**
    - **Validates: Requirements 19.3**

  - [ ]* 15.11 Run accessibility tests with jest-axe
    - Test KPISection for violations
    - Test AccountList for violations
    - Test all major components
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7_

- [ ] 16. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Performance optimization
  - [ ] 17.1 Implement performance monitoring
    - Add performance.now() measurements for initial render
    - Add performance.now() measurements for filter/search operations
    - Add performance.now() measurements for view transitions
    - Log performance metrics to console
    - _Requirements: 18.1, 18.4, 18.5_

  - [ ]* 17.2 Write performance tests
    - Test large account list rendering time (<2s)
    - Test filter operation time (<500ms)
    - Test view transition time (<300ms)
    - _Requirements: 18.1, 18.4, 18.5_

  - [ ] 17.3 Optimize component re-renders
    - Add React.memo to pure components
    - Use useMemo for expensive calculations
    - Use useCallback for event handlers
    - _Requirements: 18.1, 18.7_

  - [ ]* 17.4 Write unit tests for caching behavior
    - Test KPI calculation caching
    - Test chart data transformation caching
    - _Requirements: 18.7_

- [ ] 18. Integration and wiring
  - [ ] 18.1 Create App component
    - Wrap application with DashboardProvider
    - Wrap application with ErrorBoundary
    - Render DashboardLayout
    - _Requirements: All_

  - [ ] 18.2 Create main entry point
    - Set up React root with createRoot
    - Import and render App component
    - Import Tailwind CSS
    - _Requirements: All_

  - [ ] 18.3 Configure Vite build
    - Set up production build optimization
    - Configure code splitting for chart components
    - Configure asset optimization
    - _Requirements: 18.1, 18.6_

  - [ ]* 18.4 Write integration tests
    - Test complete data loading flow (CSV upload → validation → display)
    - Test complete data loading flow (API fetch → validation → display)
    - Test account selection flow (list → detail → back)
    - Test filter and search flow
    - Test chart export flow
    - _Requirements: 12.7, 13.6, 10.7, 11.7, 16.6_

- [ ] 19. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify test coverage meets 80% minimum
  - Run accessibility tests
  - Run performance benchmarks
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using fast-check
- Unit tests validate specific examples and edge cases
- All tests should run with `npm test` or `npm run test:coverage`
- The implementation uses TypeScript for type safety throughout
- Accessibility compliance (WCAG AA) is built in from the start
- Performance optimizations are integrated during development, not as an afterthought
