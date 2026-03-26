import { describe, it, expect, beforeEach } from 'vitest';
import { z, ZodError } from 'zod';
import {
  DashboardError,
  ErrorHandler,
  formatValidationErrors,
} from '../errors';

describe('DashboardError', () => {
  it('should create a DashboardError with message and code', () => {
    const error = new DashboardError('Test error', 'TEST_ERROR');
    
    expect(error.message).toBe('Test error');
    expect(error.code).toBe('TEST_ERROR');
    expect(error.name).toBe('DashboardError');
    expect(error.timestamp).toBeInstanceOf(Date);
  });

  it('should use default code if not provided', () => {
    const error = new DashboardError('Test error');
    
    expect(error.code).toBe('DASHBOARD_ERROR');
  });

  it('should store context information', () => {
    const context = { userId: '123', action: 'load_data' };
    const error = new DashboardError('Test error', 'TEST_ERROR', context);
    
    expect(error.context).toEqual(context);
  });

  it('should be an instance of Error', () => {
    const error = new DashboardError('Test error');
    
    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(DashboardError);
  });
});

describe('ErrorHandler', () => {
  let errorHandler: ErrorHandler;

  beforeEach(() => {
    errorHandler = ErrorHandler.getInstance();
    errorHandler.clearErrorLog();
  });

  it('should be a singleton', () => {
    const instance1 = ErrorHandler.getInstance();
    const instance2 = ErrorHandler.getInstance();
    
    expect(instance1).toBe(instance2);
  });

  it('should log errors to internal log', () => {
    const error = new Error('Test error');
    
    errorHandler.logError(error);
    
    const log = errorHandler.getErrorLog();
    expect(log).toHaveLength(1);
    expect(log[0].error).toBe(error);
    expect(log[0].timestamp).toBeInstanceOf(Date);
  });

  it('should log errors with context', () => {
    const error = new Error('Test error');
    const context = { userId: '123' };
    
    errorHandler.logError(error, context);
    
    const log = errorHandler.getErrorLog();
    expect(log).toHaveLength(1);
  });

  it('should clear error log', () => {
    const error = new Error('Test error');
    
    errorHandler.logError(error);
    expect(errorHandler.getErrorLog()).toHaveLength(1);
    
    errorHandler.clearErrorLog();
    expect(errorHandler.getErrorLog()).toHaveLength(0);
  });

  describe('getUserFriendlyMessage', () => {
    it('should return DashboardError message as-is', () => {
      const error = new DashboardError('Custom error message', 'CUSTOM_ERROR');
      const message = errorHandler.getUserFriendlyMessage(error);
      
      expect(message).toBe('Custom error message');
    });

    it('should return friendly message for ZodError', () => {
      const schema = z.object({ name: z.string() });
      let zodError: ZodError;
      
      try {
        schema.parse({ name: 123 });
      } catch (error) {
        zodError = error as ZodError;
      }
      
      const message = errorHandler.getUserFriendlyMessage(zodError!);
      expect(message).toBe('Data validation failed. Please check your input data format.');
    });

    it('should return friendly message for fetch errors', () => {
      const error = new Error('fetch failed: network error');
      const message = errorHandler.getUserFriendlyMessage(error);
      
      expect(message).toBe('Failed to load data. Please check your network connection and try again.');
    });

    it('should return friendly message for parse errors', () => {
      const error = new Error('Failed to parse JSON');
      const message = errorHandler.getUserFriendlyMessage(error);
      
      expect(message).toBe('Failed to parse data. Please ensure your data is in the correct format.');
    });

    it('should return generic message for unknown errors', () => {
      const error = new Error('Unknown error');
      const message = errorHandler.getUserFriendlyMessage(error);
      
      expect(message).toBe('An unexpected error occurred. Please try again or contact support.');
    });
  });
});

describe('formatValidationErrors', () => {
  it('should format ZodError with single error', () => {
    const schema = z.object({ name: z.string() });
    let zodError: ZodError;
    
    try {
      schema.parse({ name: 123 });
    } catch (error) {
      zodError = error as ZodError;
    }
    
    const formatted = formatValidationErrors(zodError!);
    
    expect(formatted).toContain('Validation errors:');
    expect(formatted).toContain('name:');
  });

  it('should format ZodError with multiple errors', () => {
    const schema = z.object({
      name: z.string(),
      age: z.number(),
      email: z.string().email(),
    });
    let zodError: ZodError;
    
    try {
      schema.parse({ name: 123, age: 'invalid', email: 'not-an-email' });
    } catch (error) {
      zodError = error as ZodError;
    }
    
    const formatted = formatValidationErrors(zodError!);
    
    expect(formatted).toContain('Validation errors:');
    expect(formatted).toContain('name:');
    expect(formatted).toContain('age:');
    expect(formatted).toContain('email:');
  });

  it('should format nested path errors', () => {
    const schema = z.object({
      user: z.object({
        profile: z.object({
          name: z.string(),
        }),
      }),
    });
    let zodError: ZodError;
    
    try {
      schema.parse({ user: { profile: { name: 123 } } });
    } catch (error) {
      zodError = error as ZodError;
    }
    
    const formatted = formatValidationErrors(zodError!);
    
    expect(formatted).toContain('user.profile.name:');
  });
});
