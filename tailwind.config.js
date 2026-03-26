<<<<<<< HEAD
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Risk level colors (WCAG AA compliant)
        risk: {
          critical: '#dc2626', // Red 600
          high: '#ea580c',     // Orange 600
          medium: '#ca8a04',   // Yellow 600
          low: '#16a34a',      // Green 600
        },
        // Chart colors
        chart: {
          primary: '#3b82f6',    // Blue 500
          secondary: '#10b981',  // Green 500
          tertiary: '#8b5cf6',   // Purple 500
          quaternary: '#f59e0b', // Amber 500
        },
        // Text colors
        text: {
          primary: '#0f172a',   // Slate 900
          secondary: '#475569', // Slate 600
          disabled: '#94a3b8',  // Slate 400
        },
        // Background colors
        background: {
          primary: '#ffffff',
          secondary: '#f8fafc', // Slate 50
          tertiary: '#f1f5f9',  // Slate 100
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
=======
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Risk level colors (WCAG AA compliant)
        risk: {
          critical: '#dc2626', // Red 600
          high: '#ea580c',     // Orange 600
          medium: '#ca8a04',   // Yellow 600
          low: '#16a34a',      // Green 600
        },
        // Chart colors
        chart: {
          primary: '#3b82f6',    // Blue 500
          secondary: '#10b981',  // Green 500
          tertiary: '#8b5cf6',   // Purple 500
          quaternary: '#f59e0b', // Amber 500
        },
        // Text colors
        text: {
          primary: '#0f172a',   // Slate 900
          secondary: '#475569', // Slate 600
          disabled: '#94a3b8',  // Slate 400
        },
        // Background colors
        background: {
          primary: '#ffffff',
          secondary: '#f8fafc', // Slate 50
          tertiary: '#f1f5f9',  // Slate 100
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
>>>>>>> 3ed03a3 (Initial commit)
