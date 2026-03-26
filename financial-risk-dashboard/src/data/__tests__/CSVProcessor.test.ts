import { describe, it, expect } from 'vitest';
import { CSVProcessor } from '../CSVProcessor';
import { DashboardError } from '../../utils/errors';

// Helper to create a proper File-like object with text() method
function createTestFile(content: string, filename: string): File {
  const blob = new Blob([content], { type: 'text/csv' });
  return new File([blob], filename, { type: 'text/csv' });
}

describe('CSVProcessor', () => {
  const processor = new CSVProcessor();

  describe('parseFile', () => {
    it('should parse valid CSV file with minimal data', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,75.5,HIGH
ACC002,25.0,LOW`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts).toHaveLength(2);
      expect(result.accounts[0]).toMatchObject({
        account_id: 'ACC001',
        risk_score: 75.5,
        risk_level: 'HIGH',
      });
      expect(result.accounts[1]).toMatchObject({
        account_id: 'ACC002',
        risk_score: 25.0,
        risk_level: 'LOW',
      });
    });

    it('should parse CSV with all risk levels', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,10,LOW
ACC002,40,MEDIUM
ACC003,70,HIGH
ACC004,95,CRITICAL`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts).toHaveLength(4);
      expect(result.accounts[0].risk_level).toBe('LOW');
      expect(result.accounts[1].risk_level).toBe('MEDIUM');
      expect(result.accounts[2].risk_level).toBe('HIGH');
      expect(result.accounts[3].risk_level).toBe('CRITICAL');
    });

    it('should throw error for empty CSV file', async () => {
      const csvContent = '';
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      // Papa Parse may throw different errors for empty files
      await expect(processor.parseFile(file)).rejects.toThrow(/empty|parsing errors/i);
    });

    it('should throw error for missing required columns', async () => {
      const csvContent = `account_id,risk_score
ACC001,75.5`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      await expect(processor.parseFile(file)).rejects.toThrow('Missing required columns');
      await expect(processor.parseFile(file)).rejects.toThrow('risk_level');
    });

    it('should throw error for invalid risk_score (out of range)', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,150,HIGH`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      await expect(processor.parseFile(file)).rejects.toThrow('risk_score must be a number between 0 and 100');
    });

    it('should throw error for negative risk_score', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,-10,LOW`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      await expect(processor.parseFile(file)).rejects.toThrow('risk_score must be a number between 0 and 100');
    });

    it('should throw error for invalid risk_level', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,50,INVALID`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      await expect(processor.parseFile(file)).rejects.toThrow('risk_level must be one of');
    });

    it('should throw error for missing account_id', async () => {
      const csvContent = `account_id,risk_score,risk_level
,50,MEDIUM`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      await expect(processor.parseFile(file)).rejects.toThrow('account_id must be a non-empty string');
    });

    it('should handle CSV with optional fields', async () => {
      const csvContent = `account_id,risk_score,risk_level,explanation
ACC001,75.5,HIGH,High transaction frequency`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts[0].explanation).toBe('High transaction frequency');
    });

    it('should handle CSV with JSON risk_factors', async () => {
      const riskFactors = [
        { factor_name: 'High Frequency', contribution_percentage: 60, description: 'Many transactions' }
      ];
      // Use proper CSV escaping - double quotes inside quoted field
      const csvContent = `account_id,risk_score,risk_level,risk_factors
ACC001,75.5,HIGH,"${JSON.stringify(riskFactors).replace(/"/g, '""')}"`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts[0].risk_factors).toHaveLength(1);
      expect(result.accounts[0].risk_factors[0].factor_name).toBe('High Frequency');
    });

    it('should handle CSV with JSON feature_values', async () => {
      const featureValues = { transaction_count: 100, avg_amount: 5000 };
      // Use proper CSV escaping - double quotes inside quoted field
      const csvContent = `account_id,risk_score,risk_level,feature_values
ACC001,75.5,HIGH,"${JSON.stringify(featureValues).replace(/"/g, '""')}"`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts[0].feature_values).toEqual({
        transaction_count: 100,
        avg_amount: 5000,
      });
    });

    it('should handle multiple validation errors and show first 10', async () => {
      const rows = Array.from({ length: 15 }, (_, i) => `ACC${i},150,INVALID`).join('\n');
      const csvContent = `account_id,risk_score,risk_level\n${rows}`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow(DashboardError);
      await expect(processor.parseFile(file)).rejects.toThrow('and 20 more errors');
    });

    it('should trim whitespace from headers', async () => {
      const csvContent = `  account_id  ,  risk_score  ,  risk_level  
ACC001,75.5,HIGH`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts).toHaveLength(1);
      expect(result.accounts[0].account_id).toBe('ACC001');
    });

    it('should skip empty lines in CSV', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,75.5,HIGH

ACC002,25.0,LOW`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts).toHaveLength(2);
    });

    it('should return empty arrays for missing optional fields', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,75.5,HIGH`;
      
      const file = createTestFile(csvContent, 'test.csv');
      const result = await processor.parseFile(file);

      expect(result.accounts[0].risk_factors).toEqual([]);
      expect(result.accounts[0].feature_values).toEqual({});
      expect(result.accounts[0].explanation).toBe('');
    });

    it('should include row numbers in validation errors', async () => {
      const csvContent = `account_id,risk_score,risk_level
ACC001,75.5,HIGH
ACC002,150,INVALID`;
      
      const file = createTestFile(csvContent, 'test.csv');

      await expect(processor.parseFile(file)).rejects.toThrow('Row 3');
    });
  });
});
