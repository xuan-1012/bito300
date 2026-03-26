"""
BitoGuard 風控儀表板
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
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
        color: #fff;
        margin: 0;
    }
    
    .live-badge {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .live-dot {
        width: 6px;
        height: 6px;
        background: #ef4444;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* 小卡片設計 - 台北城市儀表板風格 */
    .mini-card {
        background: #1a1f2e;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.2s;
    }
    
    .mini-card:hover {
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }
    
    .card-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    
    .card-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #fff;
        line-height: 1;
    }
    
    .card-change {
        font-size: 0.75rem;
        margin-top: 0.25rem;
        font-weight: 600;
    }
    
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .neutral { color: #64748b; }
    
    /* 圖表卡片 */
    .chart-card {
        background: #1a1f2e;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .chart-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    /* 警示框 - 緊湊版 */
    .alert {
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        border-left: 3px solid;
    }
    
    .alert-danger {
        background: rgba(239, 68, 68, 0.1);
        border-color: #ef4444;
        color: #fca5a5;
    }
    
    /* 按鈕 */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #2563eb;
        transform: translateY(-1px);
    }
    
    /* 表格樣式 */
    .dataframe {
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'selected_account' not in st.session_state:
    st.session_state.selected_account = None
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = False
if 'api_data_cache' not in st.session_state:
    st.session_state.api_data_cache = {}
if 'model' not in st.session_state:
    st.session_state.model = None
if 'scaler' not in st.session_state:
    st.session_state.scaler = None

# ============================================================================
# REAL API DATA FETCHING
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_bitopro_data(endpoint, limit=None):
    """從 BitoPro API 獲取真實資料"""
    try:
        url = f'https://aws-event-api.bitopro.com/{endpoint}'
        if limit:
            url += f'?limit={limit}'
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        elif response.status_code == 502:
            st.warning(f"⚠️ API 暫時無法使用: {endpoint} (502 Bad Gateway) - 使用空資料")
            return pd.DataFrame()
        else:
            st.warning(f"⚠️ API 錯誤: {endpoint} - {response.status_code}")
            return pd.DataFrame()
    except requests.exceptions.Timeout:
        st.warning(f"⚠️ API 請求超時: {endpoint}")
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ 獲取資料失敗: {endpoint} - {str(e)}")
        return pd.DataFrame()

def load_api_data():
    """載入所有 BitoPro API 資料"""
    if not st.session_state.api_data_cache:
        with st.spinner('正在從 BitoPro API 載入資料...'):
            progress_text = st.empty()
            
            progress_text.text('📊 載入 USDT/TWD 交易資料...')
            usdt_twd = fetch_bitopro_data('usdt_twd_trading')
            
            progress_text.text('💰 載入加密貨幣轉帳資料...')
            crypto_transfer = fetch_bitopro_data('crypto_transfer')
            
            progress_text.text('👤 載入用戶資訊...')
            user_info = fetch_bitopro_data('user_info')
            
            progress_text.text('💵 載入 TWD 轉帳資料...')
            twd_transfer = fetch_bitopro_data('twd_transfer')
            
            progress_text.text('🔄 載入 USDT 兌換資料...')
            usdt_swap = fetch_bitopro_data('usdt_swap')
            
            progress_text.text('🏷️ 載入訓練標籤...')
            train_labels = fetch_bitopro_data('train_label')
            
            progress_text.empty()
            
            # 檢查是否有足夠的資料
            if usdt_twd.empty and twd_transfer.empty and usdt_swap.empty:
                st.error("❌ 無法載入任何交易資料，請檢查 API 連線")
                return None
            
            if train_labels.empty:
                st.error("❌ 無法載入訓練標籤，無法訓練模型")
                return None
            
            st.session_state.api_data_cache = {
                'usdt_twd': usdt_twd,
                'crypto_transfer': crypto_transfer,
                'user_info': user_info,
                'twd_transfer': twd_transfer,
                'usdt_swap': usdt_swap,
                'train_labels': train_labels,
            }
            
            # 顯示資料載入摘要
            st.success(f"""
            ✅ 資料載入完成:
            - USDT/TWD 交易: {len(usdt_twd)} 筆
            - 加密貨幣轉帳: {len(crypto_transfer)} 筆
            - 用戶資訊: {len(user_info)} 筆
            - TWD 轉帳: {len(twd_transfer)} 筆
            - USDT 兌換: {len(usdt_swap)} 筆
            - 訓練標籤: {len(train_labels)} 筆
            """)
            
    return st.session_state.api_data_cache

def engineer_features_for_user(user_id, api_data):
    """為單一用戶進行特徵工程"""
    features = {'user_id': user_id}
    
    # USDT/TWD Trading features
    user_trades = api_data['usdt_twd'][api_data['usdt_twd']['user_id'] == user_id]
    features['trade_count'] = len(user_trades)
    features['trade_amount_sum'] = user_trades['trade_samount'].sum() if len(user_trades) > 0 else 0
    features['trade_amount_mean'] = user_trades['trade_samount'].mean() if len(user_trades) > 0 else 0
    features['trade_amount_std'] = user_trades['trade_samount'].std() if len(user_trades) > 0 else 0
    features['buy_ratio'] = user_trades['is_buy'].mean() if len(user_trades) > 0 else 0
    features['market_order_ratio'] = user_trades['is_market'].mean() if len(user_trades) > 0 else 0
    
    # Crypto Transfer features
    if not api_data['crypto_transfer'].empty and 'user_id' in api_data['crypto_transfer'].columns:
        user_crypto = api_data['crypto_transfer'][api_data['crypto_transfer']['user_id'] == user_id]
        features['crypto_transfer_count'] = len(user_crypto)
        features['crypto_amount_sum'] = user_crypto['ori_samount'].sum() if len(user_crypto) > 0 else 0
        features['crypto_amount_mean'] = user_crypto['ori_samount'].mean() if len(user_crypto) > 0 else 0
        features['unique_currencies'] = user_crypto['currency'].nunique() if len(user_crypto) > 0 else 0
    else:
        features['crypto_transfer_count'] = 0
        features['crypto_amount_sum'] = 0
        features['crypto_amount_mean'] = 0
        features['unique_currencies'] = 0
    
    # TWD Transfer features
    user_twd = api_data['twd_transfer'][api_data['twd_transfer']['user_id'] == user_id]
    features['twd_transfer_count'] = len(user_twd)
    features['twd_amount_sum'] = user_twd['ori_samount'].sum() if len(user_twd) > 0 else 0
    features['twd_amount_mean'] = user_twd['ori_samount'].mean() if len(user_twd) > 0 else 0
    
    # USDT Swap features
    user_swap = api_data['usdt_swap'][api_data['usdt_swap']['user_id'] == user_id]
    features['swap_count'] = len(user_swap)
    features['swap_twd_sum'] = user_swap['twd_samount'].sum() if len(user_swap) > 0 else 0
    
    # User Info features
    user_data = api_data['user_info'][api_data['user_info']['user_id'] == user_id]
    if len(user_data) > 0:
        features['age'] = user_data.iloc[0]['age'] if pd.notna(user_data.iloc[0]['age']) else 0
        features['sex'] = 1 if user_data.iloc[0]['sex'] == 'M' else 0
        features['has_level2'] = 1 if pd.notna(user_data.iloc[0]['level2_finished_at']) else 0
    else:
        features['age'] = 0
        features['sex'] = 0
        features['has_level2'] = 0
    
    return features

def train_model_if_needed(api_data):
    """訓練模型（如果尚未訓練）"""
    if st.session_state.model is None:
        with st.spinner('正在訓練風險評估模型...'):
            # 獲取訓練資料
            train_labels = api_data['train_labels']
            
            # 確保訓練資料包含兩個類別：分層抽樣
            class_0 = train_labels[train_labels['status'] == 0]
            class_1 = train_labels[train_labels['status'] == 1]
            
            # 從每個類別中抽取樣本
            n_samples_per_class = 500
            if len(class_0) > 0 and len(class_1) > 0:
                # 兩個類別都存在
                sample_0 = class_0.sample(min(n_samples_per_class, len(class_0)), random_state=42)
                sample_1 = class_1.sample(min(n_samples_per_class, len(class_1)), random_state=42)
                train_labels_sampled = pd.concat([sample_0, sample_1], ignore_index=True)
            elif len(class_0) > 0:
                # 只有類別 0
                train_labels_sampled = class_0.sample(min(1000, len(class_0)), random_state=42)
            else:
                # 只有類別 1
                train_labels_sampled = class_1.sample(min(1000, len(class_1)), random_state=42)
            
            # 打亂順序
            train_labels_sampled = train_labels_sampled.sample(frac=1, random_state=42).reset_index(drop=True)
            train_user_ids = train_labels_sampled['user_id'].values
            
            # 特徵工程
            features_list = []
            for user_id in train_user_ids:
                features_list.append(engineer_features_for_user(user_id, api_data))
            
            train_features = pd.DataFrame(features_list)
            train_data = train_features.merge(train_labels_sampled, on='user_id')
            
            # 準備訓練資料
            feature_cols = [col for col in train_features.columns if col != 'user_id']
            X = train_data[feature_cols].fillna(0)
            y = train_data['status']
            
            # 檢查類別分布
            unique_classes = y.unique()
            if len(unique_classes) < 2:
                st.warning(f"⚠️ 訓練資料只有一個類別 ({unique_classes[0]})，使用模擬資料補充")
                # 如果只有一個類別，添加一些模擬的另一個類別資料
                if 0 not in unique_classes:
                    # 只有類別 1，添加一些類別 0
                    mock_features = X.sample(min(10, len(X)), random_state=42).copy()
                    mock_features = mock_features * 0.5  # 降低特徵值
                    X = pd.concat([X, mock_features], ignore_index=True)
                    y = pd.concat([y, pd.Series([0] * len(mock_features))], ignore_index=True)
                else:
                    # 只有類別 0，添加一些類別 1
                    mock_features = X.sample(min(10, len(X)), random_state=42).copy()
                    mock_features = mock_features * 2.0  # 提高特徵值
                    X = pd.concat([X, mock_features], ignore_index=True)
                    y = pd.concat([y, pd.Series([1] * len(mock_features))], ignore_index=True)
            
            # 標準化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 訓練模型
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_scaled, y)
            
            st.session_state.model = model
            st.session_state.scaler = scaler
            st.session_state.feature_cols = feature_cols
            
    return st.session_state.model, st.session_state.scaler, st.session_state.feature_cols

def predict_risk_for_user(user_id, api_data):
    """為用戶預測風險分數"""
    try:
        # 訓練模型（如果需要）
        model, scaler, feature_cols = train_model_if_needed(api_data)
        
        # 特徵工程
        features = engineer_features_for_user(user_id, api_data)
        features_df = pd.DataFrame([features])
        
        # 預測
        X = features_df[feature_cols].fillna(0)
        X_scaled = scaler.transform(X)
        
        # 預測機率
        proba = model.predict_proba(X_scaled)[0]
        
        # 處理不同類別情況
        if len(model.classes_) == 1:
            # 只有一個類別
            if model.classes_[0] == 1:
                # 只訓練了異常類別
                risk_score = proba[0]
                prediction = 1
            else:
                # 只訓練了正常類別
                risk_score = 1 - proba[0]
                prediction = 0
        elif len(model.classes_) == 2:
            # 有兩個類別（正常情況）
            if 1 in model.classes_:
                # 找到類別 1 的索引
                class_1_idx = list(model.classes_).index(1)
                risk_score = proba[class_1_idx]
            else:
                # 沒有類別 1，使用類別 0 的反向機率
                risk_score = 1 - proba[0]
            prediction = model.predict(X_scaled)[0]
        else:
            # 異常情況：超過兩個類別
            risk_score = proba.max()
            prediction = model.predict(X_scaled)[0]
        
        return {
            'user_id': user_id,
            'risk_score': float(risk_score),
            'prediction': int(prediction),
            'label': 'Suspicious' if prediction == 1 else 'Normal',
            'features': features
        }
    
    except Exception as e:
        st.error(f"預測失敗: {str(e)}")
        # 返回預設值
        return {
            'user_id': user_id,
            'risk_score': 0.5,
            'prediction': 0,
            'label': 'Unknown',
            'features': engineer_features_for_user(user_id, api_data)
        }

def generate_mock_data(n_samples=100):
    """生成模擬交易資料"""
    np.random.seed(42)
    
    # 生成正常和異常帳號
    n_suspicious = int(n_samples * 0.15)  # 15% 異常
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
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    return df

def get_risk_level(score):
    """根據風險分數返回風險等級"""
    if score >= 0.7:
        return "高風險", "risk-high"
    elif score >= 0.5:
        return "中風險", "risk-medium"
    else:
        return "低風險", "risk-low"

def get_risk_reasons(row):
    """生成風險原因說明"""
    reasons = []
    
    if row['night_transaction_ratio'] > 0.4:
        reasons.append(f"🌙 夜間交易比例異常高 ({row['night_transaction_ratio']:.1%})")
    
    if row['large_transaction_ratio'] > 0.35:
        reasons.append(f"💰 大額交易比例過高 ({row['large_transaction_ratio']:.1%})")
    
    if row['velocity_score'] > 0.6:
        reasons.append(f"⚡ 交易速度異常 (velocity: {row['velocity_score']:.2f})")
    
    if row['unique_counterparties'] > 100:
        reasons.append(f"👥 交易對手數量異常 ({row['unique_counterparties']} 個)")
    
    if row['total_volume'] > 100000:
        reasons.append(f"📊 總交易量異常 (${row['total_volume']:,.0f})")
    
    return reasons if reasons else ["✅ 無明顯異常特徵"]

def create_risk_distribution_chart(df):
    """建立風險分數分布圖 - 緊湊版"""
    fig = go.Figure()
    
    normal_data = df[df['label'] == 'Normal']['risk_score']
    fig.add_trace(go.Histogram(
        x=normal_data,
        name='正常',
        marker_color='#10b981',
        opacity=0.7,
        nbinsx=20
    ))
    
    suspicious_data = df[df['label'] == 'Suspicious']['risk_score']
    fig.add_trace(go.Histogram(
        x=suspicious_data,
        name='異常',
        marker_color='#ef4444',
        opacity=0.7,
        nbinsx=20
    ))
    
    fig.add_vline(x=0.5, line_dash="dash", line_color="#f59e0b", 
                  annotation_text="閾值")
    
    fig.update_layout(
        xaxis_title="風險分數",
        yaxis_title="數量",
        barmode='overlay',
        height=250,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10),
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="right", x=1)
    )
    
    return fig

def create_feature_importance_chart():
    """建立特徵重要性圖 - 緊湊版"""
    features = ['夜間交易', '大額交易', '交易速度', '交易對手', '交易量', '平均額']
    importance = [0.28, 0.24, 0.19, 0.15, 0.09, 0.05]
    
    fig = go.Figure(go.Bar(
        x=importance,
        y=features,
        orientation='h',
        marker_color='#3b82f6',
        text=[f'{i:.0%}' for i in importance],
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title="重要性",
        height=250,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10),
        margin=dict(l=80, r=20, t=20, b=40),
        xaxis=dict(range=[0, 0.35])
    )
    
    return fig

def create_timeline_chart(account_id):
    """建立帳號交易時間軸 - 緊湊版"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    if 'suspicious' in account_id.lower() or int(account_id.replace('ACC', '')) > 85:
        volumes = np.random.uniform(1000, 5000, 15).tolist() + \
                  np.random.uniform(5000, 15000, 15).tolist()
    else:
        volumes = np.random.uniform(500, 2000, 30)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=volumes,
        mode='lines+markers',
        name='交易量',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)'
    ))
    
    fig.update_layout(
        xaxis_title="日期",
        yaxis_title="交易量 ($)",
        height=200,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10),
        margin=dict(l=40, r=20, t=20, b=40),
        showlegend=False
    )
    
    return fig

