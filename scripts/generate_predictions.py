#!/usr/bin/env python3
"""
Generate predictions for BitoPro competition submission.
Reads user_ids from CSV, trains model, and outputs predictions.
"""

import pandas as pd
import requests
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# API endpoints
BASE_URL = "https://aws-event-api.bitopro.com"
TRAIN_LABEL_URL = f"{BASE_URL}/train_label"
BEHAVIOR_DATA_URL = f"{BASE_URL}/behavior_data"

def fetch_train_labels():
    """Fetch training labels from API."""
    print("Fetching training labels...")
    response = requests.get(TRAIN_LABEL_URL)
    response.raise_for_status()
    return response.json()

def fetch_behavior_data():
    """Fetch behavior data from API."""
    print("Fetching behavior data...")
    response = requests.get(BEHAVIOR_DATA_URL)
    response.raise_for_status()
    return response.json()

def engineer_features(behavior_df):
    """Engineer features from behavior data."""
    print("Engineering features...")
    
    # Group by user_id and aggregate
    user_features = behavior_df.groupby('user_id').agg({
        'amount': ['sum', 'mean', 'std', 'max', 'min', 'count'],
        'timestamp': ['min', 'max']
    }).reset_index()
    
    # Flatten column names
    user_features.columns = ['_'.join(col).strip('_') for col in user_features.columns.values]
    user_features.rename(columns={'user_id_': 'user_id'}, inplace=True)
    
    # Fill NaN values
    user_features.fillna(0, inplace=True)
    
    # Add derived features
    user_features['amount_range'] = user_features['amount_max'] - user_features['amount_min']
    user_features['amount_cv'] = user_features['amount_std'] / (user_features['amount_mean'] + 1e-10)
    
    return user_features

def train_model(X_train, y_train):
    """Train Random Forest classifier."""
    print("Training model...")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    return model, scaler

def main():
    # Read input CSV - try multiple possible filenames
    print("Reading input CSV...")
    possible_files = [
        'aws-event - - -csv-.csv',
        'predict_users.csv',
        'user_list.csv'
    ]
    
    input_df = None
    for filename in possible_files:
        try:
            input_df = pd.read_csv(filename)
            print(f"Successfully loaded {filename}")
            break
        except FileNotFoundError:
            continue
    
    if input_df is None:
        print("CSV file not found. Please provide the CSV file with user_ids.")
        print("Expected columns: user_id, status")
        return
    
    predict_user_ids = input_df['user_id'].values
    
    print(f"Found {len(predict_user_ids)} users to predict")
    
    # Fetch data from API
    train_labels = fetch_train_labels()
    behavior_data = fetch_behavior_data()
    
    # Convert to DataFrames
    train_df = pd.DataFrame(train_labels)
    behavior_df = pd.DataFrame(behavior_data)
    
    # Engineer features
    features_df = engineer_features(behavior_df)
    
    # Merge with training labels
    train_data = train_df.merge(features_df, on='user_id', how='left')
    train_data.fillna(0, inplace=True)
    
    # Prepare training data
    feature_cols = [col for col in train_data.columns if col not in ['user_id', 'status']]
    X_train = train_data[feature_cols].values
    y_train = train_data['status'].values
    
    print(f"Training on {len(X_train)} samples with {len(feature_cols)} features")
    
    # Train model
    model, scaler = train_model(X_train, y_train)
    
    # Prepare prediction data
    predict_features = features_df[features_df['user_id'].isin(predict_user_ids)]
    
    # Handle users not in behavior data (predict as 0 - normal)
    missing_users = set(predict_user_ids) - set(predict_features['user_id'])
    if missing_users:
        print(f"Warning: {len(missing_users)} users not found in behavior data, predicting as normal (0)")
    
    # Make predictions
    predictions = []
    for user_id in predict_user_ids:
        if user_id in predict_features['user_id'].values:
            user_data = predict_features[predict_features['user_id'] == user_id][feature_cols]
            user_data_scaled = scaler.transform(user_data)
            pred = model.predict(user_data_scaled)[0]
            predictions.append(int(pred))
        else:
            # User not in behavior data - predict as normal
            predictions.append(0)
    
    # Create output DataFrame
    output_df = pd.DataFrame({
        'user_id': predict_user_ids,
        'status': predictions
    })
    
    # Save to CSV
    output_filename = '隊伍名稱.csv'
    output_df.to_csv(output_filename, index=False)
    
    print(f"\nPredictions saved to {output_filename}")
    print(f"Total predictions: {len(predictions)}")
    print(f"Predicted as suspicious (1): {sum(predictions)}")
    print(f"Predicted as normal (0): {len(predictions) - sum(predictions)}")
    print(f"Suspicious rate: {sum(predictions)/len(predictions)*100:.2f}%")

if __name__ == "__main__":
    main()
