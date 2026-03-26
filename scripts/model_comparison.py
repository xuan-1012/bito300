#!/usr/bin/env python3
"""
Model Comparison for BitoPro Competition
Compare multiple classifiers: XGBoost, Random Forest, LightGBM, Logistic Regression, etc.
"""
import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, precision_recall_curve, auc
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("BitoPro Competition - Model Comparison")
print("=" * 80)

# Step 1: Fetch all data
print("\nStep 1: Fetching all behavior data...")

def fetch_data(endpoint, limit=None):
    print(f"  Fetching {endpoint}...")
    url = f'https://aws-event-api.bitopro.com/{endpoint}'
    if limit:
        url += f'?limit={limit}'
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        print(f"    ✗ Error: {r.status_code}")
        return pd.DataFrame()
    try:
        df = pd.DataFrame(r.json())
        print(f"    ✓ {len(df)} records")
        return df
    except:
        print(f"    ✗ Failed to parse JSON")
        return pd.DataFrame()

# Fetch all datasets
usdt_twd = fetch_data('usdt_twd_trading')
crypto_transfer = fetch_data('crypto_transfer')
user_info = fetch_data('user_info')
twd_transfer = fetch_data('twd_transfer')
usdt_swap = fetch_data('usdt_swap')
train_labels = fetch_data('train_label')
predict_labels = fetch_data('predict_label')

print(f"\n✓ All data fetched successfully")

# Step 2: Feature Engineering
print("\nStep 2: Feature engineering...")

def engineer_features(user_ids):
    features_list = []
    
    for user_id in user_ids:
        features = {'user_id': user_id}
        
        # USDT/TWD Trading features
        user_trades = usdt_twd[usdt_twd['user_id'] == user_id]
        features['trade_count'] = len(user_trades)
        features['trade_amount_sum'] = user_trades['trade_samount'].sum() if len(user_trades) > 0 else 0
        features['trade_amount_mean'] = user_trades['trade_samount'].mean() if len(user_trades) > 0 else 0
        features['trade_amount_std'] = user_trades['trade_samount'].std() if len(user_trades) > 0 else 0
        features['buy_ratio'] = user_trades['is_buy'].mean() if len(user_trades) > 0 else 0
        features['market_order_ratio'] = user_trades['is_market'].mean() if len(user_trades) > 0 else 0
        
        # Crypto Transfer features
        if not crypto_transfer.empty and 'user_id' in crypto_transfer.columns:
            user_crypto = crypto_transfer[crypto_transfer['user_id'] == user_id]
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
        user_twd = twd_transfer[twd_transfer['user_id'] == user_id]
        features['twd_transfer_count'] = len(user_twd)
        features['twd_amount_sum'] = user_twd['ori_samount'].sum() if len(user_twd) > 0 else 0
        features['twd_amount_mean'] = user_twd['ori_samount'].mean() if len(user_twd) > 0 else 0
        
        # USDT Swap features
        user_swap = usdt_swap[usdt_swap['user_id'] == user_id]
        features['swap_count'] = len(user_swap)
        features['swap_twd_sum'] = user_swap['twd_samount'].sum() if len(user_swap) > 0 else 0
        
        # User Info features
        user_data = user_info[user_info['user_id'] == user_id]
        if len(user_data) > 0:
            features['age'] = user_data.iloc[0]['age'] if pd.notna(user_data.iloc[0]['age']) else 0
            features['sex'] = 1 if user_data.iloc[0]['sex'] == 'M' else 0
            features['has_level2'] = 1 if pd.notna(user_data.iloc[0]['level2_finished_at']) else 0
        else:
            features['age'] = 0
            features['sex'] = 0
            features['has_level2'] = 0
        
        features_list.append(features)
    
    return pd.DataFrame(features_list)

# Engineer features for training data
print("  Engineering training features...")
train_user_ids = train_labels['user_id'].values
train_features = engineer_features(train_user_ids)
train_data = train_features.merge(train_labels, on='user_id')

