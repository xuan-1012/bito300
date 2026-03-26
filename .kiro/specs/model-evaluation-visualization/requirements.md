# Requirements Document: Model Evaluation Visualization

## Introduction

本系統為模型評估與視覺化模組，用於呈現機器學習模型或風險評分系統的效能表現。系統提供完整的評估圖表與分析工具，包含 Validation Curve、Learning Curve、Confusion Matrix、ROC Curve、Precision-Recall Curve、Threshold Analysis、Lift Curve 以及模型比較表格。所有圖表皆可輸出為高品質圖片，適合放入簡報或技術文件中。

核心價值主張：
- 完整評估：涵蓋模型效能的多個面向（準確度、過擬合、閾值選擇、排序能力）
- 簡報就緒：所有圖表皆為高品質、清晰易讀，可直接用於展示
- 易於理解：提供清楚的說明文字與視覺化設計
- 靈活輸出：支援多種圖片格式與尺寸

## Glossary

- **System**: 模型評估與視覺化系統
- **Model**: 機器學習模型或風險評分系統
- **Validation_Curve**: 驗證曲線，顯示超參數變化對訓練與驗證分數的影響
- **Learning_Curve**: 學習曲線，顯示訓練集大小對訓練與驗證分數的影響
- **Confusion_Matrix**: 混淆矩陣，顯示分類模型的 TP、FP、TN、FN
- **ROC_Curve**: ROC 曲線，顯示 True Positive Rate 與 False Positive Rate 的關係
- **AUC**: Area Under Curve，ROC 曲線下面積，範圍 0-1
- **Precision_Recall_Curve**: Precision-Recall 曲線，顯示 Precision 與 Recall 的權衡關係
- **Average_Precision**: 平均精確度，Precision-Recall 曲線下面積
- **Threshold_Analysis**: 閾值分析，顯示不同分類閾值下的 Precision、Recall、F1 Score
- **Lift_Curve**: Lift 曲線，顯示模型相對於隨機排序的提升效果
- **Model_Comparison_Table**: 模型比較表格，顯示多個模型版本的核心指標
- **Chart_Generator**: 圖表產生器，負責產生各類評估圖表
- **Metric_Calculator**: 指標計算器，負責計算評估指標
- **Image_Exporter**: 圖片匯出器，負責將圖表儲存為圖片檔案

## Requirements

### Requirement 1: Validation Curve Generation

**User Story:** As a data scientist, I want to generate validation curves, so that I can understand how hyperparameter changes affect model performance and identify overfitting.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives training scores and validation scores for different hyperparameter values, THE System SHALL plot both curves on the same chart
2. WHEN plotting the validation curve, THE System SHALL use the x-axis for hyperparameter values and y-axis for scores
3. WHEN plotting the validation curve, THE System SHALL display training scores with one color and validation scores with another color
4. WHEN plotting the validation curve, THE System SHALL include a legend identifying training and validation curves
5. WHEN plotting the validation curve, THE System SHALL include axis labels and a title
6. WHEN the validation curve is complete, THE System SHALL save the chart as a high-resolution image file
7. THE System SHALL support logarithmic scale for the x-axis when hyperparameter values span multiple orders of magnitude

### Requirement 2: Learning Curve Generation

**User Story:** As a data scientist, I want to generate learning curves, so that I can determine if the model is overfitting and whether adding more data would improve performance.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives training scores and validation scores for different training set sizes, THE System SHALL plot both curves on the same chart
2. WHEN plotting the learning curve, THE System SHALL use the x-axis for training set size and y-axis for scores
3. WHEN plotting the learning curve, THE System SHALL display training scores with one color and validation scores with another color
4. WHEN plotting the learning curve, THE System SHALL include shaded regions showing score variance if provided
5. WHEN plotting the learning curve, THE System SHALL include a legend identifying training and validation curves
6. WHEN plotting the learning curve, THE System SHALL include axis labels and a title
7. WHEN the learning curve is complete, THE System SHALL save the chart as a high-resolution image file

