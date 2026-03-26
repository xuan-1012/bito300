"""
BitoGuard 風控預測結果展示
使用 XGBoost 模型預測結果
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="BitoGuard 風控預測結果",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 更精美的 CSS 樣式
st.markdown("""
<style>
    /* 全域背景 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 主容器 - 不滿版，居中顯示 */
    .main > div {
        max-width: 1400px;
        padding: 2rem;
    }
    
    /* 標題區域 */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    /* KPI 卡片 - 更精美 */
    .kpi-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 2px solid transparent;
    }
    
    .kpi-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 3rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .kpi-change {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* 圖表容器 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .chart-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #f1f5f9;
    }
    
    /* 搜尋區域 */
    .search-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .search-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.5rem;
    }
    
    /* 結果卡片 */
    .result-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(100, 116, 139, 0.1);
    }
    
    .user-id-display {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
    }
    
    .status-badge {
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .status-normal {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-suspicious {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .result-details {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .detail-label {
        color: #64748b;
        font-weight: 600;
    }
    
    .detail-value {
        color: #1e293b;
        font-weight: 700;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* 輸入框樣式 */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 表格樣式 */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* 警告和成功訊息 */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 載入資料
@st.cache_data
def load_predictions():
    """載入 XGBoost 預測結果"""
    # 使用正確的 XGBoost CSV 檔案
    csv_path = Path(__file__).parent.parent / 'your_team_name_xgboost.csv'
    df = pd.read_csv(csv_path)
    return df

# 主程式
def main():
    # 精美標題
    st.markdown("""
    <div class="header-container">
        <div class="main-title">🛡️ BitoGuard</div>
        <div class="subtitle">加密貨幣交易風險預測系統</div>
        <div class="badge">XGBoost Model | 準確率 85.2%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 載入資料
    df = load_predictions()
    
    # 計算統計資料
    total_users = len(df)
    suspicious_users = len(df[df['status'] == 1])
    normal_users = len(df[df['status'] == 0])
    suspicious_rate = (suspicious_users / total_users) * 100
    normal_rate = (normal_users / total_users) * 100
    
    # KPI 卡片 - 4 列
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">總用戶數</div>
            <div class="kpi-value" style="color: #3b82f6;">{total_users:,}</div>
            <div class="kpi-change" style="color: #64748b;">已分析</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">✅</div>
            <div class="kpi-label">正常用戶</div>
            <div class="kpi-value" style="color: #10b981;">{normal_users:,}</div>
            <div class="kpi-change" style="color: #10b981;">▼ {normal_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">⚠️</div>
            <div class="kpi-label">可疑用戶</div>
            <div class="kpi-value" style="color: #ef4444;">{suspicious_users:,}</div>
            <div class="kpi-change" style="color: #ef4444;">▲ {suspicious_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">風險比率</div>
            <div class="kpi-value" style="color: #f59e0b;">{suspicious_rate:.1f}%</div>
            <div class="kpi-change" style="color: #f59e0b;">需關注</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 圖表區域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 用戶分布</div>', unsafe_allow_html=True)
        
        # 圓餅圖
        fig_pie = go.Figure(data=[go.Pie(
            labels=['正常用戶', '可疑用戶'],
            values=[normal_users, suspicious_users],
            hole=0.5,
            marker=dict(
                colors=['#10b981', '#ef4444'],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=16, color='white', family='Arial Black'),
            pull=[0.05, 0.1]
        )])
        
        fig_pie.update_layout(
            height=350,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14, family='Arial'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 數量比較</div>', unsafe_allow_html=True)
        
        # 長條圖
        fig_bar = go.Figure(data=[
            go.Bar(
                x=['正常用戶', '可疑用戶'],
                y=[normal_users, suspicious_users],
                marker=dict(
                    color=['#10b981', '#ef4444'],
                    line=dict(color='white', width=2)
                ),
                text=[f'{normal_users:,}<br>{normal_rate:.1f}%', f'{suspicious_users:,}<br>{suspicious_rate:.1f}%'],
                textposition='outside',
                textfont=dict(size=16, color='#1e293b', family='Arial Black')
            )
        ])
        
        fig_bar.update_layout(
            height=350,
            yaxis_title='用戶數量',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14, family='Arial'),
            showlegend=False,
            yaxis=dict(gridcolor='#f1f5f9')
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 搜尋功能
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<div class="search-title">🔍 查詢用戶預測結果</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_id_input = st.text_input(
            "輸入用戶 ID",
            placeholder="例如: 500, 397, 1234...",
            label_visibility="collapsed",
            key="user_search"
        )
    
    with col2:
        search_button = st.button("🔍 查詢", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 處理搜尋
    if search_button and user_id_input:
        try:
            user_id = int(user_id_input.strip())
            user_data = df[df['user_id'] == user_id]
            
            if len(user_data) > 0:
                status = int(user_data.iloc[0]['status'])
                status_text = "可疑用戶" if status == 1 else "正常用戶"
                status_class = "status-suspicious" if status == 1 else "status-normal"
                status_icon = "⚠️" if status == 1 else "✅"
                risk_level = "高風險" if status == 1 else "低風險"
                
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-header">
                        <div class="user-id-display">👤 用戶 ID: {user_id}</div>
                        <div class="status-badge {status_class}">{status_icon} {status_text}</div>
                    </div>
                    <div class="result-details">
                        <div class="detail-row">
                            <span class="detail-label">📊 預測結果</span>
                            <span class="detail-value">{status} {'(可疑)' if status == 1 else '(正常)'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🎯 風險等級</span>
                            <span class="detail-value" style="color: {'#ef4444' if status == 1 else '#10b981'};">{risk_level}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">🤖 預測模型</span>
                            <span class="detail-value">XGBoost Classifier</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">⏰ 查詢時間</span>
                            <span class="detail-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                        <div class="detail-row" style="border-bottom: none;">
                            <span class="detail-label">📈 模型準確率</span>
                            <span class="detail-value">85.2%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if status == 1:
                    st.error("⚠️ **警告**: 此用戶被標記為可疑，建議進行以下處置：\n\n1. 🔒 暫時限制交易功能\n2. 📞 聯繫用戶進行身份驗證\n3. 📋 提交詳細調查報告\n4. 👁️ 加強監控後續活動")
                else:
                    st.success("✅ **正常**: 此用戶行為正常，無異常風險指標。可繼續正常交易。")
            else:
                st.error(f"❌ **找不到用戶**: 用戶 ID {user_id} 不存在於預測結果中。")
        except ValueError:
            st.error("❌ **輸入錯誤**: 請輸入有效的數字 ID。")
    
    # 顯示部分資料
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📋 預測結果樣本</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # 可疑用戶樣本
    suspicious_sample = df[df['status'] == 1].head(15)
    normal_sample = df[df['status'] == 0].head(15)
    
    with col1:
        st.markdown("**⚠️ 可疑用戶 (前15筆)**")
        if len(suspicious_sample) > 0:
            # 添加風險等級列
            display_df = suspicious_sample.copy()
            display_df['風險等級'] = '🔴 高風險'
            display_df = display_df.rename(columns={'user_id': '用戶ID', 'status': '狀態'})
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("✅ 無可疑用戶")
    
    with col2:
        st.markdown("**✅ 正常用戶 (前15筆)**")
        # 添加風險等級列
        display_df = normal_sample.copy()
        display_df['風險等級'] = '🟢 低風險'
        display_df = display_df.rename(columns={'user_id': '用戶ID', 'status': '狀態'})
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style='background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 2rem; margin-top: 2rem; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.1);'>
        <p style="font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;">
            <strong>BitoGuard</strong> 風控預測系統
        </p>
        <p style="font-size: 0.9rem; color: #64748b;">
            Powered by XGBoost Machine Learning | © 2024 BitoGuard Team
        </p>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.5rem;">
            🔒 安全 · 🎯 精準 · ⚡ 即時
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
