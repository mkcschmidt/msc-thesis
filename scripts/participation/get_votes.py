import os
import sys
import requests
import pandas as pd
import time

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import PROPOSALS_PATH_CSV, PROPOSALS_VOTES_PATH

# Constants
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"
DELAY = 2  # Delay in seconds

# Read the proposal details file
proposals_details_file = PROPOSALS_PATH_CSV
proposals_df = pd.read_csv(proposals_details_file)
print(f"Loaded proposal details file with {len(proposals_df)} entries.")

# Query template for votes
query_template = """
{{
  votes (
    first: 1000
    skip: {skip}
    where: {{
      proposal: "{proposal_id}"
    }}
    orderBy: "created",
    orderDirection: desc
  ) {{
    id
    voter
    vp
    vp_by_strategy
    vp_state
    created
    proposal {{
      id
    }}
    choice
    space {{
      id
    }}
  }}
}}
"""

def fetch_votes(proposal_id, skip=0):
    query = query_template.format(proposal_id=proposal_id, skip=skip)
    response = requests.post(SNAPSHOT_API_URL, json={'query': query})
    
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code} for proposal: {proposal_id}")
        print("Response:", response.text)
        return None

    try:
        data = response.json()
        if 'data' in data and 'votes' in data['data']:
            return data['data']['votes']
        else:
            print(f"No votes found for proposal: {proposal_id}")
            print("Response:", data)
            return None
    except ValueError:
        print(f"Error decoding JSON response for proposal: {proposal_id}")
        print("Response:", response.text)
        return None

def main():
    all_votes = []

    for _, row in proposals_df.iterrows():
        proposal_id = row['proposal_id']
        token_id = row['id']  # Fetch the token_id (CoinGecko ID) from the row
        print(f"Fetching votes for proposal: {proposal_id}")
        
        skip = 0
        while True:
            votes = fetch_votes(proposal_id, skip=skip)
            if not votes:
                break
            
            # Add the CoinGecko ID to each vote
            for vote in votes:
                vote['token_id'] = token_id

            all_votes.extend(votes)
            skip += len(votes)
            time.sleep(DELAY)  # Add delay between each API call
            if len(votes) < 1000:
                break
        time.sleep(DELAY)  # Add delay between fetching votes for different proposals
    
    if not all_votes:
        print("No votes fetched. Please check the proposal IDs and API query.")
        return

    votes_df = pd.DataFrame(all_votes)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(PROPOSALS_VOTES_PATH), exist_ok=True)
    
    # Save the votes to the CSV file directly
    votes_df.to_csv(PROPOSALS_VOTES_PATH, index=False)
    
    print(f"Saved votes details to {PROPOSALS_VOTES_PATH}")
    print(f"Total votes fetched: {len(votes_df)}")

if __name__ == "__main__":
    main()