### Requirement 3: Confusion Matrix Visualization

**User Story:** As a data scientist, I want to visualize confusion matrices, so that I can understand the types of errors the model makes and present classification performance clearly.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives true labels and predicted labels, THE System SHALL calculate TP, FP, TN, FN counts
2. WHEN plotting the confusion matrix, THE System SHALL display the matrix as a heatmap with color intensity representing counts
3. WHEN plotting the confusion matrix, THE System SHALL display the count values as text within each cell
4. WHEN plotting the confusion matrix, THE System SHALL label rows as "Actual" and columns as "Predicted"
5. WHEN plotting the confusion matrix, THE System SHALL include class labels for each row and column
6. WHEN plotting the confusion matrix, THE System SHALL use a clear and professional color scheme
7. WHEN the confusion matrix is complete, THE System SHALL save the chart as a high-resolution image file suitable for presentations

### Requirement 4: ROC Curve Generation

**User Story:** As a data scientist, I want to generate ROC curves with AUC scores, so that I can evaluate binary classification performance and present results in presentations.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives true labels and predicted probabilities, THE System SHALL calculate True Positive Rate and False Positive Rate for multiple thresholds
2. WHEN plotting the ROC curve, THE System SHALL use the x-axis for False Positive Rate and y-axis for True Positive Rate
3. WHEN plotting the ROC curve, THE System SHALL calculate and display the AUC score in the legend or title
4. WHEN plotting the ROC curve, THE System SHALL include a diagonal reference line representing random performance
5. WHEN plotting the ROC curve, THE System SHALL include axis labels and a title
6. WHEN plotting the ROC curve, THE System SHALL use a clear line style and color
7. WHEN the ROC curve is complete, THE System SHALL save the chart as a high-resolution image file suitable for presentations

### Requirement 5: Precision-Recall Curve Generation

**User Story:** As a data scientist, I want to generate Precision-Recall curves, so that I can evaluate model performance on imbalanced datasets and determine optimal classification thresholds.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives true labels and predicted probabilities, THE System SHALL calculate Precision and Recall for multiple thresholds
2. WHEN plotting the Precision-Recall curve, THE System SHALL use the x-axis for Recall and y-axis for Precision
3. WHEN plotting the Precision-Recall curve, THE System SHALL calculate and display the Average Precision score in the legend or title
4. WHEN plotting the Precision-Recall curve, THE System SHALL include a horizontal reference line representing the baseline precision
5. WHEN plotting the Precision-Recall curve, THE System SHALL include axis labels and a title
6. WHEN plotting the Precision-Recall curve, THE System SHALL use a clear line style and color
7. WHEN the Precision-Recall curve is complete, THE System SHALL save the chart as a high-resolution image file

### Requirement 6: Threshold Analysis Plot Generation

**User Story:** As a data scientist, I want to generate threshold analysis plots, so that I can select the optimal classification threshold by comparing Precision, Recall, and F1 Score.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives true labels and predicted probabilities, THE System SHALL calculate Precision, Recall, and F1 Score for threshold values from 0 to 1
2. WHEN plotting the threshold analysis, THE System SHALL use the x-axis for threshold values and y-axis for metric values
3. WHEN plotting the threshold analysis, THE System SHALL display Precision, Recall, and F1 Score as three separate curves with different colors
4. WHEN plotting the threshold analysis, THE System SHALL include a legend identifying each metric curve
5. WHEN plotting the threshold analysis, THE System SHALL mark the threshold that maximizes F1 Score with a vertical line or annotation
6. WHEN plotting the threshold analysis, THE System SHALL include axis labels and a title
7. WHEN the threshold analysis plot is complete, THE System SHALL save the chart as a high-resolution image file

### Requirement 7: Lift Curve Generation

