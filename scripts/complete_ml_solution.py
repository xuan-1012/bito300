#!/usr/bin/env python3
"""
Complete ML Solution using all available behavior data endpoints
"""
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("BitoPro Competition - Complete ML Solution")
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
        print(f"    ✗ Failed to parse JSON (response too large)")
        # Try with limit
        r = requests.get(f'{url.split("?")[0]}?limit=100000', timeout=60)
        df = pd.DataFrame(r.json())
        print(f"    ✓ {len(df)} records (limited)")
        return df

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

# Step 3: Train model
print("\nStep 3: Training model...")

feature_cols = [col for col in train_features.columns if col != 'user_id']
X = train_data[feature_cols].fillna(0)
y = train_data['status']

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)
print("  ✓ Model trained")

# Evaluate
y_val_pred = model.predict(X_val_scaled)
y_val_proba = model.predict_proba(X_val_scaled)[:, 1]

print(f"\nValidation Performance:")
print(f"  AUC: {roc_auc_score(y_val, y_val_proba):.4f}")
print(classification_report(y_val, y_val_pred, target_names=['Normal', 'Suspicious']))

# Step 4: Generate predictions
print("\nStep 4: Generating predictions...")
predict_user_ids = predict_labels['user_id'].values
print(f"  Engineering prediction features for {len(predict_user_ids)} users...")
predict_features = engineer_features(predict_user_ids)

X_predict = predict_features[feature_cols].fillna(0)
X_predict_scaled = scaler.transform(X_predict)

predictions = model.predict(X_predict_scaled)

# Step 5: Create submission
submission = pd.DataFrame({
    'user_id': predict_user_ids,
    'status': predictions
})

# Sort by user_id
submission = submission.sort_values('user_id').reset_index(drop=True)

output_file = 'your_team_name_new.csv'
submission.to_csv(output_file, index=False)

print(f"\n✓ Submission file created: {output_file}")
print(f"  Total users: {len(submission)}")
print(f"  Predicted suspicious: {predictions.sum()} ({predictions.mean()*100:.2f}%)")
print(f"  Predicted normal: {(predictions==0).sum()} ({(1-predictions.mean())*100:.2f}%)")

print("\nFirst 20 predictions:")
print(submission.head(20).to_string(index=False))

print("\n" + "=" * 80)
print("✓ Complete! Ready for submission")
print("=" * 80)
