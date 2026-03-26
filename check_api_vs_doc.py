<<<<<<< HEAD
import requests

# Get API data
api_data = requests.get('https://aws-event-api.bitopro.com/predict_label').json()
api_user_ids = [x['user_id'] for x in api_data]

print(f"API predict_label count: {len(api_user_ids)}")
print(f"First 20 from API: {api_user_ids[:20]}")
print(f"\nChecking specific user_ids:")
print(f"  user_id 3 in API: {3 in api_user_ids}")
print(f"  user_id 10 in API: {10 in api_user_ids}")
print(f"  user_id 967903 in API: {967903 in api_user_ids}")
=======
import requests

# Get API data
api_data = requests.get('https://aws-event-api.bitopro.com/predict_label').json()
api_user_ids = [x['user_id'] for x in api_data]

print(f"API predict_label count: {len(api_user_ids)}")
print(f"First 20 from API: {api_user_ids[:20]}")
print(f"\nChecking specific user_ids:")
print(f"  user_id 3 in API: {3 in api_user_ids}")
print(f"  user_id 10 in API: {10 in api_user_ids}")
print(f"  user_id 967903 in API: {967903 in api_user_ids}")
>>>>>>> 3ed03a3 (Initial commit)
