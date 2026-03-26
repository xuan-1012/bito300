import requests

endpoints = [
    'usdt_twd_trading',
    'crypto_transfer', 
    'user_info',
    'twd_transfer',
    'usdt_swap'
]

print("Testing all behavior data endpoints...")
print("=" * 60)

for ep in endpoints:
    try:
        r = requests.get(f'https://aws-event-api.bitopro.com/{ep}', timeout=10)
        data = r.json()
        print(f'✓ {ep}: {len(data)} records')
        if len(data) > 0:
            print(f'  Sample keys: {list(data[0].keys())}')
    except Exception as e:
        print(f'✗ {ep}: {e}')
    print()
