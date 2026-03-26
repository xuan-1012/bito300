# Implementation Plan: Presentation Charts Generation

## Overview

This implementation plan creates a presentation chart generation system for the 3/26 cryptocurrency suspicious account detection competition. The system extends the existing `model_evaluation_viz` module to support 9 types of presentation charts including AWS architecture diagrams, system flow diagrams, and model evaluation charts. All charts use a unified AWS/FinTech style suitable for 16:9 presentation format with dual Mermaid and PNG export support.

## Tasks

- [x] 1. Set up presentation charts module structure
  - Create `src/presentation_charts/` directory
  - Create `__init__.py` with module exports
  - Create `models.py` for PresentationConfig, ChartMetadata, BatchGenerationResult data classes
  - Create `constants.py` for AWS colors, chart dimensions, and style configurations
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ]* 1.1 Write unit tests for data models
  - Test PresentationConfig validation
  - Test ChartMetadata creation
  - Test BatchGenerationResult aggregation
  - _Requirements: 10.1, 10.2, 10.4_

- [ ] 2. Implement system overview diagram generator
  - [x] 2.1 Create `src/presentation_charts/generators/system_overview.py`
    - Implement `generate_system_overview(config: PresentationConfig) -> Figure`
    - Draw components: BitoPro API, Lambda Functions, S3, DynamoDB, Bedrock, Step Functions
    - Use Mermaid graph TB format for data flow
    - Apply color coding for compute, storage, AI/ML, orchestration layers
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 2.2 Write property test for system overview diagram
    - **Property 1: Architecture diagram generation completeness**
    - **Validates: Requirements 1.1, 2.1**
    - Test that all required components are present
    - Test aspect ratio is 16:9
    - Test DPI is 300

  - [ ] 2.3 Implement Mermaid source extraction for system overview
    - Generate Mermaid graph TB source code
    - Store in ChartMetadata.mermaid_source
    - _Requirements: 2.4, 11.2_

- [ ] 3. Implement AWS architecture diagram generator
  - [ ] 3.1 Create `src/presentation_charts/generators/aws_architecture.py`
    - Implement `generate_aws_architecture(config: PresentationConfig) -> Figure`
    - Draw all AWS services: Lambda, S3, DynamoDB, Step Functions, Bedrock, Secrets Manager, CloudWatch
    - Mark data flow and call relationships between services
    - Use AWS official color scheme for different service types
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 3.2 Write unit tests for AWS architecture diagram
    - Test all AWS components are rendered
    - Test connections between services
    - Test AWS color scheme application
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 3.3 Implement Mermaid source extraction for AWS architecture
    - Generate Mermaid graph with AWS service nodes
    - Store in ChartMetadata.mermaid_source
    - _Requirements: 3.4, 11.2_

- [ ] 4. Implement data flow diagram generator
  - [ ] 4.1 Create `src/presentation_charts/generators/data_flow.py`
    - Implement `generate_data_flow(config: PresentationConfig) -> Figure`
    - Draw four stages: data ingestion, feature extraction, risk analysis, report generation
    - Mark input/output data formats (JSON, CSV, PNG/PDF) for each stage
    - Use arrows to show data flow between stages
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 4.2 Write unit tests for data flow diagram
    - Test all four stages are present
    - Test data format annotations
    - Test arrow connections
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 4.3 Implement Mermaid source extraction for data flow
    - Generate Mermaid flowchart LR source code
    - Store in ChartMetadata.mermaid_source
    - _Requirements: 4.4, 11.2_

- [ ] 5. Checkpoint - Ensure architecture diagram tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement model comparison chart generator
  - [ ] 6.1 Create `src/presentation_charts/generators/model_comparison.py`
    - Implement `generate_model_comparison(config: PresentationConfig, model_data: Dict) -> Figure`
    - Display Accuracy, Precision, Recall, F1 Score, AUC metrics
    - Use different colors for different models (XGBoost, Random Forest)
    - Create grouped bar chart with side-by-side comparison
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 6.2 Write property test for model comparison chart
    - **Property 10: Model comparison chart metric completeness**
    - **Validates: Requirements 5.2**
    - Test all five metrics are displayed
    - **Property 11: Model comparison chart color differentiation**
    - **Validates: Requirements 5.3**
    - Test different models use different colors

- [ ] 7. Implement PR and ROC curve generators
  - [ ] 7.1 Create `src/presentation_charts/generators/pr_roc_curves.py`
    - Implement `generate_pr_curve(config: PresentationConfig, model_data: Dict) -> Figure`
    - Calculate and display AUC-PR value
    - Implement `generate_roc_curve(config: PresentationConfig, model_data: Dict) -> Figure`
    - Display AUC-ROC value and diagonal baseline
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 7.2 Write property tests for PR and ROC curves
    - **Property 12: PR curve annotation completeness**
    - **Validates: Requirements 6.3**
    - Test AUC-PR value is displayed
    - **Property 13: ROC curve annotation completeness**
    - **Validates: Requirements 6.4**
    - Test AUC-ROC value and diagonal baseline are present

