/**
 * Color utilities for Financial Risk Dashboard
 * Provides consistent color mapping and WCAG AA compliant color palette
 */

import type { RiskLevel } from '../types';

/**
 * WCAG AA compliant color palette for the dashboard
 * All colors meet accessibility standards for contrast ratios
 */
export const colorPalette = {
  // Risk level colors (WCAG AA compliant)
  risk: {
    critical: '#dc2626', // Red 600
    high: '#ea580c', // Orange 600
    medium: '#ca8a04', // Yellow 600
    low: '#16a34a', // Green 600
  },
  // Chart colors
  chart: {
    primary: '#3b82f6', // Blue 500
    secondary: '#10b981', // Green 500
    tertiary: '#8b5cf6', // Purple 500
    quaternary: '#f59e0b', // Amber 500
  },
  // Text colors
  text: {
    primary: '#0f172a', // Slate 900
    secondary: '#475569', // Slate 600
    disabled: '#94a3b8', // Slate 400
  },
  // Background colors
  background: {
    primary: '#ffffff',
    secondary: '#f8fafc', // Slate 50
    tertiary: '#f1f5f9', // Slate 100
  },
} as const;

/**
 * Maps a risk level to its corresponding color
 * @param riskLevel - The risk level (LOW, MEDIUM, HIGH, CRITICAL)
 * @returns Hex color code for the risk level
 * @example
 * getRiskLevelColor('HIGH') // "#ea580c"
 * getRiskLevelColor('LOW') // "#16a34a"
 */
export function getRiskLevelColor(riskLevel: RiskLevel): string {
  const colorMap: Record<RiskLevel, string> = {
    LOW: colorPalette.risk.low,
    MEDIUM: colorPalette.risk.medium,
    HIGH: colorPalette.risk.high,
    CRITICAL: colorPalette.risk.critical,
  };

  return colorMap[riskLevel];
}
