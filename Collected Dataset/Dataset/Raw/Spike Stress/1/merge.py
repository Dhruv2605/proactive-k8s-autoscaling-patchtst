import pandas as pd
import glob
import os

# --- CONFIGURATION ---
# List your files here, or use glob to find all CSVs like "data_*.csv"
FILES_TO_MERGE = ['1.csv', '2.csv', '3.csv'] 
OUTPUT_FILENAME = "final_merged_dataset.csv"

def merge_csv_files(file_list, output_name):
    print(f"Reading {len(file_list)} files...")
    
    dataframes = []
    for file in file_list:
        try:
            # Read CSV
            df = pd.read_csv(file)
            dataframes.append(df)
            print(f" -> Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f" ⚠️ Error reading {file}: {e}")

    if not dataframes:
        print("No data loaded. Exiting.")
        return

    # 1. Concatenate all dataframes into one big messy table
    print("Concatenating...")
    full_df = pd.concat(dataframes, ignore_index=True)

    # 2. Fix Timestamps
    # Ensure timestamp is actually a datetime object so we can sort properly
    full_df['timestamp'] = pd.to_datetime(full_df['timestamp'])
    
    # 3. The "Max" Trick
    # This solves your issue where one file has "NaN" and another has "44.3"
    # Grouping by timestamp and taking .max() keeps the real number!
    print("Merging duplicates (keeping best values)...")
    merged_df = full_df.groupby('timestamp').max().reset_index()

    # 4. Sort chronologically
    merged_df = merged_df.sort_values('timestamp')

    # 5. Save
    merged_df.to_csv(output_name, index=False)
    print(f"✅ Success! Saved {len(merged_df)} rows to {output_name}")
    print(merged_df.head())

# --- RUN IT ---
if __name__ == "__main__":
    merge_csv_files(FILES_TO_MERGE, OUTPUT_FILENAME)