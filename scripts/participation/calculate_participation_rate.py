import os
import sys
import pandas as pd
import requests
from datetime import datetime
from tqdm import tqdm

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import PROPOSALS_PATH, METRICS_PATH, COMBINED_TOKENS_PATH, COINGECKO_API_KEY

# Function to fetch market data from CoinGecko
def fetch_market_data(token_id, days='max'):
    url = f'https://pro-api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days={days}&interval=daily'
    headers = {
        'accept': 'application/json',
        'x-cg-pro-api-key': COINGECKO_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to fetch historical market data for a specific date from CoinGecko
def fetch_historical_market_data(token_id, date):
    formatted_date = date.strftime('%d-%m-%Y')
    url = f'https://pro-api.coingecko.com/api/v3/coins/{token_id}/history?date={formatted_date}&localization=false'
    headers = {
        'accept': 'application/json',
        'x-cg-pro-api-key': COINGECKO_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Load proposal data
proposals_file = os.path.join(PROPOSALS_PATH, "proposals.csv")
proposals_df = pd.read_csv(proposals_file)
proposals_df['end'] = pd.to_datetime(proposals_df['end'], unit='s')

# Load combined tokens data
combined_tokens_file = os.path.join(COMBINED_TOKENS_PATH)
tokens_df = pd.read_csv(combined_tokens_file)

# Merge proposals data with token names
proposals_df = proposals_df.merge(tokens_df[['id', 'name']], on='id', how='left')

# Extract unique token IDs
unique_tokens = proposals_df['id'].unique()

# Fetch and store market data for each token
market_data = {}
for token_id in tqdm(unique_tokens, desc="Fetching market data for tokens"):
    market_data[token_id] = fetch_market_data(token_id, 'max')

# Prepare a DataFrame to store the results
results = []

# Calculate participation rate for each proposal
missing_proposals = []
for _, row in proposals_df.iterrows():
    token_id = row['id']
    proposal_id = row['proposal_id']
    end_date = row['end'].date()
    token_name = row['name']
    votes = row['votes']
    
    closest_date = None
    closest_market_cap = None
    closest_price = None
    
    if token_id in market_data and market_data[token_id]:
        prices = market_data[token_id].get('prices', [])
        market_caps = market_data[token_id].get('market_caps', [])
        
        for price_data in prices:
            price_date = datetime.utcfromtimestamp(price_data[0] / 1000).date()
            if price_date == end_date:
                closest_date = price_date
                closest_price = price_data[1]
                break
        for market_cap_data in market_caps:
            market_cap_date = datetime.utcfromtimestamp(market_cap_data[0] / 1000).date()
            if market_cap_date == end_date:
                closest_market_cap = market_cap_data[1]
                break
        
    # If market data is missing, fetch historical data for the specific date
    if not closest_price or not closest_market_cap:
        historical_data = fetch_historical_market_data(token_id, end_date)
        if historical_data and 'market_data' in historical_data:
            market_data_entry = historical_data['market_data']
            closest_price = market_data_entry['current_price'].get('usd', None)
            closest_market_cap = market_data_entry['market_cap'].get('usd', None)
    
    # Calculate circulating supply if market cap and price are available
    if closest_market_cap and closest_price:
        circulating_supply = closest_market_cap / closest_price
        participation_rate = row['scores_total'] / circulating_supply
        
        results.append({
            'id': token_id,
            'name': token_name,
            'proposal_id': proposal_id,
            'date': end_date,
            'price': closest_price,
            'market_cap': closest_market_cap,
            'circulating_supply': circulating_supply,
            'votes': votes,
            'participation_rate': participation_rate
        })
    else:
        missing_proposals.append((proposal_id, end_date))

# Retry fetching missing proposals using historical data
still_missing_proposals = []
for proposal_id, end_date in tqdm(missing_proposals, desc="Fetching missing proposals with historical data"):
    token_id = proposals_df[proposals_df['proposal_id'] == proposal_id]['id'].values[0]
    token_name = proposals_df[proposals_df['proposal_id'] == proposal_id]['name'].values[0]
    votes = proposals_df[proposals_df['proposal_id'] == proposal_id]['votes'].values[0]

    historical_data = fetch_historical_market_data(token_id, end_date)
    if historical_data and 'market_data' in historical_data:
        market_data_entry = historical_data['market_data']
        closest_price = market_data_entry['current_price'].get('usd', None)
        closest_market_cap = market_data_entry['market_cap'].get('usd', None)
        
        if closest_market_cap and closest_price:
            circulating_supply = closest_market_cap / closest_price
            participation_rate = proposals_df[proposals_df['proposal_id'] == proposal_id]['scores_total'].values[0] / circulating_supply
            
            results.append({
                'id': token_id,
                'name': token_name,
                'proposal_id': proposal_id,
                'date': end_date,
                'price': closest_price,
                'market_cap': closest_market_cap,
                'circulating_supply': circulating_supply,
                'votes': votes,
                'participation_rate': participation_rate
            })
        else:
            still_missing_proposals.append((proposal_id, end_date))

# Convert results to DataFrame
output_df = pd.DataFrame(results)

# Ensure the directory exists
os.makedirs(METRICS_PATH, exist_ok=True)

# Write the resulting DataFrame to a CSV file
output_file = os.path.join(METRICS_PATH, "participation_rates.csv")
output_df.to_csv(output_file, index=False)

# Print statistics
total_proposals = len(proposals_df)
successful_proposals = len(output_df)
print(f"Total proposals: {total_proposals}")
print(f"Successful proposals with market data: {successful_proposals}")
print(f"Missing proposals after retry: {len(still_missing_proposals)}")