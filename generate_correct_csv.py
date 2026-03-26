<<<<<<< HEAD
import requests
import pandas as pd
import numpy as np

# Fetch training labels
print("Fetching training data...")
train_response = requests.get('https://aws-event-api.bitopro.com/train_label')
train_df = pd.DataFrame(train_response.json())
suspicious_rate = train_df['status'].mean()
print(f"Suspicious rate in training: {suspicious_rate*100:.2f}%")

# Your document user_ids (first 100 for testing)
doc_user_ids = [3,10,98,139,185,218,241,276,373,397,500,505,506,572,577,778,813,917,935,1097,
1303,1331,1333,1339,1364,1372,1400,1442,1568,1659,1663,1681,1718,1767,1827,1858,1980,1987,
2010,2028,2043,2057,2085,2182,2256,2306,2359,2439,2461,2650,2655,2681,2710,2715,2733,2786,
2846,2874,2879,2953,2973,2994,3054,3056,3082,3240,3265,3415,3456,3480,3502,3553,3565,3567,
3615,3617,3631,3730,3784,3808,3857,3895,3934,3942,4001,4045,4047,4199,4234,4282,4358,4543,
4574,4637,4650,4676,4683,4724,4764,4769,4798]

print(f"\\nFirst 20 user_ids from your document: {doc_user_ids[:20]}")
print(f"Total user_ids parsed: {len(doc_user_ids)}")
=======
import requests
import pandas as pd
import numpy as np

# Fetch training labels
print("Fetching training data...")
train_response = requests.get('https://aws-event-api.bitopro.com/train_label')
train_df = pd.DataFrame(train_response.json())
suspicious_rate = train_df['status'].mean()
print(f"Suspicious rate in training: {suspicious_rate*100:.2f}%")

# Your document user_ids (first 100 for testing)
doc_user_ids = [3,10,98,139,185,218,241,276,373,397,500,505,506,572,577,778,813,917,935,1097,
1303,1331,1333,1339,1364,1372,1400,1442,1568,1659,1663,1681,1718,1767,1827,1858,1980,1987,
2010,2028,2043,2057,2085,2182,2256,2306,2359,2439,2461,2650,2655,2681,2710,2715,2733,2786,
2846,2874,2879,2953,2973,2994,3054,3056,3082,3240,3265,3415,3456,3480,3502,3553,3565,3567,
3615,3617,3631,3730,3784,3808,3857,3895,3934,3942,4001,4045,4047,4199,4234,4282,4358,4543,
4574,4637,4650,4676,4683,4724,4764,4769,4798]

print(f"\\nFirst 20 user_ids from your document: {doc_user_ids[:20]}")
print(f"Total user_ids parsed: {len(doc_user_ids)}")
>>>>>>> 3ed03a3 (Initial commit)
