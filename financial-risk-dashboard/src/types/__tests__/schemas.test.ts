import { describe, it, expect } from 'vitest';
import {
  RiskLevelSchema,
  RiskFactorSchema,
  AccountSchema,
  ValidationCurveSchema,
  LearningCurveSchema,
  ConfusionMatrixSchema,
  ROCCurveSchema,
  PRCurveSchema,
  LiftCurveSchema,
  ThresholdAnalysisSchema,
  FeatureImportanceSchema,
  DashboardChartsSchema,
  DashboardDataSchema,
} from '../schemas';

describe('Zod Validation Schemas', () => {
  describe('RiskLevelSchema', () => {
    it('should accept valid risk levels', () => {
      expect(RiskLevelSchema.parse('LOW')).toBe('LOW');
      expect(RiskLevelSchema.parse('MEDIUM')).toBe('MEDIUM');
      expect(RiskLevelSchema.parse('HIGH')).toBe('HIGH');
      expect(RiskLevelSchema.parse('CRITICAL')).toBe('CRITICAL');
    });

    it('should reject invalid risk levels', () => {
      expect(() => RiskLevelSchema.parse('INVALID')).toThrow();
      expect(() => RiskLevelSchema.parse('low')).toThrow();
      expect(() => RiskLevelSchema.parse('')).toThrow();
    });
  });

  describe('RiskFactorSchema', () => {
    it('should accept valid risk factor', () => {
      const validFactor = {
        factor_name: 'High Transaction Volume',
        contribution_percentage: 45.5,
        description: 'Unusually high transaction volume detected',
      };
      expect(RiskFactorSchema.parse(validFactor)).toEqual(validFactor);
    });

    it('should reject risk factor with invalid contribution percentage', () => {
      const invalidFactor = {
        factor_name: 'Test',
        contribution_percentage: 150,
        description: 'Test',
      };
      expect(() => RiskFactorSchema.parse(invalidFactor)).toThrow();
    });

    it('should reject risk factor with negative contribution percentage', () => {
      const invalidFactor = {
        factor_name: 'Test',
        contribution_percentage: -10,
        description: 'Test',
      };
      expect(() => RiskFactorSchema.parse(invalidFactor)).toThrow();
    });
  });

  describe('AccountSchema', () => {
    it('should accept valid account', () => {
      const validAccount = {
        account_id: 'ACC001',
        risk_score: 85.5,
        risk_level: 'HIGH',
        risk_factors: [
          {
            factor_name: 'High Transaction Volume',
            contribution_percentage: 45.5,
            description: 'Unusually high transaction volume',
          },
        ],
        feature_values: {
          transaction_count: 150,
          avg_amount: 5000,
        },
        explanation: 'This account shows suspicious activity',
      };
      expect(AccountSchema.parse(validAccount)).toEqual(validAccount);
    });

    it('should reject account with invalid risk score', () => {
      const invalidAccount = {
        account_id: 'ACC001',
        risk_score: 150,
        risk_level: 'HIGH',
        risk_factors: [],
        feature_values: {},
        explanation: 'Test',
      };
      expect(() => AccountSchema.parse(invalidAccount)).toThrow();
    });

    it('should reject account with risk score below 0', () => {
      const invalidAccount = {
        account_id: 'ACC001',
        risk_score: -10,
        risk_level: 'HIGH',
        risk_factors: [],
        feature_values: {},
        explanation: 'Test',
      };
      expect(() => AccountSchema.parse(invalidAccount)).toThrow();
    });
  });

  describe('ValidationCurveSchema', () => {
    it('should accept valid validation curve data', () => {
      const validData = {
        param_values: [0.1, 0.5, 1.0, 5.0, 10.0],
        train_scores: [0.85, 0.88, 0.90, 0.89, 0.87],
        validation_scores: [0.82, 0.84, 0.86, 0.85, 0.83],
        param_name: 'C',
      };
      expect(ValidationCurveSchema.parse(validData)).toEqual(validData);
    });

    it('should reject validation curve with missing param_name', () => {
      const invalidData = {
        param_values: [0.1, 0.5],
        train_scores: [0.85, 0.88],
        validation_scores: [0.82, 0.84],
      };
      expect(() => ValidationCurveSchema.parse(invalidData)).toThrow();
    });
  });

  describe('LearningCurveSchema', () => {
    it('should accept valid learning curve data', () => {
      const validData = {
        train_sizes: [100, 200, 500, 1000],
        train_scores: [0.85, 0.88, 0.90, 0.91],
        validation_scores: [0.82, 0.84, 0.86, 0.87],
      };
      expect(LearningCurveSchema.parse(validData)).toEqual(validData);
    });

    it('should accept learning curve data with standard deviations', () => {
      const validData = {
        train_sizes: [100, 200],
        train_scores: [0.85, 0.88],
        validation_scores: [0.82, 0.84],
        train_scores_std: [0.02, 0.015],
        validation_scores_std: [0.03, 0.025],
      };
      expect(LearningCurveSchema.parse(validData)).toEqual(validData);
    });
  });

  describe('ConfusionMatrixSchema', () => {
    it('should accept valid confusion matrix data', () => {
      const validData = {
        true_positives: 85,
        false_positives: 15,
        true_negatives: 890,
        false_negatives: 10,
      };
      expect(ConfusionMatrixSchema.parse(validData)).toEqual(validData);
    });

    it('should reject confusion matrix with missing fields', () => {
      const invalidData = {
        true_positives: 85,
        false_positives: 15,
      };
      expect(() => ConfusionMatrixSchema.parse(invalidData)).toThrow();
    });
  });

  describe('ROCCurveSchema', () => {
    it('should accept valid ROC curve data', () => {
      const validData = {
        fpr: [0.0, 0.1, 0.3, 0.5, 1.0],
        tpr: [0.0, 0.6, 0.8, 0.9, 1.0],
        auc: 0.85,
      };
      expect(ROCCurveSchema.parse(validData)).toEqual(validData);
    });

    it('should reject ROC curve with missing auc', () => {
      const invalidData = {
        fpr: [0.0, 0.1],
        tpr: [0.0, 0.6],
      };
      expect(() => ROCCurveSchema.parse(invalidData)).toThrow();
    });
  });

  describe('PRCurveSchema', () => {
    it('should accept valid PR curve data', () => {
      const validData = {
        recall: [0.0, 0.2, 0.5, 0.8, 1.0],
        precision: [1.0, 0.95, 0.90, 0.85, 0.80],
        average_precision: 0.88,
      };
      expect(PRCurveSchema.parse(validData)).toEqual(validData);
    });
  });

  describe('LiftCurveSchema', () => {
    it('should accept valid lift curve data', () => {
      const validData = {
        percentiles: [0.1, 0.2, 0.3, 0.5, 1.0],
        cumulative_positives: [0.3, 0.5, 0.65, 0.85, 1.0],
        baseline: [0.1, 0.2, 0.3, 0.5, 1.0],
      };
      expect(LiftCurveSchema.parse(validData)).toEqual(validData);
    });
  });

  describe('ThresholdAnalysisSchema', () => {
    it('should accept valid threshold analysis data', () => {
      const validData = {
        thresholds: [0.1, 0.3, 0.5, 0.7, 0.9],
        precision: [0.75, 0.80, 0.85, 0.88, 0.90],
        recall: [0.95, 0.90, 0.85, 0.75, 0.60],
        f1_score: [0.84, 0.85, 0.85, 0.81, 0.72],
        optimal_threshold: 0.5,
      };
      expect(ThresholdAnalysisSchema.parse(validData)).toEqual(validData);
    });
  });

  describe('FeatureImportanceSchema', () => {
    it('should accept valid feature importance data', () => {
      const validData = {
        features: ['transaction_count', 'avg_amount', 'account_age'],
        importance: [0.45, 0.35, 0.20],
      };
      expect(FeatureImportanceSchema.parse(validData)).toEqual(validData);
    });
  });

  describe('DashboardChartsSchema', () => {
    it('should accept valid dashboard charts with all null values', () => {
      const validData = {
        validation_curve: null,
        learning_curve: null,
        confusion_matrix: null,
        roc_curve: null,
        pr_curve: null,
        lift_curve: null,
        threshold_analysis: null,
        feature_importance: null,
      };
      expect(DashboardChartsSchema.parse(validData)).toEqual(validData);
    });

    it('should accept valid dashboard charts with some populated values', () => {
      const validData = {
        validation_curve: null,
        learning_curve: null,
        confusion_matrix: {
          true_positives: 85,
          false_positives: 15,
          true_negatives: 890,
          false_negatives: 10,
        },
        roc_curve: {
          fpr: [0.0, 0.1, 1.0],
          tpr: [0.0, 0.8, 1.0],
          auc: 0.85,
        },
        pr_curve: null,
        lift_curve: null,
        threshold_analysis: null,
        feature_importance: null,
      };
      expect(DashboardChartsSchema.parse(validData)).toEqual(validData);
    });
  });

  describe('DashboardDataSchema', () => {
    it('should accept valid dashboard data', () => {
      const validData = {
        accounts: [
          {
            account_id: 'ACC001',
            risk_score: 85.5,
            risk_level: 'HIGH',
            risk_factors: [
              {
                factor_name: 'High Transaction Volume',
                contribution_percentage: 45.5,
                description: 'Unusually high transaction volume',
              },
            ],
            feature_values: {
              transaction_count: 150,
            },
            explanation: 'Suspicious activity detected',
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
      expect(DashboardDataSchema.parse(validData)).toEqual(validData);
    });

    it('should reject dashboard data with invalid account', () => {
      const invalidData = {
        accounts: [
          {
            account_id: 'ACC001',
            risk_score: 150, // Invalid: > 100
            risk_level: 'HIGH',
            risk_factors: [],
            feature_values: {},
            explanation: 'Test',
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
      expect(() => DashboardDataSchema.parse(invalidData)).toThrow();
    });
  });
});
