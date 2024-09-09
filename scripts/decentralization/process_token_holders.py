import os
import sys
import pandas as pd
import json

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, EXCHANGE_ADDRESSES_PATH

def load_exchange_addresses():
    exchange_addresses = pd.read_csv(EXCHANGE_ADDRESSES_PATH)
    exchange_dict = {}
    for i, row in exchange_addresses.iterrows():
        token_id = row['id']
        address = row['address']
        if token_id not in exchange_dict:
            exchange_dict[token_id] = set()
        exchange_dict[token_id].add(address)
    return exchange_dict

def process_token_data(token_id, exchange_addresses, date, token_file, filter_exchanges):
    input_file_path = os.path.join(RAW_DATA_PATH, "token_holders", date, token_file)
    output_dir = os.path.join(PROCESSED_DATA_PATH, "token_holders", "filtered" if filter_exchanges else "unfiltered", date)
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = pd.read_csv(input_file_path)
        # Normalize JSON-like columns and extract Address and Amount
        df['Address'] = df['Holder'].apply(lambda x: json.loads(x.replace("'", '"'))['Address'])
        df['Amount'] = df['Balance'].apply(lambda x: json.loads(x.replace("'", '"'))['Amount']).astype(float)
        
        if filter_exchanges:
            df = df[~df['Address'].isin(exchange_addresses.get(token_id, set()))]
        
        # Select only the Address and Amount columns for output
        df_cleaned = df[['Address', 'Amount']]
        
        output_file_path = os.path.join(output_dir, token_id + '.csv')
        df_cleaned.to_csv(output_file_path, index=False)
        print(f"Processed and saved file: {output_file_path}")
    except Exception as e:
        print(f"Error processing file {input_file_path}: {e}")

def main():
    exchange_addresses = load_exchange_addresses()
    
    for date_folder in os.listdir(os.path.join(RAW_DATA_PATH, "token_holders")):
        date_folder_path = os.path.join(RAW_DATA_PATH, "token_holders", date_folder)
        if os.path.isdir(date_folder_path):
            print(f"Processing date folder: {date_folder}")
            for filename in os.listdir(date_folder_path):
                if filename.endswith('.csv'):
                    token_id = filename.replace('.csv', '')
                    try:
                        # Process with filtering
                        process_token_data(token_id, exchange_addresses, date_folder, filename, filter_exchanges=True)
                        # Process without filtering
                        process_token_data(token_id, exchange_addresses, date_folder, filename, filter_exchanges=False)
                    except Exception as e:
                        print(f"Error processing file {date_folder_path}/{filename}: {e}")

if __name__ == "__main__":
    main()