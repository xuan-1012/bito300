"""System overview diagram generator."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from ..models import PresentationConfig
from ..constants import AWS_COLORS, LAYER_COLORS


def generate_system_overview(config: PresentationConfig) -> Figure:
    """
    Generate system overview architecture diagram.
    
    Args:
        config: Presentation configuration
        
    Returns:
        Figure object containing the system overview diagram
    """
    fig, ax = plt.subplots(figsize=(config.aspect_ratio[0], config.aspect_ratio[1]), 
                           dpi=config.dpi)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Define component positions and layers
    components = {
        # External
        "BitoPro API": {"pos": (0.1, 0.85), "layer": "external", "color": AWS_COLORS["BitoPro API"]},
        
        # Orchestration Layer
        "Step Functions": {"pos": (0.5, 0.9), "layer": "orchestration", "color": AWS_COLORS["Step Functions"]},
        
        # Compute Layer
        "Lambda:\nDataFetcher": {"pos": (0.2, 0.7), "layer": "compute", "color": AWS_COLORS["Lambda"]},
        "Lambda:\nFeatureExtractor": {"pos": (0.35, 0.55), "layer": "compute", "color": AWS_COLORS["Lambda"]},
        "Lambda:\nRiskAnalyzer": {"pos": (0.5, 0.4), "layer": "compute", "color": AWS_COLORS["Lambda"]},
        "Lambda:\nReportGenerator": {"pos": (0.65, 0.25), "layer": "compute", "color": AWS_COLORS["Lambda"]},
        
        # Storage Layer
        "S3 Bucket": {"pos": (0.75, 0.55), "layer": "storage", "color": AWS_COLORS["S3"]},
        "DynamoDB": {"pos": (0.85, 0.4), "layer": "storage", "color": AWS_COLORS["DynamoDB"]},
        
        # AI/ML Layer
        "Bedrock": {"pos": (0.6, 0.1), "layer": "ai_ml", "color": AWS_COLORS["Bedrock"]},
    }
    
    # Draw components
    for name, info in components.items():
        x, y = info["pos"]
        rect = mpatches.FancyBboxPatch(
            (x - 0.06, y - 0.04), 0.12, 0.08,
            boxstyle="round,pad=0.01",
            facecolor=info["color"],
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8
        )
        ax.add_patch(rect)
        ax.text(x, y, name, ha='center', va='center', 
               fontsize=config.label_font_size - 2, fontweight='bold',
               color='white', family=config.font_family)
    
    # Draw connections (arrows)
    connections = [
        ("BitoPro API", "Lambda:\nDataFetcher"),
        ("Lambda:\nDataFetcher", "S3 Bucket"),
        ("S3 Bucket", "Lambda:\nFeatureExtractor"),
        ("Lambda:\nFeatureExtractor", "S3 Bucket"),
        ("S3 Bucket", "Lambda:\nRiskAnalyzer"),
        ("Lambda:\nRiskAnalyzer", "Bedrock"),
        ("Lambda:\nRiskAnalyzer", "S3 Bucket"),
        ("Lambda:\nRiskAnalyzer", "DynamoDB"),
        ("S3 Bucket", "Lambda:\nReportGenerator"),
        ("DynamoDB", "Lambda:\nReportGenerator"),
    ]
    
    for source, target in connections:
        x1, y1 = components[source]["pos"]
        x2, y2 = components[target]["pos"]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', lw=2, color='#555555', alpha=0.7))
    
    # Add title
    ax.text(0.5, 0.98, '系統概覽架構圖 - 加密貨幣可疑帳號偵測系統',
           ha='center', va='top', fontsize=config.title_font_size,
           fontweight='bold', family=config.font_family)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=LAYER_COLORS["compute"], label='計算層'),
        mpatches.Patch(facecolor=LAYER_COLORS["storage"], label='儲存層'),
        mpatches.Patch(facecolor=LAYER_COLORS["ai_ml"], label='AI/ML層'),
        mpatches.Patch(facecolor=LAYER_COLORS["orchestration"], label='編排層'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=config.label_font_size - 2)
    
    plt.tight_layout()
    return fig


def get_mermaid_source() -> str:
    """Get Mermaid source code for system overview diagram."""
    return """```mermaid
graph TB
    subgraph "External"
        BitoPro[BitoPro API<br/>交易資料來源]
    end
    
    subgraph "AWS Cloud"
        subgraph "計算層"
            Lambda1[Lambda: DataFetcher]
            Lambda2[Lambda: FeatureExtractor]
            Lambda3[Lambda: RiskAnalyzer]
            Lambda4[Lambda: ReportGenerator]
        end
        
        subgraph "儲存層"
            S3[S3 Bucket<br/>Private + Encrypted]
            DDB[DynamoDB<br/>Risk Profiles]
        end
        
        subgraph "AI/ML層"
            Bedrock[Amazon Bedrock<br/>Claude 3 Sonnet]
        end
        
        subgraph "編排層"
            StepFn[Step Functions<br/>Workflow]
        end
    end
    
    BitoPro -->|HTTPS| Lambda1
    Lambda1 -->|Store| S3
    S3 -->|Read| Lambda2
    Lambda2 -->|Store| S3
    S3 -->|Read| Lambda3
    Lambda3 -->|Invoke| Bedrock
    Lambda3 -->|Store| S3
    Lambda3 -->|Write| DDB
    S3 -->|Read| Lambda4
    DDB -->|Query| Lambda4
    Lambda4 -->|Store| S3
    
    StepFn -.->|Orchestrate| Lambda1
    StepFn -.->|Orchestrate| Lambda2
    StepFn -.->|Orchestrate| Lambda3
    StepFn -.->|Orchestrate| Lambda4
    
    style S3 fill:#ff9999
    style Bedrock fill:#99ccff
    style StepFn fill:#ffcc99
```"""