print(f"  ✓ Training features: {train_features.shape}")

# Prepare data
feature_cols = [col for col in train_features.columns if col != 'user_id']
X = train_data[feature_cols].fillna(0)
y = train_data['status']

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

print(f"\nTraining set: {X_train.shape}, Validation set: {X_val.shape}")
print(f"Class distribution - Train: {y_train.value_counts().to_dict()}")
print(f"Class distribution - Val: {y_val.value_counts().to_dict()}")

# Step 3: Train and compare multiple models
print("\n" + "=" * 80)
print("Step 3: Training and comparing multiple models...")
print("=" * 80)

models = {}
results = {}

# 1. Random Forest
print("\n[1/5] Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
models['Random Forest'] = rf_model

y_pred_rf = rf_model.predict(X_val_scaled)
y_proba_rf = rf_model.predict_proba(X_val_scaled)[:, 1]
auc_rf = roc_auc_score(y_val, y_proba_rf)

results['Random Forest'] = {
    'model': rf_model,
    'predictions': y_pred_rf,
    'probabilities': y_proba_rf,
    'auc': auc_rf
}

print(f"  ✓ Random Forest AUC: {auc_rf:.4f}")

# 2. XGBoost
print("\n[2/5] Training XGBoost...")
try:
    import xgboost as xgb
    
    # Calculate scale_pos_weight for imbalanced data
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        eval_metric='auc'
    )
    xgb_model.fit(X_train_scaled, y_train)
    models['XGBoost'] = xgb_model
    
    y_pred_xgb = xgb_model.predict(X_val_scaled)
    y_proba_xgb = xgb_model.predict_proba(X_val_scaled)[:, 1]
    auc_xgb = roc_auc_score(y_val, y_proba_xgb)
    
    results['XGBoost'] = {
        'model': xgb_model,
        'predictions': y_pred_xgb,
        'probabilities': y_proba_xgb,
        'auc': auc_xgb
    }
    
    print(f"  ✓ XGBoost AUC: {auc_xgb:.4f}")
except ImportError:
    print("  ✗ XGBoost not installed. Run: pip install xgboost")

# 3. LightGBM
print("\n[3/5] Training LightGBM...")
try:
    import lightgbm as lgb
    
    lgb_model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgb_model.fit(X_train_scaled, y_train)
    models['LightGBM'] = lgb_model
    
    y_pred_lgb = lgb_model.predict(X_val_scaled)
    y_proba_lgb = lgb_model.predict_proba(X_val_scaled)[:, 1]
    auc_lgb = roc_auc_score(y_val, y_proba_lgb)
    
    results['LightGBM'] = {
        'model': lgb_model,
        'predictions': y_pred_lgb,
        'probabilities': y_proba_lgb,
        'auc': auc_lgb
    }
    
    print(f"  ✓ LightGBM AUC: {auc_lgb:.4f}")
except ImportError:
    print("  ✗ LightGBM not installed. Run: pip install lightgbm")

