// Zod validation schemas for Financial Risk Dashboard
import { z } from 'zod';

// Risk level enum schema
export const RiskLevelSchema = z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']);

// Risk factor schema
export const RiskFactorSchema = z.object({
  factor_name: z.string(),
  contribution_percentage: z.number().min(0).max(100),
  description: z.string(),
});

// Account schema
export const AccountSchema = z.object({
  account_id: z.string(),
  risk_score: z.number().min(0).max(100),
  risk_level: RiskLevelSchema,
  risk_factors: z.array(RiskFactorSchema),
  feature_values: z.record(z.string(), z.number()),
  explanation: z.string(),
});

// Chart data schemas
export const ValidationCurveSchema = z.object({
  param_values: z.array(z.number()),
  train_scores: z.array(z.number()),
  validation_scores: z.array(z.number()),
  param_name: z.string(),
});

export const LearningCurveSchema = z.object({
  train_sizes: z.array(z.number()),
  train_scores: z.array(z.number()),
  validation_scores: z.array(z.number()),
  train_scores_std: z.array(z.number()).optional(),
  validation_scores_std: z.array(z.number()).optional(),
});

export const ConfusionMatrixSchema = z.object({
  true_positives: z.number(),
  false_positives: z.number(),
  true_negatives: z.number(),
  false_negatives: z.number(),
});

export const ROCCurveSchema = z.object({
  fpr: z.array(z.number()),
  tpr: z.array(z.number()),
  auc: z.number(),
});

export const PRCurveSchema = z.object({
  recall: z.array(z.number()),
  precision: z.array(z.number()),
  average_precision: z.number(),
});

export const LiftCurveSchema = z.object({
  percentiles: z.array(z.number()),
  cumulative_positives: z.array(z.number()),
  baseline: z.array(z.number()),
});

export const ThresholdAnalysisSchema = z.object({
  thresholds: z.array(z.number()),
  precision: z.array(z.number()),
  recall: z.array(z.number()),
  f1_score: z.array(z.number()),
  optimal_threshold: z.number(),
});

export const FeatureImportanceSchema = z.object({
  features: z.array(z.string()),
  importance: z.array(z.number()),
});

// Dashboard charts schema
export const DashboardChartsSchema = z.object({
  validation_curve: ValidationCurveSchema.nullable(),
  learning_curve: LearningCurveSchema.nullable(),
  confusion_matrix: ConfusionMatrixSchema.nullable(),
  roc_curve: ROCCurveSchema.nullable(),
  pr_curve: PRCurveSchema.nullable(),
  lift_curve: LiftCurveSchema.nullable(),
  threshold_analysis: ThresholdAnalysisSchema.nullable(),
  feature_importance: FeatureImportanceSchema.nullable(),
});

// Dashboard data schema
export const DashboardDataSchema = z.object({
  accounts: z.array(AccountSchema),
  charts: DashboardChartsSchema,
});

// Type exports inferred from schemas
export type RiskLevelType = z.infer<typeof RiskLevelSchema>;
export type RiskFactorType = z.infer<typeof RiskFactorSchema>;
export type AccountType = z.infer<typeof AccountSchema>;
export type ValidationCurveType = z.infer<typeof ValidationCurveSchema>;
export type LearningCurveType = z.infer<typeof LearningCurveSchema>;
export type ConfusionMatrixType = z.infer<typeof ConfusionMatrixSchema>;
export type ROCCurveType = z.infer<typeof ROCCurveSchema>;
export type PRCurveType = z.infer<typeof PRCurveSchema>;
export type LiftCurveType = z.infer<typeof LiftCurveSchema>;
export type ThresholdAnalysisType = z.infer<typeof ThresholdAnalysisSchema>;
export type FeatureImportanceType = z.infer<typeof FeatureImportanceSchema>;
export type DashboardChartsType = z.infer<typeof DashboardChartsSchema>;
export type DashboardDataType = z.infer<typeof DashboardDataSchema>;
