# Implementation Plan: Hyperparameter Search Optimization

## Overview

實作一個專為防詐/可疑帳號偵測設計的超參數搜尋優化模組。系統支援 5 種主流機器學習演算法，使用分層交叉驗證確保評估可靠性，自動掃描決策閾值，並產生完整的比較分析報告。實作將採用 Python，使用 scikit-learn、XGBoost 和 LightGBM 等主流機器學習框架。

## Tasks

- [ ] 1. 建立核心資料結構與類型定義
  - 建立 `src/ml/hyperparameter_search/types.py` 檔案
  - 實作 `ModelType` 枚舉類別（5 種演算法）
  - 實作 `SearchConfig`、`EvaluationMetrics`、`SearchResult`、`ComparisonReport` 資料類別
  - 確保所有類型定義與 design.md 中的介面一致
  - _Requirements: 1.1-1.7, 11.1_

- [ ]* 1.1 為核心資料結構撰寫屬性測試
  - **Property 3: 評估指標在有效範圍內**
  - **Validates: Requirements 4.6, 5.5**

- [ ] 2. 實作模型工廠 (ModelFactory)
  - 建立 `src/ml/hyperparameter_search/model_factory.py` 檔案
  - [ ] 2.1 實作 `create_model` 方法支援 5 種演算法
    - 支援 Logistic Regression 模型建立
    - 支援 Decision Tree 模型建立
    - 支援 Random Forest 模型建立
    - 支援 XGBoost 模型建立
    - 支援 LightGBM 模型建立
    - 接受超參數作為輸入並正確傳遞給模型
    - _Requirements: 1.1-1.7_
  
  - [ ] 2.2 實作 `get_param_grid` 方法
    - 為每種演算法定義預設的超參數搜尋空間
    - 確保參數範圍適合防詐偵測任務
    - _Requirements: 7.1_

- [ ]* 2.3 為模型工廠撰寫單元測試
  - 測試所有 5 種演算法的模型建立
  - 測試超參數正確傳遞
  - 測試預設參數網格的有效性
  - _Requirements: 1.1-1.7_

- [ ] 3. 實作評估指標計算模組
  - 建立 `src/ml/hyperparameter_search/evaluator.py` 檔案
  - [ ] 3.1 實作 `evaluate_at_threshold` 方法
    - 計算 PR-AUC 分數
    - 計算 Precision 分數
    - 計算 Recall 分數
    - 計算 F1 分數
    - 計算混淆矩陣
    - 確保所有指標值在 [0, 1] 範圍內
    - _Requirements: 4.1-4.6_
  
  - [ ] 3.2 實作 `compute_imbalance_ratio` 方法
    - 計算不平衡比例（負樣本數 / 正樣本數）
    - _Requirements: 6.4_

- [ ]* 3.3 為評估模組撰寫屬性測試
  - **Property 3: 評估指標在有效範圍內**
  - **Validates: Requirements 4.6, 5.5**

- [ ]* 3.4 為評估模組撰寫單元測試
  - 測試各種指標計算的正確性
  - 測試邊界情況（全部正確、全部錯誤）
  - _Requirements: 4.1-4.6_

- [ ] 4. 實作閾值優化器 (ThresholdOptimizer)
  - 建立 `src/ml/hyperparameter_search/threshold_optimizer.py` 檔案
  - [ ] 4.1 實作標準閾值掃描
    - 掃描範圍 0.10 到 0.45，步長 0.05
    - 在每個閾值評估所有指標
    - 記錄最佳閾值與對應指標
    - 支援可配置的閾值範圍
    - 確保閾值在 [0, 1] 範圍內
    - _Requirements: 5.1-5.5_
  
  - [ ] 4.2 實作極度不平衡資料處理
    - 偵測不平衡比例是否超過 100
    - 當超過 100 時，擴展掃描範圍至 0.05-0.10
    - 合併標準範圍與擴展範圍的結果
    - _Requirements: 6.1-6.4_

