# Requirements Document

## Introduction

超參數搜尋優化模組是一個專為防詐/可疑帳號偵測設計的機器學習模型調優系統。系統需要支援多種主流演算法，針對極度不平衡的資料集進行最佳化，使用分層交叉驗證確保評估的可靠性，並以多個評估指標找出最佳的超參數組合與決策閾值。系統最終產出完整的比較分析報告，協助使用者選擇最適合的模型配置。

## Glossary

- **Search_Engine**: 超參數搜尋引擎，負責執行模型訓練與超參數優化
- **Model_Factory**: 模型工廠，負責建立不同類型的機器學習模型實例
- **Threshold_Optimizer**: 閾值優化器，負責掃描並找出最佳決策閾值
- **Report_Generator**: 報告產生器，負責產生比較表與風險分析報告
- **Stratified_Split**: 分層切分，確保訓練集與驗證集的類別比例一致
- **Stratified_K-Fold**: 分層 K 折交叉驗證，確保每個 fold 的類別比例一致
- **PR-AUC**: Precision-Recall Area Under Curve，精確率-召回率曲線下面積
- **Imbalance_Ratio**: 不平衡比例，負樣本數量除以正樣本數量

## Requirements

### Requirement 1: 支援多種機器學習演算法

**User Story:** 作為資料科學家，我希望系統支援多種主流演算法，以便比較不同模型在防詐偵測任務上的表現。

#### Acceptance Criteria

1. THE Model_Factory SHALL support Logistic Regression model creation
2. THE Model_Factory SHALL support Decision Tree model creation
3. THE Model_Factory SHALL support Random Forest model creation
4. THE Model_Factory SHALL support XGBoost model creation
5. THE Model_Factory SHALL support LightGBM model creation
6. WHEN creating a model, THE Model_Factory SHALL accept hyperparameters as input
7. WHEN creating a model, THE Model_Factory SHALL return a trained model instance

### Requirement 2: 資料分層切分

**User Story:** 作為資料科學家，我希望系統使用分層切分方法，以確保訓練集與驗證集的類別比例一致，避免評估偏差。

#### Acceptance Criteria

1. WHEN splitting data, THE Search_Engine SHALL use stratified split method
2. WHEN splitting data, THE Search_Engine SHALL preserve the class ratio between training and validation sets
3. WHEN splitting data, THE Search_Engine SHALL ensure the difference in class ratios is less than 1%
4. THE Search_Engine SHALL use a configurable random seed for reproducibility

### Requirement 3: 分層交叉驗證

**User Story:** 作為資料科學家，我希望系統使用分層 K 折交叉驗證，以獲得更可靠的模型性能評估。

#### Acceptance Criteria

1. WHEN training models, THE Search_Engine SHALL use stratified k-fold cross-validation
2. THE Search_Engine SHALL support configurable number of folds (default 5)
3. WHEN performing cross-validation, THE Search_Engine SHALL preserve class ratio in each fold
4. WHEN performing cross-validation, THE Search_Engine SHALL record scores for each fold
5. WHEN performing cross-validation, THE Search_Engine SHALL compute mean and standard deviation of scores

### Requirement 4: 多指標評估

**User Story:** 作為資料科學家，我希望系統提供多個評估指標，以全面了解模型在不平衡資料集上的表現。

#### Acceptance Criteria

1. WHEN evaluating a model, THE Search_Engine SHALL compute PR-AUC score
2. WHEN evaluating a model, THE Search_Engine SHALL compute Precision score
3. WHEN evaluating a model, THE Search_Engine SHALL compute Recall score
4. WHEN evaluating a model, THE Search_Engine SHALL compute F1 score
5. WHEN evaluating a model, THE Search_Engine SHALL compute confusion matrix
6. THE Search_Engine SHALL ensure all metric values are within the range [0, 1]

### Requirement 5: 決策閾值掃描

**User Story:** 作為資料科學家，我希望系統自動掃描多個決策閾值，以找出最適合業務需求的閾值設定。

#### Acceptance Criteria

1. WHEN optimizing threshold, THE Threshold_Optimizer SHALL scan from 0.10 to 0.45 with step size 0.05
2. WHEN optimizing threshold, THE Threshold_Optimizer SHALL evaluate metrics at each threshold value
3. WHEN optimizing threshold, THE Threshold_Optimizer SHALL record the best threshold and corresponding metrics
4. THE Threshold_Optimizer SHALL support configurable threshold range
5. THE Threshold_Optimizer SHALL ensure threshold values are within the range [0, 1]

