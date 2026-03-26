"""
Process user list from CSV and generate risk assessments.
This demo shows how to process a batch of user IDs and assign risk scores.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np
from model_risk_scoring.models import TransactionFeatures
from model_risk_scoring.engines.fallback_rule_engine import FallbackRuleEngine

# Read the CSV file
print("=" * 80)
print("批次用戶風險評估 (Batch User Risk Assessment)")
print("=" * 80)

# Simulate user IDs (in production, load from CSV)
# For demo, we'll use the first 100 user IDs from your list
user_ids = [3, 10, 98, 139, 185, 218, 241, 276, 373, 397, 500, 505, 506, 572, 577, 
            778, 813, 917, 935, 1097, 1303, 1331, 1333, 1339, 1364, 1372, 1400, 1442,
            1568, 1659, 1663, 1681, 1718, 1767, 1827, 1858, 1980, 1987, 2010, 2028,
            2043, 2057, 2085, 2182, 2256, 2306, 2359, 2439, 2461, 2650, 2655, 2681,
            2710, 2715, 2733, 2786, 2846, 2874, 2879, 2953, 2973, 2994, 3054, 3056,
            3082, 3240, 3265, 3415, 3456, 3480, 3502, 3553, 3565, 3567, 3615, 3617,
            3631, 3730, 3784, 3808, 3857, 3895, 3934, 3942, 4001, 4045, 4047, 4199,
            4234, 4282, 4358, 4543, 4574, 4637, 4650, 4676, 4683, 4724, 4764]

df = pd.DataFrame({'user_id': user_ids})
print(f"\n讀取用戶數: {len(df)} 個")

# Initialize risk engine
engine = FallbackRuleEngine()

# Simulate feature generation for each user
# In production, these would come from actual transaction data
np.random.seed(42)

results = []
risk_distribution = {'低風險': 0, '中度風險': 0, '高風險': 0, '極高風險': 0}

print("\n開始處理用戶...")
print("-" * 80)

for idx, row in df.iterrows():  # Process all users
    user_id = row['user_id']
    
    # Simulate transaction features (in production, fetch from database)
    # Generate realistic distribution: 70% low risk, 20% medium, 8% high, 2% critical
    risk_type = np.random.choice(['low', 'medium', 'high', 'critical'], 
                                  p=[0.70, 0.20, 0.08, 0.02])
    
    if risk_type == 'low':
        features = TransactionFeatures(
            account_id=f"user_{user_id}",
            total_volume=np.random.uniform(1000, 50000),
            transaction_count=np.random.randint(5, 50),
            avg_transaction_size=np.random.uniform(100, 1000),
            max_transaction_size=np.random.uniform(500, 5000),
            unique_counterparties=np.random.randint(5, 20),
            night_transaction_ratio=np.random.uniform(0.0, 0.2),
            rapid_transaction_count=np.random.randint(0, 5),
            round_number_ratio=np.random.uniform(0.0, 0.3),
            concentration_score=np.random.uniform(0.0, 0.4),
            velocity_score=np.random.uniform(0.5, 3.0)
        )
    elif risk_type == 'medium':
        features = TransactionFeatures(
            account_id=f"user_{user_id}",
            total_volume=np.random.uniform(80000, 150000),
            transaction_count=np.random.randint(50, 100),
            avg_transaction_size=np.random.uniform(800, 2000),
            max_transaction_size=np.random.uniform(5000, 10000),
            unique_counterparties=np.random.randint(8, 15),
            night_transaction_ratio=np.random.uniform(0.25, 0.4),
            rapid_transaction_count=np.random.randint(5, 12),
            round_number_ratio=np.random.uniform(0.3, 0.55),
            concentration_score=np.random.uniform(0.4, 0.65),
            velocity_score=np.random.uniform(3.0, 7.0)
        )
    elif risk_type == 'high':
        features = TransactionFeatures(
            account_id=f"user_{user_id}",
            total_volume=np.random.uniform(200000, 400000),
            transaction_count=np.random.randint(100, 200),
            avg_transaction_size=np.random.uniform(1500, 3000),
            max_transaction_size=np.random.uniform(10000, 30000),
            unique_counterparties=np.random.randint(3, 8),
            night_transaction_ratio=np.random.uniform(0.45, 0.65),
            rapid_transaction_count=np.random.randint(15, 30),
            round_number_ratio=np.random.uniform(0.55, 0.75),
            concentration_score=np.random.uniform(0.7, 0.9),
            velocity_score=np.random.uniform(8.0, 15.0)
        )
    else:  # critical
        features = TransactionFeatures(
            account_id=f"user_{user_id}",
            total_volume=np.random.uniform(500000, 1000000),
            transaction_count=np.random.randint(200, 500),
            avg_transaction_size=np.random.uniform(2500, 5000),
            max_transaction_size=np.random.uniform(30000, 100000),
            unique_counterparties=np.random.randint(1, 5),
            night_transaction_ratio=np.random.uniform(0.7, 0.95),
            rapid_transaction_count=np.random.randint(40, 100),
            round_number_ratio=np.random.uniform(0.8, 0.95),
            concentration_score=np.random.uniform(0.9, 1.0),
            velocity_score=np.random.uniform(15.0, 25.0)
        )
    
    # Calculate risk score
    result = engine.calculate_risk_score(features)
    
    # Determine risk level
    if result['risk_score'] >= 70:
        risk_level = '極高風險'
        status = 'CRITICAL'
    elif result['risk_score'] >= 50:
        risk_level = '高風險'
        status = 'HIGH'
    elif result['risk_score'] >= 30:
        risk_level = '中度風險'
        status = 'MEDIUM'
    else:
        risk_level = '低風險'
        status = 'LOW'
    
    risk_distribution[risk_level] += 1
    
    results.append({
        'user_id': user_id,
        'status': status,
        'risk_score': result['risk_score'],
        'risk_level': risk_level,
        'risk_factors_count': len(result['risk_factors']),
        'confidence': result['confidence']
    })
    
    if (idx + 1) % 20 == 0:
        print(f"已處理: {idx + 1} 個用戶...")

# Create output DataFrame
output_df = pd.DataFrame(results)

# Save results
output_df[['user_id', 'status']].to_csv('user_risk_status.csv', index=False)
output_df.to_csv('user_risk_detailed.csv', index=False)

print("\n" + "=" * 80)
print("處理完成！(Processing Complete!)")
print("=" * 80)

print("\n風險分布統計 (Risk Distribution):")
print("-" * 80)
for level, count in risk_distribution.items():
    percentage = (count / len(results)) * 100
    bar = "█" * int(percentage / 2)
    print(f"{level:12s}: {bar} {count:3d} ({percentage:5.1f}%)")

print("\n風險分數統計 (Risk Score Statistics):")
print("-" * 80)
print(f"平均分數: {output_df['risk_score'].mean():.1f}")
print(f"中位數:   {output_df['risk_score'].median():.1f}")
print(f"最高分:   {output_df['risk_score'].max():.1f}")
print(f"最低分:   {output_df['risk_score'].min():.1f}")

print("\n高風險用戶 (High Risk Users - Top 10):")
print("-" * 80)
high_risk = output_df[output_df['risk_score'] >= 50].sort_values('risk_score', ascending=False).head(10)
for _, user in high_risk.iterrows():
    print(f"User {user['user_id']:6d}: {user['risk_score']:3.0f}/100 - {user['risk_level']} "
          f"({user['risk_factors_count']} 個風險因子)")

print("\n輸出檔案:")
print("-" * 80)
print("  1. user_risk_status.csv     - 簡化版 (user_id, status)")
print("  2. user_risk_detailed.csv   - 詳細版 (包含分數和風險因子)")

print("\n" + "=" * 80)
