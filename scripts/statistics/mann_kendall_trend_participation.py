import os
import pandas as pd
from pymannkendall import original_test  # Import Mann-Kendall test function
from scripts.config import PARTICIPATION_RATES_CSV, VOTER_TURNOUT_CSV, TOKEN_NAME_MAPPING, STATISTICS_PATH

def unify_token_names(df, column_name):
    """Function to unify token names for both participation and voter turnout data."""
    df[column_name] = df[column_name].replace({
        'yearn.finance': 'Yearn Finance',
        'yearn-finance': 'Yearn Finance'
    })
    return df

def mann_kendall_trend_test_participation():
    print("Running Mann-Kendall Trend Test for participation metrics...")

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
                         how='inner')  # Use inner join to keep only matched rows
    print(f"Merged data contains {len(merged_df)} rows.")
    print("Sample of merged data:")
    print(merged_df.head())  # Debugging: print a sample of merged data

    # Check for the tokens present in the merged data
    tokens = merged_df['name'].unique()
    print(f"Tokens found in the merged data: {tokens}")

    results = []
    for token in tokens:
        print(f"\nProcessing token: {token}...")

        # Filter data for the current token
        token_data = merged_df[merged_df['name'] == token].sort_values('date')
        print(f"Number of entries for {token}: {len(token_data)}")

        if len(token_data) < 10:
            # Skip tokens with insufficient data for trend analysis
            print(f"Not enough data for Mann-Kendall trend analysis for token: {token} (only {len(token_data)} entries).")
            continue

        # Mann-Kendall test for participation rates
        print(f"Calculating Mann-Kendall trend test for participation rates for {token}...")
        participation_rate_values = token_data['participation_rate'].dropna().values
        if len(set(participation_rate_values)) < 2:
            print(f"Insufficient variation in participation rates for {token}. Skipping Mann-Kendall test.")
            continue  # Skip if there is not enough variation for trend analysis

        participation_trend = original_test(participation_rate_values)
        print(f"Participation rate trend for {token}: trend statistic = {participation_trend.Tau}, p-value = {participation_trend.p}")

        # Mann-Kendall test for voter turnout rates
        print(f"Calculating Mann-Kendall trend test for voter turnout rates for {token}...")
        voter_turnout_values = token_data['voter_turnout_rate'].dropna().values
        if len(set(voter_turnout_values)) < 2:
            print(f"Insufficient variation in voter turnout rates for {token}. Skipping Mann-Kendall test.")
            continue  # Skip if there is not enough variation for trend analysis

        turnout_trend = original_test(voter_turnout_values)
        print(f"Voter turnout rate trend for {token}: trend statistic = {turnout_trend.Tau}, p-value = {turnout_trend.p}")

        # Store the results
        results.append({
            'token': token,
            'participation_trend_stat': participation_trend.Tau,
            'participation_p_value': participation_trend.p,
            'turnout_trend_stat': turnout_trend.Tau,
            'turnout_p_value': turnout_trend.p
        })

    # Convert the results to DataFrame
    results_df = pd.DataFrame(results)
    output_path = os.path.join(STATISTICS_PATH, 'mann_kendall_trend_results_participation.csv')
    results_df.to_csv(output_path, index=False)
    print(f"Mann-Kendall trend test results saved to {output_path}")

# Main execution function
def main():
    # Ensure the STATISTICS_PATH exists
    if not os.path.exists(STATISTICS_PATH):
        os.makedirs(STATISTICS_PATH)

    # Run Mann-Kendall trend test
    mann_kendall_trend_test_participation()

if __name__ == "__main__":
    main()