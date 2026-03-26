import { describe, it, expect } from 'vitest';
import { getRiskLevelColor, colorPalette } from '../colors';
import type { RiskLevel } from '../../types';

describe('colorPalette', () => {
  it('should have all required risk colors', () => {
    expect(colorPalette.risk.critical).toBe('#dc2626');
    expect(colorPalette.risk.high).toBe('#ea580c');
    expect(colorPalette.risk.medium).toBe('#ca8a04');
    expect(colorPalette.risk.low).toBe('#16a34a');
  });

  it('should have all required chart colors', () => {
    expect(colorPalette.chart.primary).toBe('#3b82f6');
    expect(colorPalette.chart.secondary).toBe('#10b981');
    expect(colorPalette.chart.tertiary).toBe('#8b5cf6');
    expect(colorPalette.chart.quaternary).toBe('#f59e0b');
  });

  it('should have all required text colors', () => {
    expect(colorPalette.text.primary).toBe('#0f172a');
    expect(colorPalette.text.secondary).toBe('#475569');
    expect(colorPalette.text.disabled).toBe('#94a3b8');
  });

  it('should have all required background colors', () => {
    expect(colorPalette.background.primary).toBe('#ffffff');
    expect(colorPalette.background.secondary).toBe('#f8fafc');
    expect(colorPalette.background.tertiary).toBe('#f1f5f9');
  });
});

describe('getRiskLevelColor', () => {
  it('should return correct color for LOW risk level', () => {
    expect(getRiskLevelColor('LOW')).toBe('#16a34a');
  });

  it('should return correct color for MEDIUM risk level', () => {
    expect(getRiskLevelColor('MEDIUM')).toBe('#ca8a04');
  });

  it('should return correct color for HIGH risk level', () => {
    expect(getRiskLevelColor('HIGH')).toBe('#ea580c');
  });

  it('should return correct color for CRITICAL risk level', () => {
    expect(getRiskLevelColor('CRITICAL')).toBe('#dc2626');
  });

  it('should handle all risk levels consistently', () => {
    const riskLevels: RiskLevel[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
    
    riskLevels.forEach((level) => {
      const color = getRiskLevelColor(level);
      expect(color).toMatch(/^#[0-9a-f]{6}$/i);
    });
  });
});
