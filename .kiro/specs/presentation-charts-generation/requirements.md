# 需求文件：簡報圖表生成系統

## 簡介

本系統為 3/26 加密貨幣可疑帳號偵測比賽提供專業的簡報圖表生成功能。系統基於現有的 `model_evaluation_viz` 模組，擴展支援 AWS 架構圖、系統流程圖、模型比較圖表等 9 種簡報用圖表。所有圖表採用統一的 AWS/FinTech 風格，適合 16:9 簡報格式，支援 Mermaid 與 PNG 雙格式輸出。

## 術語表

- **PresentationChartGenerator**: 簡報圖表生成器，負責批次生成所有簡報圖表
- **PresentationConfig**: 簡報配置物件，定義圖表樣式、尺寸、輸出格式等參數
- **BatchGenerationResult**: 批次生成結果物件，包含成功與失敗的圖表清單
- **ChartMetadata**: 圖表元資料，記錄圖表類型、檔案路徑、Mermaid 原始碼等資訊
- **ImageExporter**: 圖片匯出器，負責將圖表匯出為 PNG 檔案
- **MermaidSource**: Mermaid 原始碼，用於生成可編輯的架構圖

## 需求

### 需求 1: 批次圖表生成

**使用者故事：** 作為簡報製作者，我想要一次生成所有需要的圖表，以便快速完成簡報準備工作。

#### 驗收標準

1. WHEN 使用者呼叫 generate_all_charts() 且未提供模型資料 THEN THE PresentationChartGenerator SHALL 生成系統概覽圖、AWS 架構圖、資料流程圖三張架構圖表
2. WHEN 使用者呼叫 generate_all_charts() 且提供有效模型資料 THEN THE PresentationChartGenerator SHALL 額外生成模型比較圖、PR 曲線、ROC 曲線、混淆矩陣、閾值分析圖、特徵重要性圖六張評估圖表
3. WHEN 批次生成過程中某張圖表生成失敗 THEN THE PresentationChartGenerator SHALL 記錄失敗原因並繼續生成其他圖表
4. WHEN 批次生成完成 THEN THE BatchGenerationResult SHALL 包含所有成功生成的圖表元資料與失敗圖表的錯誤訊息
5. THE PresentationChartGenerator SHALL 在 30 秒內完成所有 9 張圖表的批次生成

### 需求 2: 系統概覽圖生成

**使用者故事：** 作為簡報製作者，我想要生成系統概覽架構圖，以便向觀眾展示整體系統架構。

#### 驗收標準

1. THE PresentationChartGenerator SHALL 生成包含 BitoPro API、Lambda Functions、S3、DynamoDB、Bedrock、Step Functions 等元件的系統概覽圖
2. WHEN 生成系統概覽圖 THEN THE PresentationChartGenerator SHALL 使用 Mermaid graph TB 格式標示元件間的資料流向
3. THE PresentationChartGenerator SHALL 在系統概覽圖中使用不同顏色區分計算層、儲存層、AI/ML 層、編排層
4. WHEN 配置啟用 Mermaid 匯出 THEN THE PresentationChartGenerator SHALL 保存系統概覽圖的 Mermaid 原始碼

### 需求 3: AWS 架構圖生成

**使用者故事：** 作為簡報製作者，我想要生成詳細的 AWS 架構圖，以便展示所有 AWS 服務的整合方式。

#### 驗收標準

1. THE PresentationChartGenerator SHALL 生成包含所有 AWS 服務的詳細架構圖：Lambda、S3、DynamoDB、Step Functions、Bedrock、Secrets Manager、CloudWatch
2. WHEN 生成 AWS 架構圖 THEN THE PresentationChartGenerator SHALL 標示每個服務之間的資料流向與呼叫關係
3. THE PresentationChartGenerator SHALL 在 AWS 架構圖中使用 AWS 官方色彩配置標示不同服務類型
4. WHEN 配置啟用 Mermaid 匯出 THEN THE PresentationChartGenerator SHALL 保存 AWS 架構圖的 Mermaid 原始碼

### 需求 4: 資料流程圖生成

