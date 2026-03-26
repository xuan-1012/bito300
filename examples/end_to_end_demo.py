"""
End-to-End Demo: Complete Risk Assessment Pipeline
Shows actual data flow from raw transactions to risk assessment
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from model_risk_scoring.models import (
    TransactionFeatures,
    InferenceMode,
    RiskLevel
)
from model_risk_scoring.engines.fallback_rule_engine import FallbackRuleEngine
from model_risk_scoring.utils.feature_processor import FeatureProcessor

print("=" * 80)
print("END-TO-END RISK ASSESSMENT DEMO")
print("=" * 80)

# Simulate 5 different account profiles
accounts = [
    {
        "name": "正常帳戶 (Normal Account)",
        "features": TransactionFeatures(
            account_id="ACC_001",
            total_volume=25000.0,
            transaction_count=50,
            avg_transaction_size=500.0,
            max_transaction_size=2000.0,
            unique_counterparties=15,
            night_transaction_ratio=0.05,
            rapid_transaction_count=2,
            round_number_ratio=0.15,
            concentration_score=0.2,
            velocity_score=1.5
        )
    },
    {
        "name": "中度風險帳戶 (Medium Risk Account)",
        "features": TransactionFeatures(
            account_id="ACC_002",
            total_volume=120000.0,
            transaction_count=80,
            avg_transaction_size=1500.0,
            max_transaction_size=8000.0,
            unique_counterparties=10,
            night_transaction_ratio=0.35,
            rapid_transaction_count=8,
            round_number_ratio=0.45,
            concentration_score=0.55,
            velocity_score=5.0
        )
    },
    {
        "name": "高風險帳戶 (High Risk Account)",
        "features": TransactionFeatures(
            account_id="ACC_003",
            total_volume=250000.0,
            transaction_count=150,
            avg_transaction_size=1666.67,
            max_transaction_size=15000.0,
            unique_counterparties=5,
            night_transaction_ratio=0.55,
            rapid_transaction_count=25,
            round_number_ratio=0.70,
            concentration_score=0.85,
            velocity_score=12.0
        )
    },
    {
        "name": "極高風險帳戶 (Critical Risk Account)",
        "features": TransactionFeatures(
            account_id="ACC_004",
            total_volume=500000.0,
            transaction_count=200,
            avg_transaction_size=2500.0,
            max_transaction_size=50000.0,
            unique_counterparties=3,
            night_transaction_ratio=0.75,
            rapid_transaction_count=50,
            round_number_ratio=0.90,
            concentration_score=0.95,
            velocity_score=20.0
        )
    },
    {
        "name": "邊界測試帳戶 (Boundary Test Account)",
        "features": TransactionFeatures(
            account_id="ACC_005",
            total_volume=99999.0,
            transaction_count=100,
            avg_transaction_size=999.99,
            max_transaction_size=9999.0,
            unique_counterparties=8,
            night_transaction_ratio=0.29,
            rapid_transaction_count=9,
            round_number_ratio=0.49,
            concentration_score=0.49,
            velocity_score=4.9
        )
    }
]

# Initialize engines
rule_engine = FallbackRuleEngine()
feature_processor = FeatureProcessor()

# Process each account
results = []
for account in accounts:
    print(f"\n{'=' * 80}")
    print(f"帳戶: {account['name']}")
    print(f"帳戶ID: {account['features'].account_id}")
    print("=" * 80)
    
    features = account['features']
    
    # Step 1: Feature Display
    print("\n步驟 1: 特徵數據 (Feature Data)")
    print("-" * 80)
    print(f"  總交易量 (Total Volume):           ${features.total_volume:>12,.2f}")
    print(f"  交易筆數 (Transaction Count):      {features.transaction_count:>12,}")
    print(f"  平均交易額 (Avg Transaction):      ${features.avg_transaction_size:>12,.2f}")
    print(f"  最大交易額 (Max Transaction):      ${features.max_transaction_size:>12,.2f}")
    print(f"  交易對手數 (Unique Counterparties): {features.unique_counterparties:>12,}")
    print(f"  深夜交易比例 (Night Tx Ratio):      {features.night_transaction_ratio:>12.1%}")
    print(f"  快速交易數 (Rapid Tx Count):       {features.rapid_transaction_count:>12,}")
    print(f"  整數金額比例 (Round Number Ratio):  {features.round_number_ratio:>12.1%}")
    print(f"  集中度分數 (Concentration Score):   {features.concentration_score:>12.2f}")
    print(f"  交易速度 (Velocity Score):         {features.velocity_score:>12.1f} tx/hr")
    
    # Step 2: Risk Assessment
    print("\n步驟 2: 風險評估 (Risk Assessment)")
    print("-" * 80)
    result = rule_engine.calculate_risk_score(features)
    
    # Create assessment object for display
    risk_score = result['risk_score']
    risk_factors = result['risk_factors']
    explanation = result['explanation']
    confidence = result['confidence']
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "極高風險 (CRITICAL)"
        risk_color = "🔴"
    elif risk_score >= 50:
        risk_level = "高風險 (HIGH)"
        risk_color = "🟠"
    elif risk_score >= 30:
        risk_level = "中度風險 (MEDIUM)"
        risk_color = "🟡"
    else:
        risk_level = "低風險 (LOW)"
        risk_color = "🟢"
    
    print(f"  {risk_color} 風險等級: {risk_level}")
    print(f"  風險分數: {risk_score}/100")
    print(f"  信心度: {confidence:.1%}")
    print(f"  推論模式: fallback")
    
    # Step 3: Risk Factors
    if risk_factors:
        print("\n步驟 3: 風險因子 (Risk Factors)")
        print("-" * 80)
        for i, factor in enumerate(risk_factors, 1):
            print(f"  {i}. {factor}")
    
    # Step 4: Explanation
    print("\n步驟 4: 風險說明 (Risk Explanation)")
    print("-" * 80)
    for line in explanation.split('\n'):
        if line.strip():
            print(f"  {line}")
    
    # Store results
    results.append({
        "account_id": features.account_id,
        "name": account['name'],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors_count": len(risk_factors)
    })

# Summary Report
print(f"\n\n{'=' * 80}")
print("總結報告 (SUMMARY REPORT)")
print("=" * 80)

print("\n風險分數分布 (Risk Score Distribution):")
print("-" * 80)
for result in sorted(results, key=lambda x: x['risk_score'], reverse=True):
    bar_length = int(result['risk_score'] / 2)
    bar = "█" * bar_length
    print(f"{result['account_id']}: {bar} {result['risk_score']:>3}/100 - {result['risk_level']}")

print("\n風險等級統計 (Risk Level Statistics):")
print("-" * 80)
risk_counts = {}
for result in results:
    level = result['risk_level'].split()[0]
    risk_counts[level] = risk_counts.get(level, 0) + 1

for level, count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {level}: {count} 個帳戶")

print("\n風險因子統計 (Risk Factor Statistics):")
print("-" * 80)
if results:
    total_factors = sum(r['risk_factors_count'] for r in results)
    avg_factors = total_factors / len(results)
    print(f"  總風險因子數: {total_factors}")
    print(f"  平均每帳戶: {avg_factors:.1f} 個風險因子")
else:
    print("  無數據")

print("\n" + "=" * 80)
print("✓ 端到端演示完成！(End-to-End Demo Complete!)")
print("=" * 80)
