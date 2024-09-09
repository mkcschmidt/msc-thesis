import os
import pandas as pd
from pymannkendall import original_test  # Import Mann-Kendall test function
from scripts.config import TOKEN_METRICS_PATH, TOKEN_NAME_MAPPING, STATISTICS_PATH

def mann_kendall_trend_test():
    print("Running Mann-Kendall Trend Test for all decentralization metrics...")

    # Load the decentralization metrics data (Gini, HHI, etc.)
    decentralization_df = pd.read_csv(TOKEN_METRICS_PATH)
    decentralization_df['date'] = pd.to_datetime(decentralization_df['date'])
    print(f"Decentralization data loaded with {len(decentralization_df)} entries.")

    # Map token IDs to proper names using TOKEN_NAME_MAPPING
    decentralization_df['name'] = decentralization_df['token_id'].map(TOKEN_NAME_MAPPING)

    # Check if there are any tokens not found in the mapping
    if decentralization_df['name'].isnull().any():
        missing_tokens = decentralization_df[decentralization_df['name'].isnull()]['token_id'].unique()
        print(f"Warning: Some token_ids are missing in the TOKEN_NAME_MAPPING: {missing_tokens}")

    # Check for the tokens
    tokens = decentralization_df['name'].unique()
    print(f"Tokens found in the data: {tokens}")

    # List of decentralization metrics to test
    metrics = ['gini_coefficient', 'hhi', 'theil_index', 'shannon_entropy', 'unique_holders', 'nakamoto_coefficient']

    results = []
    for token in tokens:
        print(f"\nProcessing token: {token}...")

        # Filter data for the current token
        token_data = decentralization_df[decentralization_df['name'] == token].sort_values('date')

        if len(token_data) < 2:
            # Skip tokens with insufficient data for trend analysis
            print(f"Not enough data for Mann-Kendall trend analysis for token: {token} (only {len(token_data)} entries).")
            continue

        # Calculate Mann-Kendall trend for each decentralization metric
        token_results = {'token': token}
        for metric in metrics:
            print(f"Calculating Mann-Kendall trend test for {metric} for {len(token_data)} entries.")
            metric_values = token_data[metric].values
            
            # Perform Mann-Kendall test
            trend_result = original_test(metric_values)
            token_results[f'{metric}_trend_stat'] = trend_result.Tau
            token_results[f'{metric}_p_value'] = trend_result.p
            print(f"{metric.capitalize()} trend for {token}: trend statistic = {trend_result.Tau}, p-value = {trend_result.p}")

        results.append(token_results)

    # Convert the results to DataFrame
    results_df = pd.DataFrame(results)
    output_path = os.path.join(STATISTICS_PATH, 'mann_kendall_trend_results.csv')
    results_df.to_csv(output_path, index=False)
    print(f"Mann-Kendall trend test results saved to {output_path}")

# Main execution function
def main():
    # Ensure the STATISTICS_PATH exists
    if not os.path.exists(STATISTICS_PATH):
        os.makedirs(STATISTICS_PATH)

    # Run Mann-Kendall trend test
    mann_kendall_trend_test()

if __name__ == "__main__":
    main()