# ============================================================================
# HEADER - 緊湊頂部列
# ============================================================================

st.markdown(f"""
<div class="top-bar">
    <div class="title">🛡️ BitoGuard 風控儀表板</div>
    <div style="display: flex; gap: 1rem; align-items: center;">
        <span style="color: #94a3b8; font-size: 0.8rem;">{datetime.now().strftime('%Y/%m/%d %H:%M')}</span>
        <div class="live-badge">
            <div class="live-dot"></div>
            LIVE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SEARCH BAR - 美觀搜尋列
# ============================================================================

st.markdown("""
<div style="background: #1a1f2e; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
    <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
        🔍 查詢帳號
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    search_input = st.text_input(
        "輸入 User ID",
        placeholder="例如: 12345 或 67890",
        label_visibility="collapsed",
        key="search_input"
    )

with col2:
    search_button = st.button("🔍 查詢", use_container_width=True, type="primary")

with col3:
    if st.button("📊 總覽", use_container_width=True):
        # 載入 API 資料並訓練模型
        api_data = load_api_data()
        train_model_if_needed(api_data)
        
        # 使用模擬資料顯示總覽（因為預測所有用戶會太慢）
        st.session_state.df = generate_mock_data(100)
        st.session_state.data_loaded = True
        st.session_state.analysis_complete = True
        st.session_state.search_mode = False
        st.rerun()

# 處理搜尋
if search_button and search_input:
    search_term = search_input.strip()
    
    # 載入 API 資料
    api_data = load_api_data()
    
    # 檢查是否為有效的 user_id
    if search_term.isdigit():
        user_id = int(search_term)
        
        # 檢查用戶是否存在於資料中
        user_exists = False
        for dataset_name, dataset in api_data.items():
            if not dataset.empty and 'user_id' in dataset.columns:
                if user_id in dataset['user_id'].values:
                    user_exists = True
                    break
        
        if user_exists:
            with st.spinner(f'正在分析用戶 {user_id}...'):
                # 預測風險
                result = predict_risk_for_user(user_id, api_data)
                
                # 儲存結果
                st.session_state.selected_account = result
                st.session_state.search_mode = True
                st.success(f"✅ 找到用戶: {user_id} | 風險分數: {result['risk_score']:.3f}")
        else:
            st.warning(f"⚠️ 找不到用戶: {search_term}")
            st.session_state.search_mode = False
    else:
        st.warning(f"⚠️ 請輸入有效的 User ID (數字)")
        st.session_state.search_mode = False

# 控制列
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"""
    <div style="color: #64748b; font-size: 0.8rem; padding: 0.5rem 0;">
        💡 提示：輸入 User ID 進行查詢（使用真實 BitoPro API 資料），或點擊「總覽」查看模擬資料
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.selectbox("", ["即時", "1H", "24H"], label_visibility="collapsed", key="timerange")

with col3:
    st.checkbox("自動更新", value=False, key="auto_refresh")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

if st.session_state.data_loaded and st.session_state.analysis_complete:
    df = st.session_state.df
    
    # 如果是搜尋模式，直接顯示該帳號詳情
    if st.session_state.search_mode and st.session_state.selected_account:
        result = st.session_state.selected_account
        
        # 帳號資訊卡片
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                    padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(59, 130, 246, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #fff;">
                        用戶 ID: {result['user_id']}
                    </div>
                    <div style="font-size: 0.9rem; color: #93c5fd; margin-top: 0.25rem;">
                        風險分數: {result['risk_score']:.3f} | 
                        等級: {'🔴 高風險' if result['risk_score'] >= 0.7 else '🟡 中風險' if result['risk_score'] >= 0.5 else '🟢 低風險'}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2rem; font-weight: 800; color: {'#ef4444' if result['risk_score'] >= 0.7 else '#f59e0b' if result['risk_score'] >= 0.5 else '#10b981'};">
                        {result['risk_score']:.3f}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3列資訊卡片
        col1, col2, col3 = st.columns(3)
        
        features = result['features']
        
        with col1:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">💰 交易統計</div>
                <div style="color: #fff; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.6;">
                    交易筆數: <strong>{int(features['trade_count'])}</strong><br>
                    交易總額: <strong>${features['trade_amount_sum']:,.0f}</strong><br>
                    平均交易: <strong>${features['trade_amount_mean']:,.0f}</strong><br>
                    買入比例: <strong>{features['buy_ratio']:.0%}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">⚡ 轉帳行為</div>
                <div style="color: #fff; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.6;">
                    加密貨幣轉帳: <strong>{int(features['crypto_transfer_count'])}</strong><br>
                    TWD 轉帳: <strong>{int(features['twd_transfer_count'])}</strong><br>
                    USDT 兌換: <strong>{int(features['swap_count'])}</strong><br>
                    幣種數量: <strong>{int(features['unique_currencies'])}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">🎯 風險評估</div>
                <div style="color: #fff; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.6;">
                    判定: <strong style="color: {'#ef4444' if result['label'] == 'Suspicious' else '#10b981'};">{result['label']}</strong><br>
                    預測: <strong>{result['prediction']}</strong><br>
                    信心度: <strong>{result['risk_score']*100:.1f}%</strong><br>
                    KYC Level 2: <strong>{'✅' if features['has_level2'] else '❌'}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 特徵詳情
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔍 詳細特徵分析</div>', unsafe_allow_html=True)
        
        # 顯示所有特徵
        feature_data = []
        for key, value in features.items():
            if key != 'user_id':
                if isinstance(value, float):
                    feature_data.append({'特徵': key, '數值': f'{value:.2f}'})
                else:
                    feature_data.append({'特徵': key, '數值': str(value)})
        
        feature_df = pd.DataFrame(feature_data)
        st.dataframe(feature_df, use_container_width=True, hide_index=True, height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 風控建議
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💡 風控建議</div>', unsafe_allow_html=True)
        
        if result['risk_score'] >= 0.7:
            st.markdown("""
            <div class="alert alert-danger">
                <strong>🚨 高風險警示</strong><br>
                建議措施：<br>
                1. 🔒 立即凍結交易功能<br>
                2. 📞 聯繫持有人驗證身份<br>
                3. 📋 提交調查報告<br>
                4. 🔍 追蹤交易對手<br>
                5. 📊 監控後續30天
            </div>
            """, unsafe_allow_html=True)
        elif result['risk_score'] >= 0.5:
            st.markdown("""
            <div class="alert" style="background: rgba(245, 158, 11, 0.1); border-color: #f59e0b; color: #fcd34d;">
                <strong>⚠️ 中風險警示</strong><br>
                建議措施：<br>
                1. 👁️ 加入監控名單<br>
                2. 📊 每日檢視報告<br>
                3. 🔔 設定即時通知
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #6ee7b7;">
                <strong>✅ 低風險</strong><br>
                維持常規監控即可
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # 總覽模式 - 顯示所有資料
        # 計算指標
        total = len(df)
        suspicious = len(df[df['label'] == 'Suspicious'])
        high_risk = len(df[df['risk_score'] >= 0.7])
        avg_risk = df['risk_score'].mean()
        detection_rate = (suspicious / total) * 100
        
        # 警示
        if suspicious > 0:
            st.markdown(f"""
            <div class="alert alert-danger">
                🚨 偵測到 <strong>{suspicious}</strong> 個可疑帳號 ({high_risk} 個高風險) - 建議立即審查
            </div>
            """, unsafe_allow_html=True)
        
        # KPI 卡片 - 5列緊湊佈局
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">總帳號</div>
                <div class="card-value">{total}</div>
                <div class="card-change neutral">監控中</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">可疑帳號</div>
                <div class="card-value" style="color: #ef4444;">{suspicious}</div>
                <div class="card-change negative">▲ {detection_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">高風險</div>
                <div class="card-value" style="color: #f59e0b;">{high_risk}</div>
                <div class="card-change negative">需處理</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">平均風險</div>
                <div class="card-value" style="color: #3b82f6;">{avg_risk:.2f}</div>
                <div class="card-change neutral">穩定</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="mini-card">
                <div class="card-label">正常帳號</div>
                <div class="card-value" style="color: #10b981;">{total - suspicious}</div>
                <div class="card-change positive">▼ {100-detection_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 圖表區 - 2x2 網格
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 風險分數分布</div>', unsafe_allow_html=True)
            fig_dist = create_risk_distribution_chart(df)
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⚡ 特徵重要性</div>', unsafe_allow_html=True)
            fig_importance = create_feature_importance_chart()
            st.plotly_chart(fig_importance, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 可疑帳號列表 - 緊湊表格
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🔍 可疑帳號 TOP 10</div>', unsafe_allow_html=True)
        
        df_suspicious = df[df['label'] == 'Suspicious'].sort_values('risk_score', ascending=False).head(10)
        
        display_data = []
        for idx, row in df_suspicious.iterrows():
            display_data.append({
                '帳號': row['account_id'],
                '風險': f"{row['risk_score']:.3f}",
                '交易量': f"${row['total_volume']/1000:.1f}K",
                '筆數': int(row['total_transactions']),
                '夜間%': f"{row['night_transaction_ratio']:.0%}",
                '速度': f"{row['velocity_score']:.2f}"
            })
        
        df_table = pd.DataFrame(display_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 詳細分析 - 可選擇帳號
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📋 帳號詳細分析</div>', unsafe_allow_html=True)
        
        selected = st.selectbox("選擇帳號", df_suspicious['account_id'].tolist(), label_visibility="collapsed")
        
        if selected:
            account = df[df['account_id'] == selected].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="color: #94a3b8; font-size: 0.75rem;">基本資訊</div>
                <div style="color: #fff; font-size: 0.9rem; margin-top: 0.25rem;">
                    ID: {account['account_id']}<br>
                    風險: {account['risk_score']:.3f}<br>
                    等級: {'高風險' if account['risk_score'] >= 0.7 else '中風險'}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="color: #94a3b8; font-size: 0.75rem;">交易統計</div>
                <div style="color: #fff; font-size: 0.9rem; margin-top: 0.25rem;">
                    交易量: ${account['total_volume']:,.0f}<br>
                    筆數: {account['total_transactions']}<br>
                    平均: ${account['avg_transaction_size']:,.0f}
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="color: #94a3b8; font-size: 0.75rem;">行為特徵</div>
                <div style="color: #fff; font-size: 0.9rem; margin-top: 0.25rem;">
                    夜間: {account['night_transaction_ratio']:.0%}<br>
                    大額: {account['large_transaction_ratio']:.0%}<br>
                    速度: {account['velocity_score']:.2f}
                </div>
                """, unsafe_allow_html=True)
            
            # 異常原因
            reasons = get_risk_reasons(account)
            st.markdown("<div style='margin-top: 0.75rem; color: #94a3b8; font-size: 0.75rem;'>異常原因</div>", unsafe_allow_html=True)
            for reason in reasons[:3]:  # 只顯示前3個
                st.markdown(f"<div style='color: #fcd34d; font-size: 0.8rem;'>• {reason}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 初始狀態
    st.markdown("""
    <div class="alert" style="background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; color: #93c5fd;">
        ℹ️ 點擊「開始分析」載入資料
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: #475569; padding: 1rem 0; font-size: 0.75rem;'>
    BitoGuard 風控儀表板 v2.0 | Powered by AI
</div>
""", unsafe_allow_html=True)
