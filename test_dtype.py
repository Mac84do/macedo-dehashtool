#!/usr/bin/env python3
import pandas as pd

# Create a simple test DataFrame
data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
df = pd.DataFrame(data)

print("Testing DataFrame column dtype access...")
for column in df.columns:
    try:
        data_type = str(df[column].dtype)
        print(f"Column {column}: {data_type}")
    except Exception as e:
        print(f"Error accessing dtype for column {column}: {e}")
        
print("Test completed.")
