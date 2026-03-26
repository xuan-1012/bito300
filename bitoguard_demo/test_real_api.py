"""
測試真實 BitoPro API 整合
"""
import requests
import pandas as pd

def test_api_connection():
    """測試 API 連線"""
    print("=" * 60)
    print("測試 BitoPro API 連線")
    print("=" * 60)
    
    endpoints = [
        'usdt_twd_trading',
        'crypto_transfer',
        'user_info',
        'twd_transfer',
        'usdt_swap',
        'train_label'
    ]
    
    for endpoint in endpoints:
        try:
            url = f'https://aws-event-api.bitopro.com/{endpoint}?limit=10'
            print(f"\n測試 {endpoint}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                print(f"  ✓ 成功 - 獲取 {len(df)} 筆資料")
                if len(df) > 0:
                    print(f"  欄位: {', '.join(df.columns.tolist()[:5])}...")
            else:
                print(f"  ✗ 失敗 - HTTP {response.status_code}")
        except Exception as e:
            print(f"  ✗ 錯誤: {str(e)}")
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api_connection()
