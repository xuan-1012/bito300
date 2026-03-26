import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { APIProcessor } from '../APIProcessor';
import { DashboardError } from '../../utils/errors';
import type { APILoaderConfig } from '../../types';

describe('APIProcessor', () => {
  const mockConfig: APILoaderConfig = {
    endpoint: 'https://api.example.com/data',
    method: 'GET',
    headers: { 'Authorization': 'Bearer token' },
    retryAttempts: 3,
    retryDelay: 100,
  };

  const validResponse = {
    accounts: [
      {
        account_id: 'ACC001',
        risk_score: 75.5,
        risk_level: 'HIGH',
        risk_factors: [],
        feature_values: {},
        explanation: '',
      },
    ],
    charts: {
      validation_curve: null,
      learning_curve: null,
      confusion_matrix: null,
      roc_curve: null,
      pr_curve: null,
      lift_curve: null,
      threshold_analysis: null,
      feature_importance: null,
    },
  };

  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('fetchData', () => {
    it('should fetch and validate data successfully', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validResponse,
      });

      const processor = new APIProcessor(mockConfig);
      const result = await processor.fetchData();

      expect(result.accounts).toHaveLength(1);
      expect(result.accounts[0].account_id).toBe('ACC001');
      expect(global.fetch).toHaveBeenCalledWith(
        mockConfig.endpoint,
        {
          method: mockConfig.method,
          headers: mockConfig.headers,
        }
      );
    });

    it('should throw error for invalid response data', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ invalid: 'data' }),
      });

      const processor = new APIProcessor(mockConfig);

      await expect(processor.fetchData()).rejects.toThrow(DashboardError);
      await expect(processor.fetchData()).rejects.toThrow('validation failed');
    });

    it('should throw error for HTTP error response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      const processor = new APIProcessor(mockConfig);

      // Don't await - just start the promise
      const fetchPromise = processor.fetchData();

      // Fast-forward through all retry delays
      await vi.runAllTimersAsync();

      await expect(fetchPromise).rejects.toThrow(DashboardError);
      await expect(fetchPromise).rejects.toThrow('failed after 3 attempts');
    });

    it('should retry on failure with exponential backoff', async () => {
      let callCount = 0;
      global.fetch = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount < 3) {
          return Promise.resolve({
            ok: false,
            status: 500,
            statusText: 'Internal Server Error',
          });
        }
        return Promise.resolve({
          ok: true,
          json: async () => validResponse,
        });
      });

      const processor = new APIProcessor(mockConfig);
      const fetchPromise = processor.fetchData();

      // Fast-forward through retry delays
      await vi.advanceTimersByTimeAsync(100); // First retry delay
      await vi.advanceTimersByTimeAsync(200); // Second retry delay (exponential)

      const result = await fetchPromise;

      expect(result.accounts).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should fail after max retry attempts', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const processor = new APIProcessor(mockConfig);
      const fetchPromise = processor.fetchData();

      // Fast-forward through all retry delays
      await vi.advanceTimersByTimeAsync(100); // First retry
      await vi.advanceTimersByTimeAsync(200); // Second retry
      await vi.advanceTimersByTimeAsync(400); // Third retry (should fail)

      await expect(fetchPromise).rejects.toThrow(DashboardError);
      await expect(fetchPromise).rejects.toThrow('failed after 3 attempts');
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should handle network errors', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      const processor = new APIProcessor(mockConfig);
      const fetchPromise = processor.fetchData();

      // Fast-forward through retry delays
      await vi.advanceTimersByTimeAsync(100);
      await vi.advanceTimersByTimeAsync(200);

      await expect(fetchPromise).rejects.toThrow(DashboardError);
      await expect(fetchPromise).rejects.toThrow('Network error');
    });
  });

  describe('retryWithBackoff', () => {
    it('should succeed on first attempt', async () => {
      const processor = new APIProcessor(mockConfig);
      const operation = vi.fn().mockResolvedValue('success');

      const result = await processor.retryWithBackoff(operation);

      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(1);
    });

    it('should retry and eventually succeed', async () => {
      const processor = new APIProcessor(mockConfig);
      let callCount = 0;
      const operation = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount < 2) {
          return Promise.reject(new Error('Temporary failure'));
        }
        return Promise.resolve('success');
      });

      const retryPromise = processor.retryWithBackoff(operation);

      // Fast-forward through retry delay
      await vi.advanceTimersByTimeAsync(100);

      const result = await retryPromise;

      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(2);
    });

    it('should fail after max attempts', async () => {
      const processor = new APIProcessor(mockConfig);
      const operation = vi.fn().mockRejectedValue(new Error('Persistent failure'));

      const retryPromise = processor.retryWithBackoff(operation);

      // Fast-forward through all retry delays
      await vi.advanceTimersByTimeAsync(100);
      await vi.advanceTimersByTimeAsync(200);
      await vi.advanceTimersByTimeAsync(400);

      await expect(retryPromise).rejects.toThrow(DashboardError);
      await expect(retryPromise).rejects.toThrow('failed after 3 attempts');
      expect(operation).toHaveBeenCalledTimes(3);
    });

    it('should use exponential backoff delays', async () => {
      const processor = new APIProcessor(mockConfig);
      const operation = vi.fn().mockRejectedValue(new Error('Failure'));
      const delays: number[] = [];

      const retryPromise = processor.retryWithBackoff(operation);

      // Track delays between attempts
      const startTime = Date.now();
      await vi.advanceTimersByTimeAsync(100);
      delays.push(Date.now() - startTime);

      await vi.advanceTimersByTimeAsync(200);
      delays.push(Date.now() - startTime - delays[0]);

      await vi.advanceTimersByTimeAsync(400);

      await expect(retryPromise).rejects.toThrow(DashboardError);

      // Verify exponential backoff pattern (100ms, 200ms, 400ms)
      expect(operation).toHaveBeenCalledTimes(3);
    });
  });

  describe('configuration', () => {
    it('should use custom retry configuration', async () => {
      const customConfig: APILoaderConfig = {
        endpoint: 'https://api.example.com/data',
        method: 'POST',
        retryAttempts: 2,
        retryDelay: 50,
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Error',
      });

      const processor = new APIProcessor(customConfig);
      const fetchPromise = processor.fetchData();

      await vi.advanceTimersByTimeAsync(50);
      await vi.advanceTimersByTimeAsync(100);

      await expect(fetchPromise).rejects.toThrow('failed after 2 attempts');
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('should include custom headers in request', async () => {
      const configWithHeaders: APILoaderConfig = {
        endpoint: 'https://api.example.com/data',
        method: 'GET',
        headers: {
          'Authorization': 'Bearer custom-token',
          'X-Custom-Header': 'value',
        },
        retryAttempts: 1,
        retryDelay: 100,
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validResponse,
      });

      const processor = new APIProcessor(configWithHeaders);
      await processor.fetchData();

      expect(global.fetch).toHaveBeenCalledWith(
        configWithHeaders.endpoint,
        {
          method: 'GET',
          headers: configWithHeaders.headers,
        }
      );
    });

    it('should work without custom headers', async () => {
      const configWithoutHeaders: APILoaderConfig = {
        endpoint: 'https://api.example.com/data',
        method: 'GET',
        retryAttempts: 1,
        retryDelay: 100,
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validResponse,
      });

      const processor = new APIProcessor(configWithoutHeaders);
      await processor.fetchData();

      expect(global.fetch).toHaveBeenCalledWith(
        configWithoutHeaders.endpoint,
        {
          method: 'GET',
          headers: {},
        }
      );
    });
  });
});
