import os
import sys
import requests
import pandas as pd
import time

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import PROPOSALS_PATH

# Constants
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"
DELAY = 2  # Delay in seconds

# Read the proposals file
proposals_file = os.path.join(PROPOSALS_PATH, "proposals.csv")
proposals_df = pd.read_csv(proposals_file)
print(f"Loaded proposals file with {len(proposals_df)} entries.")

# Query template for detailed proposal information
query_template = """
{{
  proposal(id: "{proposal_id}") {{
    id
    title
    start
    end
    state
    author
    space {{
      id
      name
    }}
    choices
    scores
    scores_total
    votes
  }}
}}
"""

def fetch_proposal_details(proposal_id):
    query = query_template.format(proposal_id=proposal_id)
    response = requests.post(SNAPSHOT_API_URL, json={'query': query})
    
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code} for proposal: {proposal_id}")
        print("Response:", response.text)
        return None

    try:
        data = response.json()
        if 'data' in data and 'proposal' in data['data']:
            return data['data']['proposal']
        else:
            print(f"No details found for proposal: {proposal_id}")
            print("Response:", data)
            return None
    except ValueError:
        print(f"Error decoding JSON response for proposal: {proposal_id}")
        print("Response:", response.text)
        return None

def main():
    detailed_proposals = []
    
    for _, row in proposals_df.iterrows():
        proposal_id = row['proposal_id']
        token_id = row['id']  # Fetch the token_id from the row
        print(f"Fetching details for proposal: {proposal_id}")
        proposal_details = fetch_proposal_details(proposal_id)
        
        if proposal_details:
            # Add the token_id to the proposal details
            proposal_details['token_id'] = token_id
            detailed_proposals.append(proposal_details)
        
        # Delay to avoid hitting the API rate limit
        time.sleep(DELAY)
    
    details_df = pd.DataFrame(detailed_proposals)
    
    # Ensure the directory exists
    os.makedirs(PROPOSALS_PATH, exist_ok=True)
    
    output_file = os.path.join(PROPOSALS_PATH, "proposal_details.csv")
    details_df.to_csv(output_file, index=False)
    
    print(f"Saved detailed proposals to {output_file}")
    print(f"Total proposals fetched: {len(detailed_proposals)}")

if __name__ == "__main__":
    main()