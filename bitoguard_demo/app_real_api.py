"""
BitoGuard 風控儀表板 - 真實 API 整合版
參考台北城市儀表板設計 - 緊湊卡片式佈局
整合真實 BitoPro API 資料
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path
import requests
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="BitoGuard 風控儀表板",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 台北城市儀表板風格 CSS - 緊湊卡片設計
st.markdown("""
<style>
    /* 全域深色主題 */
    .stApp {
        background: #0f1419;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 頂部標題列 - 緊湊設計 */
    .top-bar {
        background: linear-gradient(90deg, #1a1f2e 0%, #2d3748 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .title {
        font-size: 1.5rem;
        font-weight: 700;
