import os
import sys
import requests
import pandas as pd
import json
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import RAW_DATA_PATH, ACCESS_TOKENS, CONSOLIDATED_INDEX_PATH, START_DATE, END_DATE

# Configuration settings
OUTPUT_DIR = os.path.join(RAW_DATA_PATH, "token_holders/")
API_URL = "https://streaming.bitquery.io/graphql"
TIMER_DELAY = 10  # Delay in seconds between each API call
PAGE_SIZE = 25000  # Maximum number of token holders per request
RETRY_DELAY = 30  # Delay in seconds before retrying after an error
MAX_RETRIES = 5  # Maximum number of retries for API calls

# List of API tokens
api_keys = ACCESS_TOKENS
current_key_index = 0

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_keys[current_key_index]}'
}

def switch_api_key():
    global current_key_index, HEADERS
    current_key_index = (current_key_index + 1) % len(api_keys)
    HEADERS['Authorization'] = f'Bearer {api_keys[current_key_index]}'
    print(f"Switched to API key {current_key_index + 1}")

def fetch_token_holders(token_contract, date, offset=0):
    query = """
    query MyQuery($tokenContract: String!, $date: String!, $offset: Int!) {
      EVM(dataset: archive, network: eth) {
        TokenHolders(
          date: $date
          tokenSmartContract: $tokenContract
          limit: {count: 25000, offset: $offset}
          orderBy: {descending: Balance_Amount}
        ) {
          Holder {
            Address
          }
          Balance {
            Amount(minimum: Balance_Amount, selectWhere: {gt: "0.000000000000000000"})
          }
        }
      }
    }
    """
    variables = {
        "tokenContract": token_contract,
        "date": date,
        "offset": offset
    }
    payload = {
        "query": query,
        "variables": variables
    }
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
            
            holders = data.get('data', {}).get('EVM', {}).get('TokenHolders', [])
            return holders
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 402:  # Payment Required
                print(f"API key {current_key_index + 1} exhausted, switching to the next key.")
                switch_api_key()
                retries = 0  # Reset retries after switching keys
                offset = 0  # Reset offset after switching keys
            else:
                print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        
        retries += 1
        print(f"Retrying in {RETRY_DELAY} seconds... (Attempt {retries}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)
    
    return []

def save_to_csv(token_id, date, holders):
    date_str = date.strftime("%Y-%m-%d")
    date_dir = os.path.join(OUTPUT_DIR, date_str)
    os.makedirs(date_dir, exist_ok=True)
    
    file_path = os.path.join(date_dir, f"{token_id}.csv")
    
    df = pd.DataFrame(holders)
    df.to_csv(file_path, index=False)
    print(f"Saved token holders for {token_id} on {date_str} to {file_path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    consolidated_index_df = pd.read_csv(CONSOLIDATED_INDEX_PATH)
    print(f"Loaded consolidated index file with {len(consolidated_index_df)} entries.")
    
    # Define date ranges
    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(END_DATE, "%Y-%m-%d")
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += relativedelta(months=1)
    
    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
        print(f"\nProcessing date: {date_str}\n" + "="*50)
        
        for i, token in consolidated_index_df.iterrows():
            token_name = token['name']
            token_contract = token['address']
            token_id = token['id']
            
            if pd.isna(token_contract) or token_contract == '':
                print(f"Skipping {token_name} due to missing contract address.")
            else:
                all_holders = []
                offset = 0

                while True:
                    print(f"Fetching holders for {token_name} ({token_contract}) on {date_str} with offset {offset}")
                    holders = fetch_token_holders(token_contract, date_str, offset)
                    
                    if holders:
                        all_holders.extend(holders)
                        if len(holders) < PAGE_SIZE:
                            break
                        offset += PAGE_SIZE
                    else:
                        print(f"No more holders found for {token_name} on {date_str}")
                        break

                    time.sleep(TIMER_DELAY)  # Adding a delay between each API call

                if all_holders:
                    save_to_csv(token_id, date, all_holders)
                else:
                    print(f"No holders found for {token_name} on {date_str}")
        
        print(f"Completed processing for date: {date_str}")

if __name__ == "__main__":
    main()