- [ ]* 4.3 為閾值優化器撰寫屬性測試
  - **Property 6: 閾值掃描完整性**
  - **Validates: Requirements 5.2**
  - **Property 14: 極度不平衡擴展範圍**
  - **Validates: Requirements 6.3**

- [ ]* 4.4 為閾值優化器撰寫單元測試
  - 測試標準範圍掃描
  - 測試極度不平衡情況的擴展範圍
  - 測試最佳閾值選擇邏輯
  - _Requirements: 5.1-5.5, 6.1-6.4_

- [ ] 5. Checkpoint - 確保基礎元件測試通過
  - 確保所有測試通過，如有問題請詢問使用者

- [ ] 6. 實作超參數搜尋引擎 (HyperparameterSearchEngine)
  - 建立 `src/ml/hyperparameter_search/search_engine.py` 檔案
  - [ ] 6.1 實作初始化與配置
    - 初始化 StratifiedKFold 交叉驗證器
    - 設定可配置的 fold 數量（預設 5）
    - 設定隨機種子以確保可重現性
    - 設定平行處理參數 (n_jobs)
    - _Requirements: 3.2, 11.1-11.2, 12.1-12.3_
  
  - [ ] 6.2 實作資料分層切分
    - 使用 stratified split 方法切分資料
    - 確保訓練集與驗證集的類別比例一致（誤差 < 1%）
    - 使用可配置的隨機種子
    - _Requirements: 2.1-2.4_
  
  - [ ] 6.3 實作分層交叉驗證
    - 使用 stratified k-fold 交叉驗證
    - 確保每個 fold 保持類別比例
    - 記錄每個 fold 的分數
    - 計算分數的平均值與標準差
    - _Requirements: 3.1-3.5_
  
  - [ ] 6.4 實作超參數網格搜尋
    - 接受參數網格作為輸入
    - 評估網格中的所有參數組合
    - 記錄每個組合的結果
    - 根據驗證指標識別最佳參數組合
    - 確保最佳參數來自提供的搜尋空間
    - _Requirements: 7.1-7.5_
  
  - [ ] 6.5 實作訓練時間記錄
    - 記錄訓練開始時間
    - 記錄訓練結束時間
    - 計算總訓練時間（秒）
    - _Requirements: 10.1-10.3_
  
  - [ ] 6.6 整合閾值優化器
    - 在每個參數組合訓練完成後呼叫閾值優化器
    - 傳遞不平衡比例以啟用擴展範圍（如需要）
    - 記錄最佳閾值與對應指標
    - _Requirements: 5.1-5.5, 6.1-6.4_

- [ ]* 6.7 為搜尋引擎撰寫屬性測試
  - **Property 1: Stratified Split 保持類別比例**
  - **Validates: Requirements 2.2, 2.3**
  - **Property 2: K-Fold 保持類別比例**
  - **Validates: Requirements 3.3**
  - **Property 4: 最佳參數來自搜尋空間**
  - **Validates: Requirements 7.5**
  - **Property 5: Cross-validation 分數數量正確**
  - **Validates: Requirements 3.4**
  - **Property 7: 超參數組合完整性**
  - **Validates: Requirements 7.2, 7.3**
  - **Property 8: 最佳結果選擇正確性**
  - **Validates: Requirements 7.4**
  - **Property 11: 可重現性**
  - **Validates: Requirements 11.3**
  - **Property 12: 訓練時間計算正確性**
  - **Validates: Requirements 10.3**
  - **Property 13: 平行執行結果一致性**
  - **Validates: Requirements 12.5**

- [ ]* 6.8 為搜尋引擎撰寫單元測試
  - 測試資料分層切分
  - 測試交叉驗證執行
  - 測試超參數網格搜尋
  - 測試訓練時間記錄
  - 測試平行處理功能
  - _Requirements: 2.1-2.4, 3.1-3.5, 7.1-7.5, 10.1-10.5, 12.1-12.5_