### Requirement 6: 極度不平衡資料處理

**User Story:** 作為資料科學家，我希望系統能偵測極度不平衡的資料集，並自動擴展閾值掃描範圍，以找出更適合的決策閾值。

#### Acceptance Criteria

1. WHEN the imbalance ratio exceeds 100, THE Threshold_Optimizer SHALL extend threshold scan to range 0.05 to 0.10
2. WHEN extending threshold range, THE Threshold_Optimizer SHALL use step size 0.05
3. WHEN extending threshold range, THE Threshold_Optimizer SHALL combine results from both standard and extended ranges
4. THE Threshold_Optimizer SHALL compute imbalance ratio as negative samples divided by positive samples

### Requirement 7: 超參數網格搜尋

**User Story:** 作為資料科學家，我希望系統能自動搜尋超參數空間，以找出最佳的超參數組合。

#### Acceptance Criteria

1. WHEN searching hyperparameters, THE Search_Engine SHALL accept a parameter grid as input
2. WHEN searching hyperparameters, THE Search_Engine SHALL evaluate all combinations in the grid
3. WHEN searching hyperparameters, THE Search_Engine SHALL record results for each combination
4. WHEN searching hyperparameters, THE Search_Engine SHALL identify the best parameter combination based on validation metrics
5. THE Search_Engine SHALL ensure the best parameters come from the provided search space

### Requirement 8: 比較報告產生

**User Story:** 作為資料科學家，我希望系統產生清晰的比較報告，以便快速了解不同模型與參數組合的表現差異。

#### Acceptance Criteria

1. WHEN generating a report, THE Report_Generator SHALL create a comparison table in Markdown format
2. WHEN generating a report, THE Report_Generator SHALL include model type, best parameters, best threshold, and all evaluation metrics
3. WHEN generating a report, THE Report_Generator SHALL rank models by PR-AUC score
4. WHEN generating a report, THE Report_Generator SHALL highlight the best performing model
5. THE Report_Generator SHALL ensure the comparison table is human-readable

### Requirement 9: 風險分析

**User Story:** 作為資料科學家，我希望系統提供風險分析，以了解模型選擇的潛在風險與注意事項。

#### Acceptance Criteria

1. WHEN generating risk analysis, THE Report_Generator SHALL analyze model stability based on cross-validation scores
2. WHEN generating risk analysis, THE Report_Generator SHALL identify models with high variance in cross-validation
3. WHEN generating risk analysis, THE Report_Generator SHALL provide recommendations based on metric trade-offs
4. WHEN generating risk analysis, THE Report_Generator SHALL warn about potential overfitting risks
5. THE Report_Generator SHALL ensure risk analysis is presented in clear text format

### Requirement 10: 訓練時間記錄

**User Story:** 作為資料科學家，我希望系統記錄每個模型的訓練時間，以便在性能與效率之間做出權衡。

#### Acceptance Criteria

1. WHEN training a model, THE Search_Engine SHALL record the start time
2. WHEN training completes, THE Search_Engine SHALL record the end time
3. WHEN training completes, THE Search_Engine SHALL compute the total training time
4. WHEN generating a report, THE Report_Generator SHALL include training time for each model
5. THE Search_Engine SHALL ensure training time is measured in seconds

### Requirement 11: 結果可重現性

**User Story:** 作為資料科學家，我希望系統的搜尋結果可重現，以便驗證與除錯。

#### Acceptance Criteria

1. THE Search_Engine SHALL accept a random seed parameter
2. WHEN a random seed is provided, THE Search_Engine SHALL use it for all random operations
3. WHEN a random seed is provided, THE Search_Engine SHALL produce identical results across multiple runs
4. THE Search_Engine SHALL use the random seed for data splitting, cross-validation, and model training
5. THE Search_Engine SHALL default to random seed 42 if not specified

### Requirement 12: 平行處理支援

**User Story:** 作為資料科學家，我希望系統支援平行處理，以加速超參數搜尋過程。

#### Acceptance Criteria

1. THE Search_Engine SHALL accept an n_jobs parameter for parallel processing
2. WHEN n_jobs is set to -1, THE Search_Engine SHALL use all available CPU cores
3. WHEN n_jobs is greater than 0, THE Search_Engine SHALL use the specified number of cores
4. THE Search_Engine SHALL apply parallel processing to cross-validation and hyperparameter search
5. THE Search_Engine SHALL ensure thread-safe operations during parallel execution