**使用者故事：** 作為簡報製作者，我想要生成資料流程圖，以便展示資料在系統中的處理流程。

#### 驗收標準

1. THE PresentationChartGenerator SHALL 生成包含資料擷取、特徵提取、風險分析、報告生成四個階段的資料流程圖
2. WHEN 生成資料流程圖 THEN THE PresentationChartGenerator SHALL 標示每個階段的輸入與輸出資料格式（JSON、CSV、PNG/PDF）
3. THE PresentationChartGenerator SHALL 使用箭頭標示資料在各階段間的流向
4. WHEN 配置啟用 Mermaid 匯出 THEN THE PresentationChartGenerator SHALL 保存資料流程圖的 Mermaid 原始碼

### 需求 5: 模型比較圖生成

**使用者故事：** 作為資料科學家，我想要生成模型比較圖，以便展示不同模型的效能差異。

#### 驗收標準

1. WHEN 提供包含多個模型效能指標的資料 THEN THE PresentationChartGenerator SHALL 生成模型比較長條圖
2. THE PresentationChartGenerator SHALL 在模型比較圖中顯示 Accuracy、Precision、Recall、F1 Score、AUC 五項指標
3. THE PresentationChartGenerator SHALL 使用不同顏色區分不同模型的長條
4. WHEN 模型資料中包含 Random Forest 與 XGBoost THEN THE PresentationChartGenerator SHALL 在圖表中並排顯示兩者的效能指標

### 需求 6: 模型評估曲線生成

**使用者故事：** 作為資料科學家，我想要生成 PR 曲線與 ROC 曲線，以便評估模型的分類效能。

#### 驗收標準

1. WHEN 提供 y_true 與 y_proba 資料 THEN THE PresentationChartGenerator SHALL 生成 PR 曲線圖
2. WHEN 提供 y_true 與 y_proba 資料 THEN THE PresentationChartGenerator SHALL 生成 ROC 曲線圖
3. THE PresentationChartGenerator SHALL 在 PR 曲線圖中標示 AUC-PR 數值
4. THE PresentationChartGenerator SHALL 在 ROC 曲線圖中標示 AUC-ROC 數值與對角線基準線

### 需求 7: 混淆矩陣生成

**使用者故事：** 作為資料科學家，我想要生成混淆矩陣，以便分析模型的分類錯誤模式。

#### 驗收標準

1. WHEN 提供 y_true 與 y_pred 資料 THEN THE PresentationChartGenerator SHALL 生成混淆矩陣熱力圖
2. THE PresentationChartGenerator SHALL 在混淆矩陣中顯示 True Positive、True Negative、False Positive、False Negative 四個數值
3. THE PresentationChartGenerator SHALL 使用色彩深淺表示混淆矩陣中各格的數值大小
4. THE PresentationChartGenerator SHALL 在混淆矩陣中標示 Normal 與 Suspicious 兩個類別標籤

### 需求 8: 閾值分析圖生成

**使用者故事：** 作為資料科學家，我想要生成閾值分析圖，以便選擇最佳的分類閾值。

#### 驗收標準

1. WHEN 提供 y_true 與 y_proba 資料 THEN THE PresentationChartGenerator SHALL 生成閾值分析圖
2. THE PresentationChartGenerator SHALL 在閾值分析圖中顯示不同閾值下的 Precision、Recall、F1 Score 曲線
3. THE PresentationChartGenerator SHALL 在閾值分析圖中標示最佳 F1 Score 對應的閾值點
4. THE PresentationChartGenerator SHALL 使用 X 軸表示閾值範圍（0.0 到 1.0），Y 軸表示指標數值

### 需求 9: 特徵重要性圖生成

**使用者故事：** 作為資料科學家，我想要生成特徵重要性圖，以便了解哪些特徵對模型預測最重要。

#### 驗收標準

1. WHEN 提供特徵名稱與重要性數值 THEN THE PresentationChartGenerator SHALL 生成特徵重要性橫條圖
2. THE PresentationChartGenerator SHALL 按重要性數值由高到低排序特徵
3. THE PresentationChartGenerator SHALL 在特徵重要性圖中顯示每個特徵的重要性百分比
4. WHEN 特徵數量超過 20 個 THEN THE PresentationChartGenerator SHALL 僅顯示前 20 個最重要的特徵

