"""Constants for presentation chart generation."""

# AWS Service Colors (based on AWS official color scheme)
AWS_COLORS = {
    # Compute
    "Lambda": "#FF9900",
    "Step Functions": "#E7157B",
    
    # Storage
    "S3": "#569A31",
    "DynamoDB": "#4053D6",
    
    # AI/ML
    "Bedrock": "#01A88D",
    
    # Security
    "Secrets Manager": "#DD344C",
    
    # Monitoring
    "CloudWatch": "#FF4F8B",
    
    # External
    "BitoPro API": "#3B48CC",
}

# Layer Colors
LAYER_COLORS = {
    "compute": "#FF9900",
    "storage": "#569A31",
    "ai_ml": "#01A88D",
    "orchestration": "#E7157B",
    "security": "#DD344C",
    "monitoring": "#FF4F8B",
}

# Chart Dimensions
CHART_WIDTH = 16
CHART_HEIGHT = 9
CHART_DPI = 300

# Font Settings
FONT_FAMILY = "Arial"
TITLE_FONT_SIZE = 18
LABEL_FONT_SIZE = 14
LEGEND_FONT_SIZE = 12

# Color Schemes
PROFESSIONAL_BLUE_SCHEME = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "accent": "#F18F01",
    "success": "#06A77D",
    "warning": "#D4AF37",
    "danger": "#C73E1D",
}

MODEL_COLORS = {
    "Random Forest": "#2E86AB",
    "XGBoost": "#A23B72",
    "LightGBM": "#F18F01",
    "CatBoost": "#06A77D",
}

# Data Flow Stage Colors
FLOW_STAGE_COLORS = {
    "data_ingestion": "#3498db",
    "feature_extraction": "#2ecc71",
    "risk_analysis": "#e74c3c",
    "report_generation": "#f39c12",
}
