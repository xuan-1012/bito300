#!/usr/bin/env python3
"""
Create submission CSV for BitoPro competition.
Since behavior_data endpoint is not available, we'll use a rule-based approach
based on the training labels distribution.
"""

import requests
import pandas as pd
import numpy as np

# API configuration
API_BASE = "https://aws-event-api.bitopro.com"

print("=" * 80)
print("BitoPro Competition - Submission Generator")
print("=" * 80)

# Step 1: Fetch training labels to understand the distribution
print("\nStep 1: Fetching training labels...")
try:
    response = requests.get(f"{API_BASE}/train_label")
    response.raise_for_status()
    train_labels = pd.DataFrame(response.json())
    print(f"✓ Loaded {len(train_labels)} training labels")
    
    # Analyze distribution
    suspicious_rate = train_labels['status'].mean()
    print(f"  Suspicious rate in training: {suspicious_rate*100:.2f}%")
    print(f"  Normal users: {(train_labels['status']==0).sum()}")
    print(f"  Suspicious users: {(train_labels['status']==1).sum()}")
    
except Exception as e:
    print(f"✗ Error fetching training labels: {e}")
    suspicious_rate = 0.05  # Default 5% suspicious rate
    print(f"  Using default suspicious rate: {suspicious_rate*100:.2f}%")

# Step 2: Fetch predict labels
print("\nStep 2: Fetching predict labels...")
try:
    response = requests.get(f"{API_BASE}/predict_label")
    response.raise_for_status()
    predict_labels = pd.DataFrame(response.json())
    print(f"✓ Loaded {len(predict_labels)} user IDs to predict")
    
except Exception as e:
    print(f"✗ Error fetching predict labels: {e}")
    print("  Exiting...")
    exit(1)

# Step 3: Generate predictions
print("\nStep 3: Generating predictions...")

# Strategy: Use a simple heuristic based on user_id patterns
# This is a baseline approach when behavior data is not available
user_ids = predict_labels['user_id'].values

# Create predictions based on user_id characteristics
predictions = []
for user_id in user_ids:
    # Simple heuristic: mark some users as suspicious based on patterns
    # This is just a baseline - in real scenario, use behavior data
    
    # Example heuristics (you can adjust these):
    # - Very low or very high user IDs might be test accounts
    # - User IDs with certain patterns
    
    score = 0
    
    # Heuristic 1: Extreme user IDs
    if user_id < 1000 or user_id > 900000:
        score += 0.3
    
    # Heuristic 2: User ID divisibility patterns
    if user_id % 7 == 0:  # Arbitrary pattern
        score += 0.2
    
    # Heuristic 3: Random component to match training distribution
    random_score = np.random.random()
    if random_score < suspicious_rate * 1.5:  # Slightly higher than training
        score += 0.5
    
    # Final decision
    is_suspicious = 1 if score > 0.6 else 0
    predictions.append(is_suspicious)

predictions = np.array(predictions)

# Step 4: Create submission file
print("\nStep 4: Creating submission file...")

submission = pd.DataFrame({
    'user_id': user_ids,
    'status': predictions
})

# Save to CSV
team_name = "your_team_name"  # Change this to your team name
output_file = f"{team_name}.csv"
submission.to_csv(output_file, index=False)

print(f"✓ Submission file created: {output_file}")
print(f"\nPrediction Summary:")
print(f"  Total users: {len(submission)}")
print(f"  Predicted suspicious: {predictions.sum()} ({predictions.mean()*100:.2f}%)")
print(f"  Predicted normal: {(predictions==0).sum()} ({(1-predictions.mean())*100:.2f}%)")

# Display sample
print(f"\nSample predictions (first 20):")
print(submission.head(20).to_string(index=False))

print("\n" + "=" * 80)
print("✓ Complete!")
print("=" * 80)
print(f"\nSubmission file: {output_file}")
print("Note: This is a baseline prediction without behavior data.")
print("For better results, ensure behavior_data API endpoint is accessible.")
