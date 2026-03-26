/**
 * Number formatting utilities for Financial Risk Dashboard
 * Provides consistent number formatting across the application
 */

/**
 * Formats a number with thousand separators (commas)
 * @param value - The number to format
 * @returns Formatted string with thousand separators
 * @example
 * formatNumberWithSeparators(1234567) // "1,234,567"
 * formatNumberWithSeparators(100) // "100"
 */
export function formatNumberWithSeparators(value: number): string {
  return value.toLocaleString('en-US');
}

/**
 * Formats a number as a percentage with specified decimal places
 * @param value - The number to format (0-100 or 0-1 depending on isDecimal)
 * @param decimalPlaces - Number of decimal places to show (default: 2)
 * @param isDecimal - Whether the input is in decimal form (0-1) or percentage form (0-100)
 * @returns Formatted percentage string
 * @example
 * formatPercentage(45.678, 2) // "45.68%"
 * formatPercentage(0.456, 2, true) // "45.60%"
 * formatPercentage(100, 0) // "100%"
 */
export function formatPercentage(
  value: number,
  decimalPlaces: number = 2,
  isDecimal: boolean = false
): string {
  const percentValue = isDecimal ? value * 100 : value;
  return `${percentValue.toFixed(decimalPlaces)}%`;
}

/**
 * Formats a risk score with 1 decimal place
 * @param score - The risk score to format (0-100)
 * @returns Formatted risk score string
 * @example
 * formatRiskScore(85.678) // "85.7"
 * formatRiskScore(100) // "100.0"
 */
export function formatRiskScore(score: number): string {
  return score.toFixed(1);
}
