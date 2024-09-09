import os
import pandas as pd
from scripts.config import RAW_DATA_PATH, EXCHANGE_ADDRESSES_PATH, TOKEN_NAME_MAPPING

# Load the exchange addresses CSV
exchange_addresses_file = os.path.join(RAW_DATA_PATH, "exchange_addresses.csv")
exchange_addresses_df = pd.read_csv(exchange_addresses_file)

# Initialize a dictionary to count ignored addresses per token
ignored_addresses_count = {token: 0 for token in TOKEN_NAME_MAPPING.values()}

# Ensure all token IDs in the CSV are lowercased to match mapping
exchange_addresses_df['id'] = exchange_addresses_df['id'].str.lower()

# Count the number of ignored addresses for each token
for token_id, token_name in TOKEN_NAME_MAPPING.items():
    token_id_lower = token_id.lower()  # Match the CSV ID format
    count = exchange_addresses_df[exchange_addresses_df['id'] == token_id_lower].shape[0]
    ignored_addresses_count[token_name] = count

# Calculate the total number of ignored exchange addresses
total_ignored_addresses = exchange_addresses_df.shape[0]

# Print the results to the console
print("Ignored Exchange Addresses per Token:")
for token_name, count in ignored_addresses_count.items():
    print(f"{token_name}: {count} addresses ignored")

print(f"\nTotal number of exchange addresses ignored across all tokens: {total_ignored_addresses}")

# If you want to save this data to a CSV file:
output_file = os.path.join(RAW_DATA_PATH, "ignored_addresses_summary.csv")
summary_df = pd.DataFrame(list(ignored_addresses_count.items()), columns=['Token', 'Ignored Addresses'])
summary_df.to_csv(output_file, index=False)
print(f"\nSummary saved to {output_file}")