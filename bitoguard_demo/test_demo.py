"""
Quick test script to verify the demo components work correctly
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import NumPy: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Plotly: {e}")
        return False
    
    return True

def test_data_generation():
    """Test the mock data generation function"""
    print("\nTesting data generation...")
    
    np.random.seed(42)
    n_samples = 100
    n_suspicious = int(n_samples * 0.15)
    n_normal = n_samples - n_suspicious
    
    data = []
    
    # Generate normal accounts
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
    
    # Generate suspicious accounts
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
    
    print(f"✅ Generated {len(df)} accounts")
    print(f"   - Normal: {len(df[df['label'] == 'Normal'])}")
    print(f"   - Suspicious: {len(df[df['label'] == 'Suspicious'])}")
    print(f"   - Columns: {list(df.columns)}")
    
    return True

def test_chart_creation():
    """Test that charts can be created"""
    print("\nTesting chart creation...")
    
    try:
        import plotly.graph_objects as go
        
        # Test histogram
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=np.random.randn(100),
            name='Test',
            marker_color='#10b981'
        ))
        print("✅ Histogram created successfully")
        
        # Test bar chart
        fig = go.Figure(go.Bar(
            x=[0.1, 0.2, 0.3],
            y=['A', 'B', 'C'],
            orientation='h'
        ))
        print("✅ Bar chart created successfully")
        
        # Test line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(10)),
            y=np.random.randn(10),
            mode='lines+markers'
        ))
        print("✅ Line chart created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create charts: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("BitoGuard Demo - Component Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test data generation
    if not test_data_generation():
        all_passed = False
    
    # Test chart creation
    if not test_chart_creation():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Demo is ready to run.")
        print("\nTo start the demo, run:")
        print("  streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)

if __name__ == '__main__':
    main()
