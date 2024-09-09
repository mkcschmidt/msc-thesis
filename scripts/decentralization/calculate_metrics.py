import os
import sys
import pandas as pd
import numpy as np

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import PROCESSED_DATA_PATH, METRICS_PATH

def calculate_gini_coefficient(amounts):
    n = len(amounts)
    sorted_amounts = np.sort(amounts)
    cumulative_sum = np.cumsum(sorted_amounts)
    sum_of_amounts = np.sum(amounts)
    index = np.arange(1, n + 1)
    gini_numerator = np.sum((2 * index - n - 1) * sorted_amounts)
    gini_denominator = n * sum_of_amounts
    gini_coefficient = gini_numerator / gini_denominator
    return gini_coefficient

def calculate_nakamoto_coefficient(amounts, total_supply):
    sorted_amounts = np.sort(amounts)[::-1]
    cumulative_amount = 0
    threshold = 0.5 * total_supply

    for i, amount in enumerate(sorted_amounts):
        cumulative_amount += amount
        if cumulative_amount > threshold:
            return i + 1
    return len(amounts)

def calculate_shannon_entropy(amounts):
    total_supply = np.sum(amounts)
    proportions = amounts / total_supply
    proportions = proportions[proportions > 0]  # Avoid log(0) issues
    entropy = -np.sum(proportions * np.log2(proportions))
    return entropy

def calculate_hhi(amounts):
    total_supply = np.sum(amounts)
    proportions = amounts / total_supply
    hhi = np.sum(proportions ** 2)
    return hhi

def calculate_theil_index(amounts):
    mean_amount = np.mean(amounts)
    proportions = amounts / mean_amount
    proportions = proportions[proportions > 0]  # Avoid log(0) issues
    theil_index = np.mean(proportions * np.log(proportions))
    return theil_index

def process_token_file(file_path):
    df = pd.read_csv(file_path)
    amounts = df['Amount'].values.astype(float)
    total_supply = np.sum(amounts)

    gini = calculate_gini_coefficient(amounts)
    nakamoto = calculate_nakamoto_coefficient(amounts, total_supply)
    shannon_entropy = calculate_shannon_entropy(amounts)
    hhi = calculate_hhi(amounts)
    theil_index = calculate_theil_index(amounts)
    unique_holders = len(df)

    return gini, nakamoto, shannon_entropy, hhi, theil_index, unique_holders

def main():
    os.makedirs(METRICS_PATH, exist_ok=True)
    metrics_filtered = []
    metrics_unfiltered = []

    for filter_type in ['filtered', 'unfiltered']:
        filter_path = os.path.join(PROCESSED_DATA_PATH, "token_holders", filter_type)
        date_folders = [f for f in os.listdir(filter_path) if os.path.isdir(os.path.join(filter_path, f))]
        
        for date_folder in date_folders:
            date_folder_path = os.path.join(filter_path, date_folder)
            files = [f for f in os.listdir(date_folder_path) if f.endswith('.csv')]
            
            print(f"\nProcessing {filter_type} data for {date_folder}: {len(files)} files found.")
            
            for i, filename in enumerate(files):
                token_id = filename.replace('.csv', '')
                file_path = os.path.join(date_folder_path, filename)
                
                try:
                    gini, nakamoto, shannon_entropy, hhi, theil_index, unique_holders = process_token_file(file_path)
                    metric_entry = {
                        'date': date_folder,
                        'token_id': token_id,
                        'gini_coefficient': gini,
                        'nakamoto_coefficient': nakamoto,
                        'shannon_entropy': shannon_entropy,
                        'hhi': hhi,
                        'theil_index': theil_index,
                        'unique_holders': unique_holders
                    }
                    
                    if filter_type == 'filtered':
                        metrics_filtered.append(metric_entry)
                    else:
                        metrics_unfiltered.append(metric_entry)
                    
                    if i % 10 == 0:
                        print(f"Processed {i + 1}/{len(files)} files for {date_folder}")
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    metrics_filtered_df = pd.DataFrame(metrics_filtered)
    metrics_unfiltered_df = pd.DataFrame(metrics_unfiltered)
    
    output_filtered_file = os.path.join(METRICS_PATH, "token_metrics_filtered.csv")
    output_unfiltered_file = os.path.join(METRICS_PATH, "token_metrics_unfiltered.csv")

    metrics_filtered_df.to_csv(output_filtered_file, index=False)
    metrics_unfiltered_df.to_csv(output_unfiltered_file, index=False)

    print(f"\nFiltered metrics saved to {output_filtered_file}")
    print(f"Unfiltered metrics saved to {output_unfiltered_file}")

if __name__ == "__main__":
    main()