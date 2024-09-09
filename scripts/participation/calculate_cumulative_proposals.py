import os
import sys
import pandas as pd

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import PROPOSALS_PATH, METRICS_PATH, COMBINED_TOKENS_PATH

# Load proposals data
proposals_file = os.path.join(PROPOSALS_PATH, "proposals.csv")
proposals_df = pd.read_csv(proposals_file)
print(f"Loaded proposals file with {len(proposals_df)} entries.")

# Convert the 'end' column to datetime and extract the date
proposals_df['end'] = pd.to_datetime(proposals_df['end'], unit='s')
proposals_df['end_date'] = proposals_df['end'].dt.date

# Load combined tokens data
combined_tokens_file = os.path.join(COMBINED_TOKENS_PATH)
tokens_df = pd.read_csv(combined_tokens_file)
print(f"Loaded combined tokens file with {len(tokens_df)} entries.")

# Merge proposals data with token names
proposals_df = proposals_df.merge(tokens_df[['id', 'name']], on='id', how='left')

# Group by id, name, and end_date to count proposals per day
daily_counts = proposals_df.groupby(['id', 'name', 'end_date']).size().reset_index(name='daily_count')

# Calculate the cumulative sum of proposals for each id
daily_counts['cumulative_proposals'] = daily_counts.groupby('id')['daily_count'].cumsum()

# Print the first and last proposal date for each token
token_ids = daily_counts['id'].unique()
for token_id in token_ids:
    token_proposals = daily_counts[daily_counts['id'] == token_id]
    first_proposal_date = token_proposals['end_date'].min()
    last_proposal_date = token_proposals['end_date'].max()
    token_name = token_proposals['name'].iloc[0]
    print(f"Token: {token_name} ({token_id}), First Proposal Date: {first_proposal_date}, Last Proposal Date: {last_proposal_date}")

# Ensure the metrics directory exists
os.makedirs(METRICS_PATH, exist_ok=True)

# Select and rename columns for the output
daily_counts = daily_counts[['id', 'name', 'end_date', 'cumulative_proposals']]
daily_counts.columns = ['id', 'name', 'date', 'cumulative_proposals']

# Save the metrics to a new CSV file
output_file = os.path.join(METRICS_PATH, "cumulative_proposals.csv")
daily_counts.to_csv(output_file, index=False)

print(f"Saved cumulative proposal metrics to {output_file}")