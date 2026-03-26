// CSV data processor for Financial Risk Dashboard
import Papa from 'papaparse';
import { DashboardDataSchema } from '../types/schemas';
import type { DashboardData } from '../types';
import { DashboardError } from '../utils/errors';

export interface CSVValidationError {
  row: number;
  field: string;
  message: string;
}

export class CSVProcessor {
  /**
   * Parse a CSV file and transform it into DashboardData
   * @param file - The CSV file to parse
   * @returns Promise resolving to validated DashboardData
   * @throws DashboardError if parsing or validation fails
   */
  async parseFile(file: File): Promise<DashboardData> {
    try {
      // Read file as text (compatible with both browser and test environments)
      const text = await this.readFileAsText(file);
      
      // Parse CSV
      const rows = this.parseCSV(text);
      
      // Validate rows
      const validated = this.validateData(rows);
      
      // Transform to DashboardData
      return this.transformData(validated);
    } catch (error) {
      if (error instanceof DashboardError) {
        throw error;
      }
      throw new DashboardError(
        `Failed to parse CSV file: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'DATA_LOADING_ERROR',
        error instanceof Error ? { originalError: error.message } : undefined
      );
    }
  }

  /**
   * Read file content as text (compatible with test environments)
   * @param file - File to read
   * @returns Promise resolving to file text content
   */
  private readFileAsText(file: File | Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file);
    });
  }

  /**
   * Parse CSV text into array of row objects
   * @param text - CSV text content
   * @returns Array of parsed row objects
   */
  private parseCSV(text: string): any[] {
    const result = Papa.parse(text, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      transformHeader: (header: string) => header.trim(),
    });

    if (result.errors.length > 0) {
      const errorMessages = result.errors
        .map(err => `Row ${err.row}: ${err.message}`)
        .join('; ');
      throw new DashboardError(
        `CSV parsing errors: ${errorMessages}`,
        'CSV_PARSING_ERROR'
      );
    }

    if (!result.data || result.data.length === 0) {
      throw new DashboardError(
        'CSV file is empty or contains no valid data',
        'CSV_EMPTY_ERROR'
      );
    }

    return result.data;
  }

  /**
   * Validate CSV rows and check for required columns
   * @param rows - Array of parsed CSV rows
   * @returns Validated rows
   * @throws DashboardError if validation fails
   */
  private validateData(rows: any[]): any[] {
    const errors: CSVValidationError[] = [];
    
    // Check first row for required columns
    if (rows.length > 0) {
      const firstRow = rows[0];
      const requiredColumns = ['account_id', 'risk_score', 'risk_level'];
      const missingColumns = requiredColumns.filter(col => !(col in firstRow));
      
      if (missingColumns.length > 0) {
        throw new DashboardError(
          `Missing required columns: ${missingColumns.join(', ')}`,
          'CSV_MISSING_COLUMNS'
        );
      }
    }

    // Validate each row
    rows.forEach((row, index) => {
      const rowNumber = index + 2; // +2 because index is 0-based and header is row 1
      
      // Validate account_id
      if (!row.account_id || typeof row.account_id !== 'string') {
        errors.push({
          row: rowNumber,
          field: 'account_id',
          message: 'account_id must be a non-empty string',
        });
      }

      // Validate risk_score
      if (typeof row.risk_score !== 'number' || row.risk_score < 0 || row.risk_score > 100) {
        errors.push({
          row: rowNumber,
          field: 'risk_score',
          message: 'risk_score must be a number between 0 and 100',
        });
      }

      // Validate risk_level
      const validRiskLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
      if (!validRiskLevels.includes(row.risk_level)) {
        errors.push({
          row: rowNumber,
          field: 'risk_level',
          message: `risk_level must be one of: ${validRiskLevels.join(', ')}`,
        });
      }
    });

    if (errors.length > 0) {
      const errorMessage = errors
        .slice(0, 10) // Show first 10 errors
        .map(err => `Row ${err.row}, ${err.field}: ${err.message}`)
        .join('\n');
      
      const additionalErrors = errors.length > 10 ? `\n... and ${errors.length - 10} more errors` : '';
      
      throw new DashboardError(
        `CSV validation failed:\n${errorMessage}${additionalErrors}`,
        'CSV_VALIDATION_ERROR',
        { errorCount: errors.length }
      );
    }

    return rows;
  }

  /**
   * Transform validated CSV rows into DashboardData structure
   * @param rows - Validated CSV rows
   * @returns DashboardData object
   */
  private transformData(rows: any[]): DashboardData {
    // Transform rows into accounts
    const accounts = rows.map(row => ({
      account_id: row.account_id,
      risk_score: row.risk_score,
      risk_level: row.risk_level,
      risk_factors: this.parseRiskFactors(row.risk_factors),
      feature_values: this.parseFeatureValues(row.feature_values),
      explanation: row.explanation || '',
    }));

    // Extract chart data if present
    const charts = {
      validation_curve: null,
      learning_curve: null,
      confusion_matrix: null,
      roc_curve: null,
      pr_curve: null,
      lift_curve: null,
      threshold_analysis: null,
      feature_importance: null,
    };

    const dashboardData = {
      accounts,
      charts,
    };

    // Validate against schema
    try {
      return DashboardDataSchema.parse(dashboardData);
    } catch (error) {
      throw new DashboardError(
        `Data validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'DATA_VALIDATION_ERROR',
        error instanceof Error ? { originalError: error.message } : undefined
      );
    }
  }

  /**
   * Parse risk factors from CSV field (JSON string or empty)
   * @param value - Risk factors value from CSV
   * @returns Array of risk factors
   */
  private parseRiskFactors(value: any): any[] {
    if (!value) return [];
    
    try {
      if (typeof value === 'string') {
        return JSON.parse(value);
      }
      if (Array.isArray(value)) {
        return value;
      }
      return [];
    } catch {
      return [];
    }
  }

  /**
   * Parse feature values from CSV field (JSON string or empty)
   * @param value - Feature values from CSV
   * @returns Record of feature values
   */
  private parseFeatureValues(value: any): Record<string, number> {
    if (!value) return {};
    
    try {
      if (typeof value === 'string') {
        return JSON.parse(value);
      }
      if (typeof value === 'object' && !Array.isArray(value)) {
        return value;
      }
      return {};
    } catch {
      return {};
    }
  }
}
