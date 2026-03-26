// API data processor for Financial Risk Dashboard
import { DashboardDataSchema } from '../types/schemas';
import type { DashboardData, APILoaderConfig } from '../types';
import { DashboardError } from '../utils/errors';

export class APIProcessor {
  constructor(private config: APILoaderConfig) {}

  /**
   * Fetch data from the configured API endpoint
   * @returns Promise resolving to validated DashboardData
   * @throws DashboardError if fetching or validation fails
   */
  async fetchData(): Promise<DashboardData> {
    try {
      const response = await this.makeRequest();
      const validated = this.validateResponse(response);
      return validated;
    } catch (error) {
      if (error instanceof DashboardError) {
        throw error;
      }
      throw new DashboardError(
        `Failed to fetch API data: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'API_FETCH_ERROR',
        error instanceof Error ? { originalError: error.message } : undefined
      );
    }
  }

  /**
   * Make HTTP request with retry logic
   * @param attempt - Current attempt number (1-indexed)
   * @returns Promise resolving to response data
   */
  private async makeRequest(attempt = 1): Promise<any> {
    try {
      const response = await fetch(this.config.endpoint, {
        method: this.config.method,
        headers: this.config.headers || {},
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      // Retry with exponential backoff if attempts remain
      if (attempt < this.config.retryAttempts) {
        const delay = this.calculateBackoffDelay(attempt);
        await this.delay(delay);
        return this.makeRequest(attempt + 1);
      }

      // All retries exhausted
      throw new DashboardError(
        `API request failed after ${this.config.retryAttempts} attempts: ${
          error instanceof Error ? error.message : 'Unknown error'
        }`,
        'API_REQUEST_FAILED',
        { 
          attempts: this.config.retryAttempts,
          originalError: error instanceof Error ? error.message : 'Unknown error'
        }
      );
    }
  }

  /**
   * Calculate exponential backoff delay
   * @param attempt - Current attempt number (1-indexed)
   * @returns Delay in milliseconds
   */
  private calculateBackoffDelay(attempt: number): number {
    // Exponential backoff: baseDelay * 2^(attempt-1)
    return this.config.retryDelay * Math.pow(2, attempt - 1);
  }

  /**
   * Delay execution for specified milliseconds
   * @param ms - Milliseconds to delay
   * @returns Promise that resolves after delay
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Validate API response against schema
   * @param data - Response data from API
   * @returns Validated DashboardData
   * @throws DashboardError if validation fails
   */
  private validateResponse(data: any): DashboardData {
    try {
      return DashboardDataSchema.parse(data);
    } catch (error) {
      throw new DashboardError(
        `API response validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'API_VALIDATION_ERROR',
        error instanceof Error ? { originalError: error.message } : undefined
      );
    }
  }

  /**
   * Retry a failed request with exponential backoff
   * This is a public method for manual retry scenarios
   * @param operation - Async operation to retry
   * @returns Promise resolving to operation result
   */
  async retryWithBackoff<T>(operation: () => Promise<T>): Promise<T> {
    let lastError: Error | undefined;

    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        
        if (attempt < this.config.retryAttempts) {
          const delay = this.calculateBackoffDelay(attempt);
          await this.delay(delay);
        }
      }
    }

    throw new DashboardError(
      `Operation failed after ${this.config.retryAttempts} attempts: ${lastError?.message || 'Unknown error'}`,
      'RETRY_EXHAUSTED',
      { 
        attempts: this.config.retryAttempts,
        originalError: lastError?.message || 'Unknown error'
      }
    );
  }
}
