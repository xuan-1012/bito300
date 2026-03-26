/**
 * Error handling utilities for Financial Risk Dashboard
 * Provides custom error classes and error formatting utilities
 */

import { ZodError } from 'zod';

/**
 * Custom error class for Dashboard-specific errors
 * Extends the native Error class with additional context
 */
export class DashboardError extends Error {
  public readonly code: string;
  public readonly context?: Record<string, unknown>;
  public readonly timestamp: Date;

  constructor(
    message: string,
    code: string = 'DASHBOARD_ERROR',
    context?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'DashboardError';
    this.code = code;
    this.context = context;
    this.timestamp = new Date();

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, DashboardError);
    }
  }
}

/**
 * Error handler class for centralized error management
 * Provides logging and user-friendly error message generation
 */
export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: Array<{ error: Error; timestamp: Date }> = [];

  private constructor() {}

  /**
   * Gets the singleton instance of ErrorHandler
   */
  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  /**
   * Logs an error to the console and internal error log
   * @param error - The error to log
   * @param context - Additional context information
   */
  public logError(error: Error, context?: Record<string, unknown>): void {
    const timestamp = new Date();
    
    // Add to internal log
    this.errorLog.push({ error, timestamp });

    // Log to console with context
    console.error('[Dashboard Error]', {
      message: error.message,
      name: error.name,
      timestamp: timestamp.toISOString(),
      context,
      stack: error.stack,
    });
  }

  /**
   * Converts an error to a user-friendly message
   * @param error - The error to convert
   * @returns User-friendly error message
   */
  public getUserFriendlyMessage(error: Error): string {
    if (error instanceof DashboardError) {
      return error.message;
    }

    if (error instanceof ZodError) {
      return 'Data validation failed. Please check your input data format.';
    }

    if (error.message.includes('fetch')) {
      return 'Failed to load data. Please check your network connection and try again.';
    }

    if (error.message.includes('parse')) {
      return 'Failed to parse data. Please ensure your data is in the correct format.';
    }

    return 'An unexpected error occurred. Please try again or contact support.';
  }

  /**
   * Gets the error log
   * @returns Array of logged errors with timestamps
   */
  public getErrorLog(): Array<{ error: Error; timestamp: Date }> {
    return [...this.errorLog];
  }

  /**
   * Clears the error log
   */
  public clearErrorLog(): void {
    this.errorLog = [];
  }
}

/**
 * Formats Zod validation errors into a readable string
 * @param error - The ZodError to format
 * @returns Formatted error message with field-specific errors
 * @example
 * formatValidationErrors(zodError)
 * // "Validation errors:
 * //  - risk_score: Expected number, received string
 * //  - risk_level: Invalid enum value"
 */
export function formatValidationErrors(error: ZodError): string {
  const errors = error.errors.map((err) => {
    const path = err.path.join('.');
    return `  - ${path}: ${err.message}`;
  });

  return `Validation errors:\n${errors.join('\n')}`;
}