**User Story:** As a data scientist, I want to generate lift curves, so that I can demonstrate the model's ability to rank high-risk samples and compare it to random selection.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives true labels and predicted probabilities, THE System SHALL sort samples by predicted probability in descending order
2. WHEN plotting the lift curve, THE System SHALL use the x-axis for the percentage of samples and y-axis for the cumulative percentage of positive cases
3. WHEN plotting the lift curve, THE System SHALL display the model curve and a diagonal reference line representing random selection
4. WHEN plotting the lift curve, THE System SHALL calculate and display the lift value at specific percentiles in annotations or legend
5. WHEN plotting the lift curve, THE System SHALL include axis labels and a title
6. WHEN plotting the lift curve, THE System SHALL use clear line styles and colors to distinguish model and baseline
7. WHEN the lift curve is complete, THE System SHALL save the chart as a high-resolution image file

### Requirement 8: Model Comparison Table Generation

**User Story:** As a data scientist, I want to generate model comparison tables, so that I can compare core metrics across different model versions and select the best model.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives evaluation metrics for multiple models, THE System SHALL create a comparison table with models as rows and metrics as columns
2. WHEN creating the comparison table, THE System SHALL include metrics such as Accuracy, Precision, Recall, F1 Score, AUC, and Average Precision
3. WHEN creating the comparison table, THE System SHALL format numeric values to 4 decimal places
4. WHEN creating the comparison table, THE System SHALL highlight the best value in each metric column
5. WHEN creating the comparison table, THE System SHALL include model names or version identifiers as row labels
6. WHEN creating the comparison table, THE System SHALL use a clean and professional table design
7. WHEN the comparison table is complete, THE System SHALL save the table as a high-resolution image file or export as CSV

### Requirement 9: Chart Image Export

**User Story:** As a data scientist, I want to export charts as high-quality images, so that I can include them in presentations, reports, and README files.

#### Acceptance Criteria

1. WHEN the Image_Exporter saves a chart, THE System SHALL support PNG format with transparent background option
2. WHEN the Image_Exporter saves a chart, THE System SHALL support JPEG format for smaller file sizes
3. WHEN the Image_Exporter saves a chart, THE System SHALL support SVG format for vector graphics
4. WHEN the Image_Exporter saves a chart, THE System SHALL use a minimum resolution of 300 DPI for raster formats
5. WHEN the Image_Exporter saves a chart, THE System SHALL allow custom width and height specifications
6. WHEN the Image_Exporter saves a chart, THE System SHALL use descriptive filenames including chart type and timestamp
7. THE System SHALL save all exported images to a designated output directory

### Requirement 10: Chart Styling and Readability

**User Story:** As a data scientist, I want charts to be visually appealing and easy to read, so that they are suitable for presentations and do not look unprofessional.

#### Acceptance Criteria

1. THE System SHALL use a consistent color palette across all charts
2. THE System SHALL use font sizes that are readable when charts are displayed in presentations
3. THE System SHALL include grid lines on charts to improve readability
4. THE System SHALL use appropriate line widths and marker sizes for visibility
5. THE System SHALL ensure axis labels and titles do not overlap with chart elements
6. THE System SHALL use high-contrast colors for different curves or categories
7. THE System SHALL apply anti-aliasing to all chart elements for smooth rendering

### Requirement 11: Metric Calculation

**User Story:** As a data scientist, I want accurate metric calculations, so that I can trust the evaluation results and make informed decisions.

#### Acceptance Criteria

1. WHEN the Metric_Calculator receives true labels and predicted labels, THE System SHALL calculate Accuracy as the proportion of correct predictions
2. WHEN the Metric_Calculator receives true labels and predicted labels, THE System SHALL calculate Precision as TP divided by the sum of TP and FP
3. WHEN the Metric_Calculator receives true labels and predicted labels, THE System SHALL calculate Recall as TP divided by the sum of TP and FN
4. WHEN the Metric_Calculator receives true labels and predicted labels, THE System SHALL calculate F1 Score as the harmonic mean of Precision and Recall
5. WHEN the Metric_Calculator receives true labels and predicted probabilities, THE System SHALL calculate AUC using the trapezoidal rule
6. WHEN the Metric_Calculator receives true labels and predicted probabilities, THE System SHALL calculate Average Precision using the step function integration
7. IF the Metric_Calculator encounters division by zero, THEN THE System SHALL return NaN or a specified default value