# 4. Gradient Boosting
print("\n[4/5] Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
models['Gradient Boosting'] = gb_model

y_pred_gb = gb_model.predict(X_val_scaled)
y_proba_gb = gb_model.predict_proba(X_val_scaled)[:, 1]
auc_gb = roc_auc_score(y_val, y_proba_gb)

results['Gradient Boosting'] = {
    'model': gb_model,
    'predictions': y_pred_gb,
    'probabilities': y_proba_gb,
    'auc': auc_gb
}

print(f"  ✓ Gradient Boosting AUC: {auc_gb:.4f}")

# 5. Logistic Regression
print("\n[5/5] Training Logistic Regression...")
lr_model = LogisticRegression(
    class_weight='balanced',
    max_iter=1000,
    random_state=42,
    n_jobs=-1
)
lr_model.fit(X_train_scaled, y_train)
models['Logistic Regression'] = lr_model

y_pred_lr = lr_model.predict(X_val_scaled)
y_proba_lr = lr_model.predict_proba(X_val_scaled)[:, 1]
auc_lr = roc_auc_score(y_val, y_proba_lr)

results['Logistic Regression'] = {
    'model': lr_model,
    'predictions': y_pred_lr,
    'probabilities': y_proba_lr,
    'auc': auc_lr
}

print(f"  ✓ Logistic Regression AUC: {auc_lr:.4f}")

# Step 4: Compare results
print("\n" + "=" * 80)
print("Step 4: Model Comparison Results")
print("=" * 80)

comparison_data = []
for model_name, result in results.items():
    y_pred = result['predictions']
    y_proba = result['probabilities']
    
    # Calculate metrics
    tn, fp, fn, tp = confusion_matrix(y_val, y_pred).ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Calculate PR-AUC
    precision_curve, recall_curve, _ = precision_recall_curve(y_val, y_proba)
    pr_auc = auc(recall_curve, precision_curve)
    
    comparison_data.append({
        'Model': model_name,
        'AUC-ROC': result['auc'],
        'AUC-PR': pr_auc,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'TP': tp,
        'FP': fp,
        'TN': tn,
        'FN': fn
    })

comparison_df = pd.DataFrame(comparison_data)
comparison_df = comparison_df.sort_values('AUC-ROC', ascending=False)

print("\n📊 Model Performance Comparison:")
print(comparison_df.to_string(index=False))

# Find best model
best_model_name = comparison_df.iloc[0]['Model']
best_model = results[best_model_name]['model']
best_auc = comparison_df.iloc[0]['AUC-ROC']

print(f"\n🏆 Best Model: {best_model_name} (AUC: {best_auc:.4f})")

# Step 5: Detailed reports for each model
print("\n" + "=" * 80)
print("Step 5: Detailed Classification Reports")
print("=" * 80)

for model_name, result in results.items():
    print(f"\n{'='*80}")
    print(f"Model: {model_name}")
    print(f"{'='*80}")
    print(f"AUC-ROC: {result['auc']:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_val, result['predictions'], target_names=['Normal', 'Suspicious']))
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_val, result['predictions'])
    print(f"                Predicted")
    print(f"                Normal  Suspicious")
    print(f"Actual Normal   {cm[0][0]:6d}  {cm[0][1]:10d}")
    print(f"       Suspicious {cm[1][0]:4d}  {cm[1][1]:10d}")

# Step 6: Generate predictions with all models
print("\n" + "=" * 80)
print("Step 6: Generating predictions for all models...")
print("=" * 80)

predict_user_ids = predict_labels['user_id'].values
print(f"  Engineering prediction features for {len(predict_user_ids)} users...")
predict_features = engineer_features(predict_user_ids)

X_predict = predict_features[feature_cols].fillna(0)
X_predict_scaled = scaler.transform(X_predict)

# Generate predictions for each model
for model_name, result in results.items():
    model = result['model']
    predictions = model.predict(X_predict_scaled)
    
    submission = pd.DataFrame({
        'user_id': predict_user_ids,
        'status': predictions
    })
    submission = submission.sort_values('user_id').reset_index(drop=True)
    
    # Save to file
    filename = f"predictions_{model_name.replace(' ', '_').lower()}.csv"
    submission.to_csv(filename, index=False)
    
    suspicious_count = predictions.sum()
    suspicious_pct = (suspicious_count / len(predictions)) * 100
    
    print(f"\n✓ {model_name}:")
    print(f"  File: {filename}")
    print(f"  Suspicious: {suspicious_count} ({suspicious_pct:.2f}%)")
    print(f"  Normal: {len(predictions) - suspicious_count} ({100-suspicious_pct:.2f}%)")

# Save comparison results
comparison_df.to_csv('model_comparison_results.csv', index=False)
print(f"\n✓ Comparison results saved to: model_comparison_results.csv")

print("\n" + "=" * 80)
print("✓ Model Comparison Complete!")
print("=" * 80)
print(f"\n🏆 Recommended model: {best_model_name}")
print(f"   Use file: predictions_{best_model_name.replace(' ', '_').lower()}.csv")
