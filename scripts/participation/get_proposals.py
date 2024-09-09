import os
import sys
import requests
import pandas as pd

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import SPACES_CSV_PATH, PROPOSALS_PATH

# Constants
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"

# Read the spaces file
spaces_df = pd.read_csv(SPACES_CSV_PATH)
print(f"Loaded spaces file with {len(spaces_df)} entries.")

# Query template to fetch proposals
query_template = """
{{
  proposals(first: 100, skip: {skip}, where: {{space: "{space_id}"}}, orderBy: "created", orderDirection: desc) {{
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
    scores
    scores_total
    votes
  }}
}}
"""

def fetch_proposals(space_id):
    proposals = []
    skip = 0
    
    while True:
        query = query_template.format(space_id=space_id, skip=skip)
        response = requests.post(SNAPSHOT_API_URL, json={'query': query})
        
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code} for space: {space_id}")
            print("Response:", response.text)
            break

        try:
            data = response.json()
            if 'data' in data and 'proposals' in data['data']:
                new_proposals = data['data']['proposals']
                if not new_proposals:
                    break
                proposals.extend(new_proposals)
                skip += len(new_proposals)
            else:
                print(f"No proposals found for space: {space_id}")
                print("Response:", data)
                break
        except ValueError:
            print(f"Error decoding JSON response for space: {space_id}")
            print("Response:", response.text)
            break

    return proposals

def main():
    all_proposals = []
    
    for _, row in spaces_df.iterrows():
        space_id = row['space_id']
        token_id = row['id']
        if pd.notna(space_id):  # Only process if space_id is not NaN
            print(f"Fetching proposals for space: {space_id}")
            proposals = fetch_proposals(space_id)
            print(f"Found {len(proposals)} proposals for space: {space_id}")
            
            for proposal in proposals:
                proposal_data = {
                    'id': token_id,
                    'space_id': space_id,
                    'proposal_id': proposal['id'],
                    'title': proposal['title'],
                    'start': proposal['start'],
                    'end': proposal['end'],
                    'state': proposal['state'],
                    'author': proposal['author'],
                    'space_name': proposal['space']['name'],
                    'scores': proposal['scores'],
                    'scores_total': proposal['scores_total'],
                    'votes': proposal['votes']
                }
                all_proposals.append(proposal_data)
    
    proposals_df = pd.DataFrame(all_proposals)
    
    # Ensure the directory exists
    os.makedirs(PROPOSALS_PATH, exist_ok=True)
    
    output_file = os.path.join(PROPOSALS_PATH, "proposals.csv")
    proposals_df.to_csv(output_file, index=False)
    
    print(f"Saved all proposals to {output_file}")

if __name__ == "__main__":
    main()