### 需求 10: 圖表格式標準化

**使用者故事：** 作為簡報製作者，我想要所有圖表使用統一的格式與風格，以便保持簡報的視覺一致性。

#### 驗收標準

1. THE PresentationChartGenerator SHALL 生成所有圖表為 16:9 寬高比
2. THE PresentationChartGenerator SHALL 以 300 DPI 解析度匯出所有圖表
3. THE PresentationChartGenerator SHALL 對所有圖表使用相同的色彩配置與字型
4. THE PresentationChartGenerator SHALL 在所有圖表中使用 Arial 字型，標題字型大小為 18，標籤字型大小為 14

### 需求 11: 檔案匯出管理

**使用者故事：** 作為簡報製作者，我想要將圖表匯出為 PNG 檔案與 Mermaid 原始碼，以便在不同工具中使用。

#### 驗收標準

1. WHEN 配置啟用 PNG 匯出 THEN THE PresentationChartGenerator SHALL 將所有圖表匯出為 PNG 檔案
2. WHEN 配置啟用 Mermaid 匯出 THEN THE PresentationChartGenerator SHALL 將架構圖的 Mermaid 原始碼匯出為單一 Markdown 檔案
3. THE PresentationChartGenerator SHALL 將所有匯出檔案儲存至配置指定的輸出目錄
4. THE PresentationChartGenerator SHALL 為每個匯出檔案使用描述性的檔案名稱（如 system_overview.png、aws_architecture.png）
5. WHEN 輸出目錄不存在 THEN THE PresentationChartGenerator SHALL 自動建立該目錄

### 需求 12: 錯誤處理與復原

**使用者故事：** 作為系統使用者，我想要系統能妥善處理錯誤情況，以便在部分圖表生成失敗時仍能取得其他圖表。

#### 驗收標準

1. WHEN 輸出目錄無法寫入 THEN THE PresentationChartGenerator SHALL 拋出 IOError 並提供明確的錯誤訊息
2. WHEN 模型資料格式不正確 THEN THE PresentationChartGenerator SHALL 拋出 ValidationError 並記錄缺少的欄位
3. WHEN 單一圖表生成失敗 THEN THE PresentationChartGenerator SHALL 記錄失敗原因至 BatchGenerationResult.failed_charts 並繼續生成其他圖表
4. WHEN Mermaid 匯出失敗 THEN THE PresentationChartGenerator SHALL 記錄警告訊息但不影響 PNG 圖表生成

### 需求 13: 輸入驗證

**使用者故事：** 作為系統開發者，我想要系統驗證所有輸入參數，以便防止安全漏洞與資料錯誤。

#### 驗收標準

1. WHEN 提供 PresentationConfig THEN THE PresentationChartGenerator SHALL 驗證 output_dir 不包含路徑遍歷字元（如 ../）
2. WHEN 提供模型資料 THEN THE PresentationChartGenerator SHALL 驗證 y_true、y_pred、y_proba 陣列長度一致
3. WHEN 提供模型資料 THEN THE PresentationChartGenerator SHALL 驗證 y_proba 數值範圍在 0.0 到 1.0 之間
4. WHEN 提供特徵名稱 THEN THE PresentationChartGenerator SHALL 限制每個特徵名稱長度不超過 100 個字元

### 需求 14: 效能要求

**使用者故事：** 作為系統使用者，我想要系統能快速生成圖表，以便提高工作效率。

#### 驗收標準

1. THE PresentationChartGenerator SHALL 在 2 秒內完成單張架構圖表的生成
2. THE PresentationChartGenerator SHALL 在 5 秒內完成單張模型評估圖表的生成
3. THE PresentationChartGenerator SHALL 在生成每張圖表後立即釋放 Figure 物件以節省記憶體
4. THE PresentationChartGenerator SHALL 確保每張 PNG 圖表檔案大小不超過 500 KB
