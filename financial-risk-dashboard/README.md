# Financial Risk Dashboard

A professional-grade web application for visualizing machine learning model risk assessment results and account analysis information.

## Features

- **KPI Cards**: Display key performance indicators at a glance
- **8 Chart Types**: Validation Curve, Learning Curve, Confusion Matrix, ROC Curve, PR Curve, Lift Curve, Threshold Analysis, Feature Importance
- **Account Management**: Suspicious account list with filtering and search
- **Detailed Analysis**: Single account risk factor breakdown
- **Responsive Design**: Adapts to desktop, tablet, and mobile screens
- **Accessibility**: WCAG AA compliant
- **Performance**: Optimized for large datasets (up to 10,000 accounts)

## Technology Stack

- **React 18** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Apache ECharts 5.x** for professional visualizations
- **Tailwind CSS** for responsive styling
- **Zod** for runtime data validation
- **Vitest** for unit and property-based testing
- **fast-check** for property-based testing

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build

```bash
npm run build
```

### Testing

```bash
# Run all tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Linting

```bash
npm run lint
```

## Project Structure

```
src/
├── components/     # React components
├── context/        # React context providers
├── hooks/          # Custom React hooks
├── types/          # TypeScript type definitions
├── utils/          # Utility functions
├── test/           # Test utilities and setup
├── App.tsx         # Main application component
├── main.tsx        # Application entry point
└── index.css       # Global styles with Tailwind
```

## Testing Strategy

The project uses a dual testing approach:

- **Unit Tests**: Verify specific examples and edge cases
- **Property-Based Tests**: Verify universal properties across randomized inputs

All tests are written using Vitest and fast-check, with a minimum coverage target of 80%.

## License

Private project - All rights reserved
