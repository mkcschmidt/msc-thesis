import os
import pandas as pd
from scipy.stats import spearmanr
from scripts.config import PARTICIPATION_RATES_CSV, VOTER_TURNOUT_CSV, TOKEN_NAME_MAPPING, STATISTICS_PATH

def unify_token_names(df, column_name):
    """Function to unify token names for both participation and voter turnout data."""
    df[column_name] = df[column_name].replace({
        'yearn.finance': 'Yearn Finance',
        'yearn-finance': 'Yearn Finance'
    })
    return df

def spearman_correlation():
    print("Running Spearman's Rank Correlation Coefficient...")

    # Load Participation Rates
    print(f"Loading participation rates from {PARTICIPATION_RATES_CSV}...")
    participation_df = pd.read_csv(PARTICIPATION_RATES_CSV)
    participation_df['date'] = pd.to_datetime(participation_df['date'])
    print(f"Participation data loaded with {len(participation_df)} entries.")
    print("Sample of participation data:")
    print(participation_df.head())  # Debugging: print a sample of participation data

    # Load Voter Turnout Rates
    print(f"Loading voter turnout rates from {VOTER_TURNOUT_CSV}...")
    voter_turnout_df = pd.read_csv(VOTER_TURNOUT_CSV)
    voter_turnout_df['end_date'] = pd.to_datetime(voter_turnout_df['end_date'])
    print(f"Voter turnout data loaded with {len(voter_turnout_df)} entries.")
    print("Sample of voter turnout data:")
    print(voter_turnout_df.head())  # Debugging: print a sample of voter turnout data

    # Unify token names in both dataframes
    print("Unifying token names...")
    participation_df = unify_token_names(participation_df, 'name')
    voter_turnout_df = unify_token_names(voter_turnout_df, 'token_id')

    # Map lowercase token_ids in voter_turnout_df to the proper case names using TOKEN_NAME_MAPPING
    voter_turnout_df['name'] = voter_turnout_df['token_id'].replace(TOKEN_NAME_MAPPING)
    print("Token name mapping applied to voter turnout data.")

    # Check if there are any tokens not found in the mapping
    if voter_turnout_df['name'].isnull().any():
        missing_tokens = voter_turnout_df[voter_turnout_df['name'].isnull()]['token_id'].unique()
        print(f"Warning: Some token_ids are missing in the TOKEN_NAME_MAPPING: {missing_tokens}")

    # Merge on proposal_id and name to align data
    print("Merging participation rates and voter turnout rates on 'proposal_id' and 'name'...")
    merged_df = pd.merge(participation_df, voter_turnout_df, 
                         left_on=['proposal_id', 'name'], 
                         right_on=['proposal_id', 'name'], 
                         how='inner')
    print(f"Merged data contains {len(merged_df)} rows.")
    print("Sample of merged data:")
    print(merged_df.head())  # Debugging: print a sample of merged data

    # Check for the tokens present in the merged data
    tokens = merged_df['name'].unique()
    print(f"Tokens found in the merged data: {tokens}")

    results = []
    for token in tokens:
        print(f"\nProcessing token: {token}...")
        token_data = merged_df[merged_df['name'] == token]

        if len(token_data) < 10:
            # Skip tokens with insufficient data for correlation
            print(f"Not enough data for Spearman correlation for token: {token} (only {len(token_data)} entries).")
            continue

        print(f"Calculating Spearman correlation for {len(token_data)} entries.")
        # Extract the participation rates and voter turnout rates
        participation_rate = token_data['participation_rate']
        voter_turnout_rate = token_data['voter_turnout_rate']

        # Calculate Spearman's correlation
        corr, p_value = spearmanr(participation_rate, voter_turnout_rate)
        print(f"Spearman correlation for {token}: correlation = {corr}, p-value = {p_value}")

        results.append({
            'token': token,
            'spearman_corr': corr,
            'p_value': p_value
        })

    # Convert the results to DataFrame
    results_df = pd.DataFrame(results)
    output_path = os.path.join(STATISTICS_PATH, 'spearman_correlation_results.csv')
    results_df.to_csv(output_path, index=False)
    print(f"Spearman's correlation results saved to {output_path}")

# Main execution function
def main():
    # Ensure the METRICS_PATH exists
    if not os.path.exists(STATISTICS_PATH):
        os.makedirs(STATISTICS_PATH)

    # Run Spearman correlation
    spearman_correlation()

if __name__ == "__main__":
    main()