import { describe, it, expect } from 'vitest';
import {
  formatNumberWithSeparators,
  formatPercentage,
  formatRiskScore,
} from '../formatters';

describe('formatNumberWithSeparators', () => {
  it('should format numbers with thousand separators', () => {
    expect(formatNumberWithSeparators(1234567)).toBe('1,234,567');
    expect(formatNumberWithSeparators(1000)).toBe('1,000');
    expect(formatNumberWithSeparators(1000000)).toBe('1,000,000');
  });

  it('should handle numbers without thousands', () => {
    expect(formatNumberWithSeparators(100)).toBe('100');
    expect(formatNumberWithSeparators(999)).toBe('999');
    expect(formatNumberWithSeparators(0)).toBe('0');
  });

  it('should handle decimal numbers', () => {
    expect(formatNumberWithSeparators(1234.56)).toBe('1,234.56');
    expect(formatNumberWithSeparators(1000000.123)).toBe('1,000,000.123');
  });

  it('should handle negative numbers', () => {
    expect(formatNumberWithSeparators(-1234567)).toBe('-1,234,567');
    expect(formatNumberWithSeparators(-1000)).toBe('-1,000');
  });
});

describe('formatPercentage', () => {
  it('should format percentages with default 2 decimal places', () => {
    expect(formatPercentage(45.678)).toBe('45.68%');
    expect(formatPercentage(100)).toBe('100.00%');
    expect(formatPercentage(0)).toBe('0.00%');
  });

  it('should format percentages with custom decimal places', () => {
    expect(formatPercentage(45.678, 0)).toBe('46%');
    expect(formatPercentage(45.678, 1)).toBe('45.7%');
    expect(formatPercentage(45.678, 3)).toBe('45.678%');
  });

  it('should handle decimal input (0-1 range)', () => {
    expect(formatPercentage(0.456, 2, true)).toBe('45.60%');
    expect(formatPercentage(1, 2, true)).toBe('100.00%');
    expect(formatPercentage(0, 2, true)).toBe('0.00%');
  });

  it('should handle edge cases', () => {
    expect(formatPercentage(99.999, 2)).toBe('100.00%');
    expect(formatPercentage(0.001, 2)).toBe('0.00%');
  });
});

describe('formatRiskScore', () => {
  it('should format risk scores with 1 decimal place', () => {
    expect(formatRiskScore(85.678)).toBe('85.7');
    expect(formatRiskScore(100)).toBe('100.0');
    expect(formatRiskScore(0)).toBe('0.0');
  });

  it('should round correctly', () => {
    expect(formatRiskScore(85.64)).toBe('85.6');
    expect(formatRiskScore(85.65)).toBe('85.7');
    expect(formatRiskScore(85.66)).toBe('85.7');
  });

  it('should handle edge cases', () => {
    expect(formatRiskScore(99.99)).toBe('100.0');
    expect(formatRiskScore(0.01)).toBe('0.0');
    expect(formatRiskScore(50.5)).toBe('50.5');
  });
});
