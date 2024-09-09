import os
import sys
import pandas as pd

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import INDEX_DATA_PATH, CONSOLIDATED_INDEX_PATH

# Configuration settings
OUTPUT_FILE = CONSOLIDATED_INDEX_PATH

def consolidate_index_constituents():
    # Initialize an empty DataFrame to hold the consolidated data
    consolidated_df = pd.DataFrame()
    
    # Iterate over the CSV files in the index data directory
    for filename in os.listdir(INDEX_DATA_PATH):
        file_path = os.path.join(INDEX_DATA_PATH, filename)
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            consolidated_df = pd.concat([consolidated_df, df])
    
    # Remove duplicates
    consolidated_df.drop_duplicates(subset=['id'], keep='first', inplace=True)
    
    # Sort by market cap for better readability
    consolidated_df.sort_values(by='market_cap', ascending=False, inplace=True)
    
    # Save the consolidated data to a new CSV file
    consolidated_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Consolidated index constituents saved to {OUTPUT_FILE}")

def main():
    consolidate_index_constituents()

if __name__ == "__main__":
    main()