- [ ] 8. Implement confusion matrix generator
  - [ ] 8.1 Create `src/presentation_charts/generators/confusion_matrix_presentation.py`
    - Implement `generate_confusion_matrix(config: PresentationConfig, model_data: Dict) -> Figure`
    - Display TP, TN, FP, FN values in heatmap
    - Use color intensity to represent value magnitude
    - Label Normal and Suspicious classes
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 8.2 Write property tests for confusion matrix
    - **Property 14: Confusion matrix completeness**
    - **Validates: Requirements 7.2**
    - Test all four values (TP, TN, FP, FN) are displayed
    - **Property 15: Confusion matrix color mapping**
    - **Validates: Requirements 7.3**
    - Test larger values use darker colors

- [ ] 9. Implement threshold analysis chart generator
  - [ ] 9.1 Create `src/presentation_charts/generators/threshold_analysis_presentation.py`
    - Implement `generate_threshold_analysis(config: PresentationConfig, model_data: Dict) -> Figure`
    - Display Precision, Recall, F1 Score curves across thresholds
    - Mark optimal F1 Score threshold point
    - Configure X-axis for threshold range (0.0 to 1.0), Y-axis for metric values
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 9.2 Write property tests for threshold analysis
    - **Property 16: Threshold analysis curve completeness**
    - **Validates: Requirements 8.2**
    - Test all three curves are present
    - **Property 17: Threshold analysis optimal point annotation**
    - **Validates: Requirements 8.3**
    - Test optimal F1 threshold is marked
    - **Property 18: Threshold analysis axis configuration**
    - **Validates: Requirements 8.4**
    - Test X-axis range is 0.0-1.0

- [ ] 10. Implement feature importance chart generator
  - [ ] 10.1 Create `src/presentation_charts/generators/feature_importance_presentation.py`
    - Implement `generate_feature_importance(config: PresentationConfig, model_data: Dict) -> Figure`
    - Sort features by importance (high to low)
    - Display importance percentage for each feature
    - Limit to top 20 features if more than 20 provided
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ]* 10.2 Write property tests for feature importance
    - **Property 19: Feature importance sorting**
    - **Validates: Requirements 9.2**
    - Test features are sorted by importance
    - **Property 20: Feature importance percentage display**
    - **Validates: Requirements 9.3**
    - Test percentages are shown
    - **Property 21: Feature importance truncation**
    - **Validates: Requirements 9.4**
    - Test only top 20 features shown when >20 provided

- [ ] 11. Checkpoint - Ensure model evaluation chart tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement batch generation orchestrator
  - [ ] 12.1 Create `src/presentation_charts/generator.py`
    - Implement `PresentationChartGenerator` class
    - Implement `generate_all_charts(config: PresentationConfig, model_data: Optional[Dict]) -> BatchGenerationResult`
    - Generate architecture diagrams (system overview, AWS architecture, data flow)
    - Generate model evaluation charts if model_data provided
    - Implement error isolation: catch exceptions per chart, continue generation
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 12.2 Implement input validation
    - Validate output_dir does not contain path traversal characters (../)
    - Validate y_true, y_pred, y_proba array lengths are consistent
    - Validate y_proba values are in range [0.0, 1.0]
    - Validate feature names are ≤100 characters
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [ ]* 12.3 Write property tests for batch generation
    - **Property 2: Model evaluation chart generation completeness**
    - **Validates: Requirements 1.2**
    - Test all 6 evaluation charts generated when model_data provided
    - **Property 3: Error isolation**
    - **Validates: Requirements 1.3, 12.3**
    - Test single chart failure doesn't stop other charts
    - **Property 4: Result completeness**
    - **Validates: Requirements 1.4**
    - Test successful and failed charts are properly recorded

