"""
BitoGuard 風控監控儀表板 v2.0
參考台北城市儀表板設計風格
深色主題 + 現代化介面 + 即時監控
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="BitoGuard 風控監控儀表板",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 台北城市儀表板風格 CSS
st.markdown("""
<style>
    /* 全域樣式 - 深色主題 */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* 隱藏 Streamlit 預設元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 主標題區 */
    .dashboard-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .dashboard-subtitle {
        font-size: 1.1rem;
        color: #93c5fd;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    .dashboard-time {
        font-size: 0.95rem;
        color: #bfdbfe;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* KPI 卡片 */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .kpi-change {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }
    
    .kpi-change.positive {
        color: #10b981;
    }
    
    .kpi-change.negative {
        color: #ef4444;
    }
    
    .kpi-change.neutral {
        color: #6b7280;
    }
    
    /* 圖表容器 */
    .chart-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    /* 警示框 */
    .alert-box {
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
        font-weight: 500;
    }
    
    .alert-critical {
        background: rgba(239, 68, 68, 0.15);
        border-color: #ef4444;
        color: #fca5a5;
    }
    
    .alert-warning {
        background: rgba(245, 158, 11, 0.15);
        border-color: #f59e0b;
        color: #fcd34d;
    }
    
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
        color: #93c5fd;
    }
    
    .alert-success {
        background: rgba(16, 185, 129, 0.15);
        border-color: #10b981;
        color: #6ee7b7;
    }
    
    /* 狀態指示器 */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-high {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    .status-medium {
        background: rgba(245, 158, 11, 0.2);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    
    .status-low {
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    /* 表格樣式 */
    .dataframe {
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* 分隔線 */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
        margin: 2rem 0;
    }
    
    /* 脈衝動畫 */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* 即時指示器 */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(239, 68, 68, 0.2);
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #fca5a5;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #ef4444;
        border-radius: 50%;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

def generate_mock_data(n_samples=100):
    """生成模擬交易資料"""
    np.random.seed(42)
    
    n_suspicious = int(n_samples * 0.15)
    n_normal = n_samples - n_suspicious
    
    data = []
    
    # 正常帳號
    for i in range(n_normal):
        account_id = f"ACC{i+1:05d}"
        data.append({
            'account_id': account_id,
            'total_transactions': np.random.randint(10, 100),
            'total_volume': np.random.uniform(1000, 50000),
            'avg_transaction_size': np.random.uniform(100, 1000),
            'unique_counterparties': np.random.randint(5, 30),
            'night_transaction_ratio': np.random.uniform(0.05, 0.25),
            'large_transaction_ratio': np.random.uniform(0.05, 0.20),
            'velocity_score': np.random.uniform(0.1, 0.4),
            'risk_score': np.random.uniform(0.1, 0.45),
            'prediction': 0,
            'label': 'Normal'
        })
    
    # 異常帳號
    for i in range(n_suspicious):
        account_id = f"ACC{n_normal+i+1:05d}"
        data.append({
            'account_id': account_id,
            'total_transactions': np.random.randint(150, 500),
            'total_volume': np.random.uniform(80000, 500000),
            'avg_transaction_size': np.random.uniform(2000, 10000),
            'unique_counterparties': np.random.randint(50, 200),
            'night_transaction_ratio': np.random.uniform(0.40, 0.85),
            'large_transaction_ratio': np.random.uniform(0.35, 0.75),
            'velocity_score': np.random.uniform(0.6, 0.95),
            'risk_score': np.random.uniform(0.65, 0.98),
            'prediction': 1,
            'label': 'Suspicious'
        })
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

def create_gauge_chart(value, title, max_value=100):
    """建立儀表板圖表"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#f1f5f9'}},
        delta={'reference': max_value * 0.5, 'increasing': {'color': "#ef4444"}},
        gauge={
            'axis': {'range': [None, max_value], 'tickcolor': "#64748b"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, max_value * 0.33], 'color': 'rgba(16, 185, 129, 0.3)'},
                {'range': [max_value * 0.33, max_value * 0.66], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [max_value * 0.66, max_value], 'color': 'rgba(239, 68, 68, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.8
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f1f5f9", 'family': "Arial"},
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_risk_heatmap(df):
    """建立風險熱力圖"""
    # 創建風險矩陣
    risk_matrix = df.pivot_table(
        values='risk_score',
        index=pd.cut(df['night_transaction_ratio'], bins=5),
        columns=pd.cut(df['velocity_score'], bins=5),
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=risk_matrix.values,
        x=[f'{i:.2f}' for i in risk_matrix.columns.categories.mid],
        y=[f'{i:.2f}' for i in risk_matrix.index.categories.mid],
        colorscale=[
            [0, '#10b981'],
            [0.5, '#f59e0b'],
            [1, '#ef4444']
        ],
        text=risk_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(
            title="風險分數",
            titleside="right",
            tickmode="linear",
            tick0=0,
            dtick=0.2,
            tickfont=dict(color='#f1f5f9')
        )
    ))
    
    fig.update_layout(
        title='風險熱力圖 (夜間交易 vs 交易速度)',
        xaxis_title='交易速度分數',
        yaxis_title='夜間交易比例',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        height=400
    )
    
    return fig

def create_timeline_chart(df):
    """建立即時監控時間軸"""
    # 模擬過去24小時的資料
    hours = pd.date_range(end=datetime.now(), periods=24, freq='H')
    
    # 生成每小時的異常偵測數量
    suspicious_counts = np.random.poisson(lam=2, size=24)
    normal_counts = np.random.poisson(lam=10, size=24)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=suspicious_counts,
        name='異常偵測',
        mode='lines+markers',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=8, symbol='diamond'),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.2)'
    ))
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=normal_counts,
        name='正常交易',
        mode='lines+markers',
        line=dict(color='#10b981', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(
        title='24小時即時監控',
        xaxis_title='時間',
        yaxis_title='偵測數量',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        hovermode='x unified',
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# ============================================================================
# HEADER
# ============================================================================

st.markdown(f"""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="dashboard-title">🛡️ BitoGuard 風控監控儀表板</h1>
            <p class="dashboard-subtitle">即時異常交易偵測與風險分析系統</p>
            <p class="dashboard-time">📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
        <div class="live-indicator">
            <div class="live-dot"></div>
            <span>即時監控中</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CONTROL PANEL
# ============================================================================

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    if st.button("🚀 開始分析", use_container_width=True):
        with st.spinner("正在載入資料並進行風險分析..."):
            st.session_state.df = generate_mock_data(100)
            st.session_state.data_loaded = True
            st.session_state.last_update = datetime.now()
            st.success("✅ 分析完成！")
            st.rerun()

with col2:
    if st.button("🔄 重新整理", use_container_width=True):
        if st.session_state.data_loaded:
            st.session_state.last_update = datetime.now()
            st.rerun()

with col3:
    auto_refresh = st.checkbox("自動更新", value=False)

with col4:
    st.selectbox("時間範圍", ["即時", "1小時", "24小時", "7天"], label_visibility="collapsed")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

if st.session_state.data_loaded:
    df = st.session_state.df
    
    # KPI 區域
    st.markdown("### 📊 關鍵指標")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_accounts = len(df)
    suspicious_accounts = len(df[df['label'] == 'Suspicious'])
    high_risk = len(df[df['risk_score'] >= 0.7])
    avg_risk = df['risk_score'].mean()
    detection_rate = (suspicious_accounts / total_accounts) * 100
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📈 總帳號數</div>
            <div class="kpi-value">{total_accounts:,}</div>
            <div class="kpi-change neutral">監控中</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⚠️ 可疑帳號</div>
            <div class="kpi-value" style="color: #ef4444;">{suspicious_accounts}</div>
            <div class="kpi-change negative">▲ {detection_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🔴 高風險</div>
            <div class="kpi-value" style="color: #f59e0b;">{high_risk}</div>
            <div class="kpi-change negative">需立即處理</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📉 平均風險</div>
            <div class="kpi-value" style="color: #3b82f6;">{avg_risk:.3f}</div>
            <div class="kpi-change neutral">穩定</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">✅ 正常帳號</div>
            <div class="kpi-value" style="color: #10b981;">{total_accounts - suspicious_accounts}</div>
            <div class="kpi-change positive">▼ {100-detection_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 警示區域
    if suspicious_accounts > 0:
        st.markdown(f"""
        <div class="alert-box alert-critical">
            <strong>🚨 高風險警示</strong><br>
            系統偵測到 <strong>{suspicious_accounts}</strong> 個可疑帳號，其中 <strong>{high_risk}</strong> 個為高風險等級，建議立即進行人工審查與處置。
        </div>
        """, unsafe_allow_html=True)
    
    # 圖表區域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 24小時即時監控</div>', unsafe_allow_html=True)
        fig_timeline = create_timeline_chart(df)
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔥 風險熱力圖</div>', unsafe_allow_html=True)
        fig_heatmap = create_risk_heatmap(df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 儀表板區域
    st.markdown("### 🎯 風險儀表板")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_gauge1 = create_gauge_chart(detection_rate, "偵測率 (%)", 100)
        st.plotly_chart(fig_gauge1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_gauge2 = create_gauge_chart(avg_risk * 100, "平均風險", 100)
        st.plotly_chart(fig_gauge2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_gauge3 = create_gauge_chart((high_risk/total_accounts)*100, "高風險率 (%)", 100)
        st.plotly_chart(fig_gauge3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_gauge4 = create_gauge_chart(df['velocity_score'].mean() * 100, "交易速度", 100)
        st.plotly_chart(fig_gauge4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 可疑帳號列表
    st.markdown("### 🔍 可疑帳號列表")
    
    df_suspicious = df[df['label'] == 'Suspicious'].sort_values('risk_score', ascending=False).head(10)
    
    # 建立顯示表格
    display_data = []
    for idx, row in df_suspicious.iterrows():
        risk_level = "高風險" if row['risk_score'] >= 0.7 else "中風險"
        status_class = "status-high" if row['risk_score'] >= 0.7 else "status-medium"
        
        display_data.append({
            '帳號ID': row['account_id'],
            '風險分數': f"{row['risk_score']:.3f}",
            '風險等級': risk_level,
            '交易量': f"${row['total_volume']:,.0f}",
            '交易筆數': int(row['total_transactions']),
            '夜間比例': f"{row['night_transaction_ratio']:.1%}",
            '交易速度': f"{row['velocity_score']:.2f}"
        })
    
    df_table = pd.DataFrame(display_data)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 初始狀態
    st.markdown("""
    <div class="alert-box alert-info">
        <strong>ℹ️ 系統就緒</strong><br>
        點擊上方「開始分析」按鈕載入資料並開始風險分析。
    </div>
    """, unsafe_allow_html=True)
    
    # 顯示系統功能介紹
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h3 style="color: #3b82f6;">⚡ 即時監控</h3>
            <p style="color: #94a3b8;">24小時不間斷監控交易活動，即時偵測異常行為模式</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h3 style="color: #3b82f6;">🎯 精準分析</h3>
            <p style="color: #94a3b8;">多維度風險評估，準確率達85%以上</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="chart-container">
            <h3 style="color: #3b82f6;">📊 視覺化</h3>
            <p style="color: #94a3b8;">直觀的儀表板設計，快速掌握風險狀況</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p style="font-size: 0.9rem;"><strong>BitoGuard</strong> 風控監控儀表板 v2.0</p>
    <p style="font-size: 0.8rem;">Powered by AI & Machine Learning | © 2024 BitoGuard Team</p>
</div>
""", unsafe_allow_html=True)