### Requirement 12: Input Validation

**User Story:** As a data scientist, I want input validation for all chart generation functions, so that I receive clear error messages when providing invalid data.

#### Acceptance Criteria

1. WHEN the Chart_Generator receives input data, THE System SHALL validate that true labels and predicted values have the same length
2. WHEN the Chart_Generator receives input data for binary classification, THE System SHALL validate that labels contain only two unique values
3. WHEN the Chart_Generator receives predicted probabilities, THE System SHALL validate that all values are between 0 and 1
4. WHEN the Chart_Generator receives training and validation scores, THE System SHALL validate that both arrays have the same length
5. IF input validation fails, THEN THE System SHALL raise a descriptive error message indicating the validation issue
6. WHEN the Chart_Generator receives hyperparameter values, THE System SHALL validate that all values are numeric
7. WHEN the Chart_Generator receives model comparison data, THE System SHALL validate that all models have the same set of metrics

### Requirement 13: Batch Chart Generation

**User Story:** As a data scientist, I want to generate all evaluation charts in a single function call, so that I can quickly produce a complete evaluation report.

#### Acceptance Criteria

1. WHEN the System receives a batch generation request with true labels and predicted probabilities, THE System SHALL generate all applicable charts
2. WHEN generating charts in batch mode, THE System SHALL create a Confusion Matrix, ROC Curve, Precision-Recall Curve, and Threshold Analysis Plot
3. WHEN generating charts in batch mode, THE System SHALL save all charts to the same output directory
4. WHEN generating charts in batch mode, THE System SHALL use consistent naming conventions for all output files
5. WHEN generating charts in batch mode, THE System SHALL return a list of file paths for all generated charts
6. IF any chart generation fails in batch mode, THEN THE System SHALL log the error and continue generating remaining charts
7. WHEN batch generation completes, THE System SHALL create a summary report listing all generated charts and their file paths

### Requirement 14: Customization Options

**User Story:** As a data scientist, I want to customize chart appearance, so that I can match organizational branding or personal preferences.

#### Acceptance Criteria

1. THE System SHALL allow users to specify custom color palettes for charts
2. THE System SHALL allow users to specify custom font families and sizes
3. THE System SHALL allow users to specify custom figure sizes for charts
4. THE System SHALL allow users to enable or disable grid lines
5. THE System SHALL allow users to specify custom axis limits
6. THE System SHALL allow users to add custom annotations or text to charts
7. WHERE custom options are not provided, THE System SHALL use sensible default values

### Requirement 15: Documentation and Examples

**User Story:** As a data scientist, I want clear documentation and examples, so that I can quickly learn how to use the visualization system.

#### Acceptance Criteria

1. THE System SHALL provide docstrings for all public functions and classes
2. THE System SHALL include parameter descriptions, return value descriptions, and usage examples in docstrings
3. THE System SHALL provide example scripts demonstrating how to generate each chart type
4. THE System SHALL include sample data files for testing and demonstration purposes
5. THE System SHALL provide a README file with installation instructions and quick start guide
6. THE System SHALL include example output images showing what each chart type looks like
7. THE System SHALL document all customization options and their default values

### Requirement 16: Performance and Efficiency

**User Story:** As a data scientist, I want chart generation to be fast and efficient, so that I can iterate quickly during model development.

#### Acceptance Criteria

1. WHEN generating a single chart with up to 10,000 data points, THE System SHALL complete in less than 2 seconds
2. WHEN generating charts in batch mode with up to 10,000 data points, THE System SHALL complete all charts in less than 10 seconds
3. THE System SHALL use vectorized operations for metric calculations to improve performance
4. THE System SHALL avoid redundant calculations when generating multiple charts from the same data
5. WHEN saving charts to disk, THE System SHALL use efficient file I/O operations
6. THE System SHALL release memory resources after chart generation to prevent memory leaks
7. WHEN processing large datasets, THE System SHALL provide progress indicators for long-running operations