- [ ] 13. Implement export functionality
  - [ ] 13.1 Create `src/presentation_charts/exporter.py`
    - Implement `export_chart(fig: Figure, chart_type: str, config: PresentationConfig) -> str`
    - Export PNG files with descriptive names (system_overview.png, aws_architecture.png, etc.)
    - Create output directory if it doesn't exist
    - Close Figure objects after export to free memory
    - Ensure PNG file size ≤500 KB
    - _Requirements: 11.1, 11.3, 11.4, 11.5, 14.3, 14.4_

  - [ ] 13.2 Implement Mermaid source export
    - Implement `export_mermaid_sources(result: BatchGenerationResult, config: PresentationConfig) -> str`
    - Collect all Mermaid sources from architecture diagrams
    - Export to single Markdown file (mermaid_diagrams.md)
    - Handle Mermaid export failures gracefully (log warning, don't fail PNG export)
    - _Requirements: 11.2, 12.4_

  - [ ]* 13.3 Write property tests for export functionality
    - **Property 5: Mermaid export consistency**
    - **Validates: Requirements 2.4, 3.4, 4.4, 11.2**
    - Test all architecture diagrams have Mermaid sources exported
    - **Property 8: File existence**
    - **Validates: Requirements 11.3, 11.4**
    - Test exported files exist with correct names
    - **Property 9: Output directory auto-creation**
    - **Validates: Requirements 11.5**
    - Test non-existent directories are created
    - **Property 26: Memory release**
    - **Validates: Requirements 14.3**
    - Test Figure objects are closed after export
    - **Property 27: File size limit**
    - **Validates: Requirements 14.4**
    - Test PNG files are ≤500 KB

- [ ] 14. Implement chart styling and format standardization
  - [ ] 14.1 Create `src/presentation_charts/styling.py`
    - Implement `apply_presentation_style(fig: Figure, config: PresentationConfig) -> None`
    - Set 16:9 aspect ratio for all charts
    - Set 300 DPI resolution
    - Apply consistent color scheme and font (Arial)
    - Set title font size to 18, label font size to 14
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ]* 14.2 Write property tests for styling
    - **Property 6: Chart format consistency**
    - **Validates: Requirements 10.1, 10.2, 10.4**
    - Test all charts have 16:9 ratio, 300 DPI, Arial font, correct font sizes
    - **Property 7: Visual style consistency**
    - **Validates: Requirements 10.3**
    - Test all charts use same color scheme

- [ ] 15. Implement error handling
  - [ ] 15.1 Create `src/presentation_charts/exceptions.py`
    - Define `PresentationChartError` base exception
    - Define `ValidationError` for input validation failures
    - Define `ExportError` for file export failures
    - _Requirements: 12.1, 12.2_

  - [ ] 15.2 Add error handling to generator
    - Raise IOError with clear message when output_dir is not writable
    - Raise ValidationError when model_data format is incorrect
    - Log failed charts to BatchGenerationResult.failed_charts
    - Log warnings for Mermaid export failures without affecting PNG generation
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

  - [ ]* 15.3 Write unit tests for error handling
    - Test IOError on unwritable directory
    - Test ValidationError on invalid model_data
    - Test partial failure handling
    - Test Mermaid failure isolation
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [ ] 16. Checkpoint - Ensure all core functionality tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Create demo scripts
  - [ ] 17.1 Create `examples/presentation_charts_basic_demo.py`
    - Demonstrate generating architecture diagrams only (no model data)
    - Show BatchGenerationResult output
    - _Requirements: 1.1, 2.1, 3.1, 4.1_

  - [ ] 17.2 Create `examples/presentation_charts_full_demo.py`
    - Demonstrate generating all 9 charts with model data
    - Show model comparison, PR/ROC curves, confusion matrix, threshold analysis, feature importance
    - Display generated file paths and Mermaid sources
    - _Requirements: 1.2, 5.1, 6.1, 7.1, 8.1, 9.1_

  - [ ] 17.3 Create `examples/presentation_charts_custom_demo.py`
    - Demonstrate generating individual charts
    - Show custom PresentationConfig usage
    - Demonstrate error handling scenarios
    - _Requirements: 10.1, 12.1, 13.1_

- [ ]* 18. Write integration tests
  - [ ]* 18.1 Create `tests/integration/test_presentation_charts_end_to_end.py`
    - Test complete batch generation workflow
    - Test generated files can be read by external tools
    - Test Mermaid sources can be rendered by Mermaid Live Editor
    - Test integration with existing model_evaluation_viz module
    - _Requirements: 1.1, 1.2, 1.4, 11.1, 11.2_

  - [ ]* 18.2 Write property test for input validation
    - **Property 22: Array length consistency validation**
    - **Validates: Requirements 13.2**
    - Test ValidationError on inconsistent array lengths
    - **Property 23: Probability value range validation**
    - **Validates: Requirements 13.3**
    - Test ValidationError on y_proba outside [0.0, 1.0]
    - **Property 24: Path traversal protection**
    - **Validates: Requirements 13.1**
    - Test validation error on ../ in output_dir
    - **Property 25: Feature name length limit**
    - **Validates: Requirements 13.4**
    - Test validation error on feature names >100 chars

  - [ ]* 18.3 Write property test for Mermaid export failure isolation
    - **Property 28: Mermaid export failure isolation**
    - **Validates: Requirements 12.4**
    - Test Mermaid failure logs warning but doesn't affect PNG generation

- [ ] 19. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation builds on the existing `model_evaluation_viz` module for model evaluation charts
- All charts use Python with matplotlib for rendering
- Mermaid sources are text-based and can be edited manually after generation