- [ ] 7. 實作報告產生器 (ReportGenerator)
  - 建立 `src/ml/hyperparameter_search/report_generator.py` 檔案
  - [ ] 7.1 實作比較表產生
    - 產生 Markdown 格式的比較表
    - 包含模型類型、最佳參數、最佳閾值、所有評估指標、訓練時間
    - 按 PR-AUC 分數排序模型
    - 標示最佳表現的模型
    - 確保表格易於閱讀
    - _Requirements: 8.1-8.5, 10.4_
  
  - [ ] 7.2 實作風險分析產生
    - 基於交叉驗證分數分析模型穩定性
    - 識別交叉驗證中高變異的模型
    - 基於指標權衡提供建議
    - 警告潛在的過擬合風險
    - 確保風險分析以清晰文字呈現
    - _Requirements: 9.1-9.5_
  
  - [ ] 7.3 實作完整報告產生
    - 整合比較表與風險分析
    - 識別最佳模型、參數、閾值
    - 返回 ComparisonReport 物件
    - _Requirements: 8.1-8.5, 9.1-9.5_

- [ ]* 7.4 為報告產生器撰寫屬性測試
  - **Property 9: 報告包含必要資訊**
  - **Validates: Requirements 8.2, 10.4**
  - **Property 10: 模型排序正確性**
  - **Validates: Requirements 8.3**

- [ ]* 7.5 為報告產生器撰寫單元測試
  - 測試比較表格式正確性
  - 測試模型排序邏輯
  - 測試風險分析內容
  - 測試報告完整性
  - _Requirements: 8.1-8.5, 9.1-9.5_

- [ ] 8. 建立高階 API 與整合
  - 建立 `src/ml/hyperparameter_search/__init__.py` 檔案
  - [ ] 8.1 實作 `compare_all_models` 函數
    - 對所有 5 種演算法執行超參數搜尋
    - 使用預設的參數網格
    - 返回所有模型的搜尋結果列表
    - _Requirements: 1.1-1.7, 7.1-7.5_
  
  - [ ] 8.2 匯出公開 API
    - 匯出 `HyperparameterSearchEngine`
    - 匯出 `ModelFactory`
    - 匯出 `ReportGenerator`
    - 匯出所有資料類型
    - 匯出 `compare_all_models` 函數

- [ ]* 8.3 為高階 API 撰寫整合測試
  - 測試完整的端到端工作流程
  - 測試 `compare_all_models` 函數
  - 使用模擬資料驗證所有元件整合
  - _Requirements: 1.1-1.7, 7.1-7.5, 8.1-8.5_

- [ ] 9. Checkpoint - 確保所有測試通過
  - 確保所有測試通過，如有問題請詢問使用者

- [ ] 10. 建立使用範例與文件
  - 建立 `examples/hyperparameter_search_example.py` 檔案
  - [ ] 10.1 撰寫基本使用範例
    - 展示單一模型的超參數搜尋
    - 展示結果解讀
    - _Requirements: 1.1-1.7, 7.1-7.5_
  
  - [ ] 10.2 撰寫進階使用範例
    - 展示比較所有模型
    - 展示報告產生
    - 展示極度不平衡資料處理
    - _Requirements: 6.1-6.4, 8.1-8.5, 9.1-9.5_

- [ ] 11. 最終整合與驗證
  - 執行所有測試確保通過
  - 驗證所有需求都已實作
  - 確認程式碼符合 Python 最佳實踐
  - 確認所有公開 API 都有適當的文件字串

## Notes

- 標記 `*` 的任務為可選任務，可跳過以加速 MVP 開發
- 每個任務都參照特定需求以確保可追溯性
- Checkpoint 確保增量驗證
- 屬性測試驗證通用正確性屬性
- 單元測試驗證特定範例與邊界情況
- 實作使用 Python 與主流機器學習框架（scikit-learn、XGBoost、LightGBM）
