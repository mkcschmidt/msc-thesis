import os
import sys
import pandas as pd
from datetime import datetime
import numpy as np

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import PROPOSALS_VOTES_PATH, TOKEN_METRICS_PATH, METRICS_PATH

# Read proposal votes and details files
votes_df = pd.read_csv(PROPOSALS_VOTES_PATH)
token_holders_df = pd.read_csv(TOKEN_METRICS_PATH)

print(f"Loaded votes file with {len(votes_df)} entries.")
print(f"Loaded unique token holders file with {len(token_holders_df)} entries.")

# Convert 'date' column to datetime in token_holders_df
token_holders_df['date'] = pd.to_datetime(token_holders_df['date'])

# Function to approximate unique holders at a specific date
def get_approx_unique_holders(date, token_id):
    date = pd.to_datetime(date)
    df = token_holders_df[token_holders_df['token_id'] == token_id]

    before = df[df['date'] <= date].sort_values('date').iloc[-1]
    after = df[df['date'] >= date].sort_values('date').iloc[0]

    if before['date'] == after['date']:
        return before['unique_holders']

    # Linear interpolation
    delta_days = (after['date'] - before['date']).days
    delta_holders = after['unique_holders'] - before['unique_holders']
    delta_date = (date - before['date']).days

    approx_holders = before['unique_holders'] + (delta_holders / delta_days) * delta_date
    return approx_holders

# Extract proposal ID from the nested dictionary in votes_df
votes_df['proposal_id'] = votes_df['proposal'].apply(lambda x: eval(x)['id'])

# Initialize a list to store results
results = []

# Get the unique proposal IDs from the votes DataFrame
unique_proposals = votes_df['proposal_id'].unique()

# Calculate voter turnout rate for each proposal
for proposal_id in unique_proposals:
    try:
        print(f"Processing proposal_id: {proposal_id}")
        proposal_votes = votes_df[votes_df['proposal_id'] == proposal_id]
        
        # Assuming 'end' and 'id' (token ID) can be retrieved similarly, adjust if necessary
        end_date = datetime.utcfromtimestamp(proposal_votes['created'].max()).strftime('%Y-%m-%d')
        token_id = proposal_votes['token_id'].iloc[0]
        
        unique_voters = proposal_votes['voter'].nunique()
        unique_token_holders = get_approx_unique_holders(end_date, token_id)
        
        voter_turnout_rate = unique_voters / unique_token_holders if unique_token_holders > 0 else 0
        
        results.append({
            'proposal_id': proposal_id,
            'end_date': end_date,
            'token_id': token_id,
            'unique_voters': unique_voters,
            'unique_token_holders': unique_token_holders,
            'voter_turnout_rate': voter_turnout_rate
        })
    except Exception as e:
        print(f"Error processing proposal_id {proposal_id}: {e}")
        continue

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Ensure the directory exists
os.makedirs(METRICS_PATH, exist_ok=True)

# Save the results to a CSV file
output_file = os.path.join(METRICS_PATH, "voter_turnout_rates.csv")
results_df.to_csv(output_file, index=False)

print(f"Saved voter turnout rates to {output_file}")
print(f"Total proposals analyzed: {len(results_df)}")