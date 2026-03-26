<<<<<<< HEAD
#!/usr/bin/env python3
"""
Reorder the CSV file to match document order (sorted by user_id)
"""
import pandas as pd

print("Reading current CSV file...")
df = pd.read_csv('your_team_name.csv')

print(f"Current order (first 20):")
print(df.head(20)['user_id'].tolist())

print("\nSorting by user_id...")
df_sorted = df.sort_values('user_id').reset_index(drop=True)

print(f"\nNew order (first 20):")
print(df_sorted.head(20)['user_id'].tolist())

# Save the sorted version
output_file = 'your_team_name_sorted.csv'
df_sorted.to_csv(output_file, index=False)

print(f"\n✓ Sorted CSV saved to: {output_file}")
print(f"Total records: {len(df_sorted)}")
print(f"\nFirst 20 user_ids in sorted file:")
for i, row in df_sorted.head(20).iterrows():
    print(f"  {row['user_id']},{row['status']}")
=======
#!/usr/bin/env python3
"""
Reorder the CSV file to match document order (sorted by user_id)
"""
import pandas as pd

print("Reading current CSV file...")
df = pd.read_csv('your_team_name.csv')

print(f"Current order (first 20):")
print(df.head(20)['user_id'].tolist())

print("\nSorting by user_id...")
df_sorted = df.sort_values('user_id').reset_index(drop=True)

print(f"\nNew order (first 20):")
print(df_sorted.head(20)['user_id'].tolist())

# Save the sorted version
output_file = 'your_team_name_sorted.csv'
df_sorted.to_csv(output_file, index=False)

print(f"\n✓ Sorted CSV saved to: {output_file}")
print(f"Total records: {len(df_sorted)}")
print(f"\nFirst 20 user_ids in sorted file:")
for i, row in df_sorted.head(20).iterrows():
    print(f"  {row['user_id']},{row['status']}")
>>>>>>> 3ed03a3 (Initial commit)
