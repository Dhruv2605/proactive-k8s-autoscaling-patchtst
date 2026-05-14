import pandas as pd
import os

input_file = "final_sockshop_dataset_clean.csv"
output_file = "final_sockshop_dataset_final.csv"

if os.path.exists(input_file):
    df = pd.read_csv(input_file)
    # Removing any leading/trailing whitespace and literal single/double quotes from column names
    df.columns = [c.strip().replace("'", "").replace('"', '') for c in df.columns]
    df.to_csv(output_file, index=False)
    print(f"Successfully cleaned headers. New columns: {df.columns.tolist()}")
else:
    print(f"Error: {input_file} not found.")
